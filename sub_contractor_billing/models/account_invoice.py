# -*- coding: utf-8 -*-
""" This Module For Account Invoice """
from odoo import models, fields, api


class AccountInvoice(models.Model):
    """ account.invoice Model """
    _inherit = 'account.move'

    job_type_id = fields.Many2one(comodel_name='job.type')
    project_name_id = fields.Many2one(comodel_name='project.project')
    project_no = fields.Char(related='project_name_id.project_no', readonly=True)
    project_start_date = fields.Date(related='project_name_id.project_start_date', readonly=True)
    project_end_date = fields.Date(related='project_name_id.project_end_date', readonly=True)
    project_period = fields.Float(related='project_name_id.project_period', readonly=True)
    sub_contractor = fields.Char(string="Sub Contractor Invoice")
    previous_invoice_id = fields.Many2one('account.move', string="Previous Invoice")
    period_from = fields.Date()
    period_to = fields.Date()
    account_move_no = fields.Char(string="", required=False)
    final_invoice = fields.Boolean(string='Final Invoice')

    @api.model
    def create(self, vals):
        if vals.get('contract_project_id') and not vals.get('project_name_id'):
            vals['project_name_id'] = vals.get('contract_project_id')
        if vals.get('contract_id'):
            prev_invoice_number = []
            prev_invoice = self.env['account.move']
            move_no = 0
            if vals.get('contract_type') == 'contractor':
                move_no = self.env['account.move'].search_count([('contract_id', '=', vals.get('contract_id')), ('move_type', '=', 'out_invoice'), 
                    ('is_contract_invoice', '=', True), ('contract_project_id', '=', vals.get('contract_project_id'))])
            if vals.get('contract_type') == 'subcontractor':
                move_no = self.env['account.move'].search_count([('contract_id', '=', vals.get('contract_id')), ('move_type', '=', 'in_invoice'), 
                    ('is_contract_invoice', '=', True), ('contract_project_id', '=', vals.get('contract_project_id'))])
            vals['sub_contractor'] = move_no + 1 if move_no else 1
            # for rec in self.env['account.move'].search([('contract_id', '=', vals.get('contract_id')), ('move_type', '=', 'out_invoice'), 
            #     ('is_contract_invoice', '=', True), ('contract_project_id', '=', vals.get('contract_project_id'))]).mapped('account_move_no'):
            #     if rec != False:
            #         prev_invoice_number.append(int(rec))
            # vals['sub_contractor'] = max(prev_invoice_number) + 1 if prev_invoice_number else 1
            for rec in self.env['account.move'].search([('contract_id', '=', vals.get('contract_id'))],limit=1):
                if rec != False:
                    prev_invoice = rec
            vals['previous_invoice_id'] = prev_invoice and prev_invoice.id
        res = super(AccountInvoice, self).create(vals)
        res.set_sub_contractor()
        prev_invoice_num = []
        for rec in self.env['account.move'].search([]).mapped('account_move_no'):
            if rec != False:
                prev_invoice_num.append(int(rec))
        res.account_move_no = max(prev_invoice_num) + 1 if prev_invoice_num else 1
        return res

    @api.onchange('contract_project_id')
    def onchange_contract_project_id(self):
        if self.contract_project_id:
            self.project_name_id = self.contract_project_id

    def unlink(self):
        self.with_context(from_unlink=True).set_sub_contractor()
        return super(AccountInvoice, self).unlink()

    def get_related_order(self):
        """
        Set the invoice sequence related to sale order or purchase order.
        :return: None
        """
        so_obj = self.env['sale.order']
        po_obj = self.env['purchase.order']
        order_obj = po_obj if self.move_type == 'in_invoice' else so_obj
        return order_obj.search([('invoice_ids', '=', self.id)], limit=1)  # in  >>>  =

    def set_sub_contractor(self):
        """
        Set the invoice sequence related to sale order or purchase order.
        :return: None
        """
        for rec in self:
            order = rec.get_related_order()
            invoices = order.invoice_ids if not \
                self._context.get('from_unlink') else order.invoice_ids - rec
            previous = False
            for i, inv in enumerate(invoices.sorted(key=lambda p: p.id)):
                inv.sub_contractor = '%s' % (i + 1)
                inv.previous_invoice_id = previous
                previous = inv.id


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"




    @api.onchange('move_id', 'product_id', 'previous_qty', 'current_qty2', 'actual_quant')
    def calculate_previous_qty(self):
        for rec in self:
            previous_qty = 0.0
            if rec.move_id.contract_id and rec.move_id.contract_type == 'contractor':
                previous_invoices = self.env['account.move'].search(
                [('contract_id', '=', rec.move_id.contract_id.id), ('move_type', '=', 'out_invoice'),
                 ('is_contract_invoice', '=', True), ('contract_type', '=', rec.move_id.contract_type), 
                 ('contract_project_id', '=', rec.move_id.contract_project_id.id),  ('state', '!=', 'cancel'),
                 ('id', '!=', self.move_id._origin.id), ('id', '<', self.move_id._origin.id)])
                for prev in previous_invoices:
                    previous_qty += sum(
                        line.current_qty2 for line in prev.invoice_line_ids
                        if line.product_id == rec.product_id)
                rec.previous_qty = previous_qty
                rec.total_contract_qty = sum(line.quantity
                                             for line in rec.move_id.contract_id.contract_line_ids
                                             if line.product_id == rec.product_id)
            elif rec.move_id.contract_id and rec.move_id.contract_type == 'subcontractor':
                if rec.actual_quant:
                    previous_invoices = self.env['account.move'].search(
                    [('contract_id', '=', rec.move_id.contract_id.id), ('move_type', '=', 'in_invoice'),
                     ('is_contract_invoice', '=', True), ('contract_type', '=', rec.move_id.contract_type), 
                     ('contract_project_id', '=', rec.move_id.contract_project_id.id),  ('state', '!=', 'cancel'),
                     ('id', '!=', self.move_id._origin.id), ('id', '<', self.move_id._origin.id)])
                    for prev in previous_invoices:
                        previous_qty += sum(
                            line.current_qty2 for line in prev.invoice_line_ids
                            if line.product_id == rec.product_id and line.work_plan_item_id == rec.work_plan_item_id)
                    rec.previous_qty = previous_qty
                    rec.total_contract_qty = sum(line.quantity for line in rec.move_id.contract_id.contract_line_ids if line.product_id == rec.product_id)
            else:
                rec.previous_qty = previous_qty

    def calculate_tender_qty_amount(self):
        for rec in self:
            rec.tender_qty = 0.0
            rec.tender_amount = 0.0
            rec.tender_qty = sum(line.quantity for line in rec.move_id.contract_id.contract_line_ids
                                         if line.product_id == rec.product_id)
            rec.tender_amount = sum(line.price_subtotal for line in rec.move_id.contract_id.contract_line_ids
                                         if line.product_id == rec.product_id)

    

    @api.onchange('actual_quant', 'previous_qty')
    @api.depends('actual_quant', 'previous_qty')
    def calculate_current_qty(self):
        for line in self:
            if line.previous_qty:
                line.current_qty2 = line.actual_quant - line.previous_qty
            else:
                line.current_qty2 = line.actual_quant
            


    @api.onchange('current_qty2')
    def get_original_quantity(self):
        for item in self:
            item.quantity = item.current_qty2
                
    @api.depends('previous_qty', 'current_qty2')
    def calculate_total_qty(self):
        for rec in self:
            if rec.move_id.contract_type == 'contractor':
                rec.total_qty = rec.total_qty
                if rec.current_qty2 != 0 or rec.previous_qty != 0:
                    rec.total_qty = rec.previous_qty + rec.current_qty2
            else:
                rec.total_qty = rec.total_qty
                for line in rec.move_id.contract_id.contract_line_ids:
                    if rec.product_id == line.product_id and rec.name == line.work_plan_item_id.name:
                        rec.total_qty = line.total_work_plan_qty
                    else:
                        rec.total_qty = rec.total_qty

    

    previous_qty = fields.Float(string="Previous QTY", compute='calculate_previous_qty', store=True)
    total_contract_qty = fields.Float(string='Total Contract QTY')
    current_qty2 = fields.Float(string='Current Qty', compute='calculate_current_qty')
    actual_quant = fields.Float(string='Actual Quantity', store=True)
    tender_qty = fields.Float(string='Tender Qty', compute='calculate_tender_qty_amount')
    tender_amount = fields.Float(string='Tender Amount', compute='calculate_tender_qty_amount')
    total_qty = fields.Float(string="Total QTY ",compute='calculate_total_qty', store=True)

    # @api.depends('total_qty')
    # def calculate_total_amount(self):
    #     for rec in self:
    #         # need to check if it is calculated on total qty or in current qty without previous
    #         rec.total_amount = rec.current_qty2 * rec.price_unit2
    #         rec.price_subtotal = rec.total_amount


    total_amount = fields.Float(string='Total Amount')
    completed_percentage = fields.Char('% Completed')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        res.update({'price_unit2': self.price_unit, 'current_qty2': self.qty_to_invoice})
        return res

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = {
            'ref': order.client_order_ref,
            'move_type': 'out_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,
            'fiscal_position_id': (order.fiscal_position_id or order.fiscal_position_id.get_fiscal_position(order.partner_id.id)).id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_reference': order.reference,
            'invoice_payment_term_id': order.payment_term_id.id,
            'partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
            'team_id': order.team_id.id,
            'campaign_id': order.campaign_id.id,
            'medium_id': order.medium_id.id,
            'source_id': order.source_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'price_unit2': amount,
                'quantity': 1.0,
                'current_qty2': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,
                'tax_ids': [(6, 0, so_line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }
        return invoice_vals