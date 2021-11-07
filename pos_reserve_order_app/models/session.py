# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, \
    DEFAULT_SERVER_DATETIME_FORMAT
from odoo.http import request
from collections import defaultdict


class PosPayment(models.Model):
    _inherit = 'pos.payment'

    actual_session_id = fields.Many2one('pos.session', string='Session',
                                        compute='get_session_id', store=True)

    @api.depends('pos_order_id')
    def get_session_id(self):
        for rec in self:
            if rec.session_id and rec.pos_order_id.is_reserved and rec.actual_session_id:
                rec.actual_session_id = rec.actual_session_id.id
            else:
                rec.actual_session_id = rec.pos_order_id.session_id and \
                                        rec.pos_order_id.session_id.id or False


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    total_payments_amount_display = fields.Float(
        compute='_compute_total_payments_amount_display',
        string='Total Payments Amount')

    @api.depends('order_ids.payment_ids.amount')
    def _compute_total_payments_amount_display(self):
        for session in self:
            session.total_payments_amount_display = sum(
                session.order_ids.mapped('payment_ids').filtered(
                    lambda x: x.actual_session_id.id == session.id).mapped(
                    'amount'))

    def action_show_payments_list(self):
        return {
            'name': _('Payments'),
            'type': 'ir.actions.act_window',
            'res_model': 'pos.payment',
            'view_mode': 'tree,form',
            'domain': [('actual_session_id', '=', self.id)],
            'context': {'search_default_group_by_payment_method': 1}
        }

    @api.model
    def create(self, vals):
        res = super(PosSessionInherit, self).create(vals)
        orders = self.env['pos.order'].search([
            ('state', '=', 'reserved'), ('user_id', '=', request.env.uid)])
        orders.write({'session_id': res.id})
        orders.mapped('payment_ids').get_session_id()
        return res

    def _accumulate_amounts(self, data):
        # Accumulate the amounts for each accounting lines group
        # Each dict maps `key` -> `amounts`, where `key` is the group key.
        # E.g. `combine_receivables` is derived from pos.payment records
        # in the self.order_ids with group key of the `payment_method_id`
        # field of the pos.payment record.
        amounts = lambda: {'amount': 0.0, 'amount_converted': 0.0}
        tax_amounts = lambda: {'amount': 0.0, 'amount_converted': 0.0,
                               'base_amount': 0.0, 'base_amount_converted': 0.0}
        split_receivables = defaultdict(amounts)
        split_receivables_cash = defaultdict(amounts)
        combine_receivables = defaultdict(amounts)
        combine_receivables_cash = defaultdict(amounts)
        invoice_receivables = defaultdict(amounts)
        sales = defaultdict(amounts)
        taxes = defaultdict(tax_amounts)
        stock_expense = defaultdict(amounts)
        stock_output = defaultdict(amounts)
        # Track the receivable lines of the invoiced orders' account moves for reconciliation
        # These receivable lines are reconciled to the corresponding invoice receivable lines
        # of this session's move_id.
        order_account_move_receivable_lines = defaultdict(
            lambda: self.env['account.move.line'])
        rounded_globally = self.company_id.tax_calculation_rounding_method == 'round_globally'
        for order in self.order_ids:
            # if order.state != 'reserved':
            # Combine pos receivable lines
            # Separate cash payments for cash reconciliation later.
            for payment in order.payment_ids.filtered(lambda x:
                                                      x.actual_session_id.id == self.id):
                amount, date = payment.amount, payment.payment_date
                if payment.payment_method_id.split_transactions:
                    if payment.payment_method_id.is_cash_count:
                        split_receivables_cash[payment] = self._update_amounts(
                            split_receivables_cash[payment], {'amount': amount},
                            date)
                    else:
                        split_receivables[payment] = self._update_amounts(
                            split_receivables[payment], {'amount': amount},
                            date)
                else:
                    key = payment.payment_method_id
                    if payment.payment_method_id.is_cash_count:
                        combine_receivables_cash[key] = self._update_amounts(
                            combine_receivables_cash[key], {'amount': amount},
                            date)
                    else:
                        combine_receivables[key] = self._update_amounts(
                            combine_receivables[key], {'amount': amount}, date)
            if order.is_invoiced:
                # Combine invoice receivable lines
                key = order.partner_id.property_account_receivable_id.id
                invoice_receivables[key] = self._update_amounts(
                    invoice_receivables[key],
                    {'amount': order._get_amount_receivable()},
                    order.date_order)
                # side loop to gather receivable lines by account for reconciliation
                for move_line in order.account_move.line_ids.filtered(lambda
                                                                              aml: aml.account_id.internal_type == 'receivable' and not aml.reconciled):
                    order_account_move_receivable_lines[
                        move_line.account_id.id] |= move_line
            else:
                order_taxes = defaultdict(tax_amounts)
                for order_line in order.lines:
                    line = self._prepare_line(order_line)
                    # Combine sales/refund lines
                    sale_key = (
                        # account
                        line['income_account_id'],
                        # sign
                        -1 if line['amount'] < 0 else 1,
                        # for taxes
                        tuple((tax['id'], tax['account_id'],
                               tax['tax_repartition_line_id']) for tax in
                              line['taxes']),
                    )
                    sales[sale_key] = self._update_amounts(
                        sales[sale_key], {
                            'amount': sum(
                                p.amount for p in
                                order.payment_ids.filtered(
                                    lambda x: x.actual_session_id.id ==
                                              self.id))},
                        order.date_order)
                    # Combine tax lines
                    for tax in line['taxes']:
                        tax_key = (
                            tax['account_id'], tax['tax_repartition_line_id'],
                            tax['id'], tuple(tax['tag_ids']))
                        order_taxes[tax_key] = self._update_amounts(
                            order_taxes[tax_key],
                            {'amount': tax['amount'],
                             'base_amount': tax['base']},
                            tax['date_order'],
                            round=not rounded_globally
                        )
                for tax_key, amounts in order_taxes.items():
                    if rounded_globally:
                        amounts = self._round_amounts(amounts)
                    for amount_key, amount in amounts.items():
                        taxes[tax_key][amount_key] += amount

                if self.company_id.anglo_saxon_accounting and order.picking_id.id:
                    # Combine stock lines
                    stock_moves = self.env['stock.move'].search([
                        ('picking_id', '=', order.picking_id.id),
                        ('company_id.anglo_saxon_accounting', '=', True),
                        ('product_id.categ_id.property_valuation', '=',
                         'real_time')
                    ])
                    for move in stock_moves:
                        exp_key = move.product_id.property_account_expense_id or move.product_id.categ_id.property_account_expense_categ_id
                        out_key = move.product_id.categ_id.property_stock_account_output_categ_id
                        amount = -sum(
                            move.stock_valuation_layer_ids.mapped('value'))
                        stock_expense[exp_key] = self._update_amounts(
                            stock_expense[exp_key], {'amount': amount},
                            move.picking_id.date, force_company_currency=True)
                        stock_output[out_key] = self._update_amounts(
                            stock_output[out_key], {'amount': amount},
                            move.picking_id.date, force_company_currency=True)

                # Increasing current partner's customer_rank
                order.partner_id._increase_rank('customer_rank')

        MoveLine = self.env['account.move.line'].with_context(
            check_move_validity=False)

        data.update({
            'taxes': taxes,
            'sales': sales,
            'stock_expense': stock_expense,
            'split_receivables': split_receivables,
            'combine_receivables': combine_receivables,
            'split_receivables_cash': split_receivables_cash,
            'combine_receivables_cash': combine_receivables_cash,
            'invoice_receivables': invoice_receivables,
            'stock_output': stock_output,
            'order_account_move_receivable_lines': order_account_move_receivable_lines,
            'MoveLine': MoveLine
        })
        return data

    def _confirm_orders(self):
        for session in self:
            company_id = session.config_id.journal_id.company_id.id
            orders = session.order_ids.filtered(
                lambda order: order.state == 'paid')
            journal_id = self.env['ir.config_parameter'].sudo().get_param(
                'pos.closing.journal_id_%s' % company_id,
                default=session.config_id.journal_id.id)
            if not journal_id:
                raise UserError(
                    _("You have to set a Sale Journal for the POS:%s") % (
                        session.config_id.name,))

            move = self.env['pos.order'].with_context(
                force_company=company_id)._create_account_move(session.start_at,
                                                               session.name,
                                                               int(journal_id),
                                                               company_id)
            orders.with_context(
                force_company=company_id)._create_account_move_line(session,
                                                                    move)

            for order in session.order_ids.filtered(
                    lambda o: o.state not in ['done', 'invoiced']):
                if order.state in ('paid'):
                    order.action_pos_order_done()

            orders_to_reconcile = session.order_ids._filtered_for_reconciliation()
            orders_to_reconcile.sudo()._reconcile_payments()

    def _reconcile_account_move_lines(self, data):
        # reconcile cash receivable lines
        split_cash_statement_lines = data.get('split_cash_statement_lines')
        combine_cash_statement_lines = data.get('combine_cash_statement_lines')
        split_cash_receivable_lines = data.get('split_cash_receivable_lines')
        combine_cash_receivable_lines = data.get(
            'combine_cash_receivable_lines')
        order_account_move_receivable_lines = data.get(
            'order_account_move_receivable_lines')
        invoice_receivable_lines = data.get('invoice_receivable_lines')
        stock_output_lines = data.get('stock_output_lines')

        for statement in self.statement_ids:
            if not self.config_id.cash_control:
                statement.write({'balance_end_real': statement.balance_end})
            statement.button_confirm_bank()
            all_lines = (split_cash_statement_lines[statement].mapped(
                'journal_entry_ids').filtered(
                lambda aml: aml.account_id.internal_type == 'receivable')
                         | combine_cash_statement_lines[statement].mapped(
                        'journal_entry_ids').filtered(
                        lambda
                            aml: aml.account_id.internal_type == 'receivable')
                         | split_cash_receivable_lines[statement]
                         | combine_cash_receivable_lines[statement]
                         )
            accounts = all_lines.mapped('account_id')
            lines_by_account = [
                all_lines.filtered(lambda l: l.account_id == account) for
                account in accounts]
            for lines in lines_by_account:
                lines.reconcile()
        # reconcile invoice receivable lines
        for account_id in order_account_move_receivable_lines:
            (order_account_move_receivable_lines[account_id]
             | invoice_receivable_lines.get(account_id,
                                            self.env['account.move.line'])
             ).reconcile()

        # reconcile stock output lines
        stock_moves = self.env['stock.move'].search([
            ('picking_id', 'in', self.order_ids.filtered(
                lambda order: not order.is_invoiced).mapped('picking_id').ids)
        ])
        stock_account_move_lines = self.env['account.move'].search(
            [('stock_move_id', 'in', stock_moves.ids)]).mapped('line_ids')
        for account_id in stock_output_lines:
            (stock_output_lines[account_id].filtered(
                lambda aml: not aml.reconciled)
             | stock_account_move_lines.filtered(
                        lambda
                            aml: not aml.reconciled and aml.account_id == account_id)).reconcile()
        return data
