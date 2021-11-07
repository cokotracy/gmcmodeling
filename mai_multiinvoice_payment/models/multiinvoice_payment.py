from odoo import _, api, fields, models
from odoo.exceptions import UserError

class AccountPaymentInvoices(models.Model):
    _name = 'account.payment.invoice'

    invoice_id = fields.Many2one('account.move', string='Invoice')
    payment_id = fields.Many2one('account.payment', string='Payment')
    currency_id = fields.Many2one(related='invoice_id.currency_id')
    origin = fields.Char(related='invoice_id.invoice_origin')
    date_invoice = fields.Date(related='invoice_id.invoice_date')
    date_due = fields.Date(related='invoice_id.invoice_date_due')
    payment_state = fields.Selection(related='payment_id.state', store=True)
    reconcile_amount = fields.Monetary(string='Reconcile Amount')
    amount_total = fields.Monetary(related="invoice_id.amount_total")
    residual = fields.Monetary(related="invoice_id.amount_residual")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invoice_id = fields.Many2one('account.move', string='Invoice')

    def _check_reconcile_validity(self):
        #Perform all checks on lines
        company_ids = set()
        all_accounts = []
        for line in self:
            company_ids.add(line.company_id.id)
            all_accounts.append(line.account_id)
            if (line.matched_debit_ids or line.matched_credit_ids) and line.reconciled:
                pass
                # raise UserError(_('You are trying to reconcile some entries that are already reconciled.'))
        if len(company_ids) > 1:
            raise UserError(_('To reconcile the entries company should be the same for all entries.'))
        if len(set(all_accounts)) > 1:
            raise UserError(_('Entries are not from the same account.'))
        if not (all_accounts[0].reconcile or all_accounts[0].internal_type == 'liquidity'):
            raise UserError(_('Account %s (%s) does not allow reconciliation. First change the configuration of this account to allow it.') % (all_accounts[0].name, all_accounts[0].code))


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_invoice_ids = fields.One2many('account.payment.invoice', 'payment_id',string="Customer Invoices")

    @api.onchange('payment_type', 'partner_type', 'partner_id', 'currency_id')
    def _onchange_to_get_vendor_invoices(self):
        if self.payment_type in ['inbound', 'outbound'] and self.partner_type and self.partner_id and self.currency_id:
            self.payment_invoice_ids = [(6, 0, [])]
            if self.payment_type == 'inbound' and self.partner_type == 'customer':
                invoice_type = 'out_invoice'
            elif self.payment_type == 'outbound' and self.partner_type == 'customer':
                invoice_type = 'out_refund'
            elif self.payment_type == 'outbound' and self.partner_type == 'supplier':
                invoice_type = 'in_invoice'
            else:
                invoice_type = 'in_refund'
            invoice_recs = self.env['account.move'].search([('partner_id', 'child_of', self.partner_id.id), ('state', '=', 'posted'), ('move_type', '=', invoice_type), ('payment_state', '!=', 'paid'), ('currency_id', '=', self.currency_id.id)])
            payment_invoice_values = []
            for invoice_rec in invoice_recs:
                payment_invoice_values.append([0, 0, {'invoice_id': invoice_rec.id}])
            self.payment_invoice_ids = payment_invoice_values

    def post(self):
        AccountMove = self.env['account.move'].with_context(default_type='entry')
        for rec in self:
            if rec.payment_method_code == 'received_third_check':
                rec.create_check('third_check', 'holding', rec.check_bank_id)
            elif rec.payment_method_code == 'issue_check':
                check = rec.create_check('issue_check', 'handed', rec.check_bank_id)
                checkbooks_sequence = self.env['checkbook.sequence'].search([('name', '=', check.number)])
                checkbooks_sequence.write({'state': 'issued'})
            if rec.payment_invoice_ids:
                if rec.amount < sum(rec.payment_invoice_ids.mapped('reconcile_amount')):
                    raise UserError(_("The sum of the reconcile amount of listed invoices are greater than payment's amount."))

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'posted' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            if not rec.name:
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=rec.payment_date)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

            moves = AccountMove.create(rec._prepare_payment_moves())
            moves.filtered(lambda move: move.journal_id.post_at != 'bank_rec').post()

            move_name = self._get_move_name_transfer_separator().join(moves.mapped('name'))
            rec.write({'state': 'posted', 'move_name': move_name})

            if rec.payment_invoice_ids:
                AML_obj = self.env['account.move.line']
                if rec.payment_type in ('inbound', 'outbound'):
                    for line_id in rec.payment_invoice_ids:
                        lines = AML_obj.search([('invoice_id', '=', line_id.invoice_id.id)])
                        if lines:
                            lines += line_id.invoice_id.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                            lines.reconcile()
            else:
                if rec.payment_type in ('inbound', 'outbound'):
                    if rec.invoice_ids:
                        (moves[0] + rec.invoice_ids).line_ids \
                            .filtered(lambda line: not line.reconciled and line.account_id == rec.destination_account_id)\
                            .reconcile()
                elif rec.payment_type == 'transfer':
                    moves.mapped('line_ids')\
                        .filtered(lambda line: line.account_id == rec.company_id.transfer_account_id)\
                        .reconcile()

        return True


    def _prepare_payment_moves(self):

        all_move_vals = []
        for payment in self:
            payment_total_amount = payment.amount
            company_currency = payment.company_id.currency_id
            move_names = payment.move_name.split(payment._get_move_name_transfer_separator()) if payment.move_name else None

            write_off_amount = payment.payment_difference_handling == 'reconcile' and -payment.payment_difference or 0.0
            if payment.payment_type in ('outbound', 'transfer'):
                counterpart_amount = payment.amount
                if payment.payment_method_code == 'issue_check':
                    liquidity_line_account = payment.journal_id.deferred_check_account_id
                else:
                    liquidity_line_account = payment.journal_id.default_debit_account_id
                # liquidity_line_account = payment.journal_id.default_debit_account_id
            else:
                counterpart_amount = -payment.amount
                if payment.payment_method_code == 'received_third_check':
                    liquidity_line_account = payment.journal_id.holding_check_account_id
                else:
                    liquidity_line_account = payment.journal_id.default_credit_account_id

            if payment.currency_id == company_currency:
                balance = counterpart_amount
                write_off_balance = write_off_amount
                counterpart_amount = write_off_amount = 0.0
                currency_id = False
            else:
                balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id, payment.payment_date)
                write_off_balance = payment.currency_id._convert(write_off_amount, company_currency, payment.company_id, payment.payment_date)
                currency_id = payment.currency_id.id

            if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
                if payment.journal_id.currency_id == company_currency:
                    liquidity_line_currency_id = False
                else:
                    liquidity_line_currency_id = payment.journal_id.currency_id.id
                liquidity_amount = company_currency._convert(
                    balance, payment.journal_id.currency_id, payment.company_id, payment.payment_date)
            else:
                liquidity_line_currency_id = currency_id
                liquidity_amount = counterpart_amount

            rec_pay_line_name = ''
            if payment.payment_type == 'transfer':
                rec_pay_line_name = payment.name
            else:
                if payment.partner_type == 'customer':
                    if payment.payment_type == 'inbound':
                        rec_pay_line_name += _("Customer Payment")
                    elif payment.payment_type == 'outbound':
                        rec_pay_line_name += _("Customer Credit Note")
                elif payment.partner_type == 'supplier':
                    if payment.payment_type == 'inbound':
                        rec_pay_line_name += _("Vendor Credit Note")
                    elif payment.payment_type == 'outbound':
                        rec_pay_line_name += _("Vendor Payment")
                if payment.invoice_ids:
                    rec_pay_line_name += ': %s' % ', '.join(payment.invoice_ids.mapped('name'))

            if payment.payment_type == 'transfer':
                liquidity_line_name = _('Transfer to %s') % payment.destination_journal_id.name
            else:
                liquidity_line_name = payment.name

            if not payment.payment_invoice_ids:
                move_vals = {
                    'date': payment.payment_date,
                    'ref': payment.communication,
                    'journal_id': payment.journal_id.id,
                    'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
                    'partner_id': payment.partner_id.id,
                    'line_ids': [
                        (0, 0, {
                            'name': rec_pay_line_name,
                            'amount_currency': counterpart_amount + write_off_amount if currency_id else 0.0,
                            'currency_id': currency_id,
                            'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                            'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': payment.destination_account_id.id,
                            'payment_id': payment.id,
                        }),
                        (0, 0, {
                            'name': liquidity_line_name,
                            'amount_currency': -liquidity_amount if liquidity_line_currency_id else 0.0,
                            'currency_id': liquidity_line_currency_id,
                            'debit': balance < 0.0 and -balance or 0.0,
                            'credit': balance > 0.0 and balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': liquidity_line_account.id,
                            'payment_id': payment.id,
                        }),
                    ],
                }

                if write_off_balance:
                    move_vals['line_ids'].append((0, 0, {
                        'name': payment.writeoff_label,
                        'amount_currency': -write_off_amount,
                        'currency_id': currency_id,
                        'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                        'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                        'date_maturity': payment.payment_date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': payment.writeoff_account_id.id,
                        'payment_id': payment.id,
                    }))

                if move_names:
                    move_vals['name'] = move_names[0]

                all_move_vals.append(move_vals)

                if payment.payment_type == 'transfer':
                    journal = payment.destination_journal_id

                    if journal.currency_id and payment.currency_id != journal.currency_id:
                        liquidity_line_currency_id = journal.currency_id.id
                        transfer_amount = company_currency._convert(balance, journal.currency_id, payment.company_id, payment.payment_date)
                    else:
                        liquidity_line_currency_id = currency_id
                        transfer_amount = counterpart_amount

                    transfer_move_vals = {
                        'date': payment.payment_date,
                        'ref': payment.communication,
                        'partner_id': payment.partner_id.id,
                        'journal_id': payment.destination_journal_id.id,
                        'line_ids': [
                            (0, 0, {
                                'name': payment.name,
                                'amount_currency': -counterpart_amount if currency_id else 0.0,
                                'currency_id': currency_id,
                                'debit': balance < 0.0 and -balance or 0.0,
                                'credit': balance > 0.0 and balance or 0.0,
                                'date_maturity': payment.payment_date,
                                'partner_id': payment.partner_id.commercial_partner_id.id,
                                'account_id': payment.company_id.transfer_account_id.id,
                                'payment_id': payment.id,
                            }),
                            (0, 0, {
                                'name': _('Transfer from %s') % payment.journal_id.name,
                                'amount_currency': transfer_amount if liquidity_line_currency_id else 0.0,
                                'currency_id': liquidity_line_currency_id,
                                'debit': balance > 0.0 and balance or 0.0,
                                'credit': balance < 0.0 and -balance or 0.0,
                                'date_maturity': payment.payment_date,
                                'partner_id': payment.partner_id.commercial_partner_id.id,
                                'account_id': payment.destination_journal_id.default_credit_account_id.id,
                                'payment_id': payment.id,
                            }),
                        ],
                    }

                    if move_names and len(move_names) == 2:
                        transfer_move_vals['name'] = move_names[1]

                    all_move_vals.append(transfer_move_vals)
            else:
                check_use_amount = 0.0
                transfer_move_vals_extra = {
                    'date': payment.payment_date,
                    'ref': payment.communication,
                    'partner_id': payment.partner_id.id,
                    'journal_id': payment.journal_id.id,
                    'line_ids': [
                        (0, 0, {
                            'name': payment.name,
                            'amount_currency': -counterpart_amount if currency_id else 0.0,
                            'currency_id': currency_id,
                            'debit':  balance < 0.0 and -balance or 0.0,
                            'credit': balance > 0.0 and balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': liquidity_line_account.id,
                            'payment_id': payment.id,
                        }),
                    ],
                }

                for line in payment.payment_invoice_ids:
                    if not line.reconcile_amount:
                        continue
                    check_use_amount += line.reconcile_amount
                    company_currency = payment.company_id.currency_id
                    move_names = payment.move_name.split(payment._get_move_name_transfer_separator()) if payment.move_name else None

                    write_off_amount = payment.payment_difference_handling == 'reconcile' and -payment.payment_difference or 0.0
                    if payment.payment_type in ('outbound', 'transfer'):
                        counterpart_amount = line.reconcile_amount
                        # liquidity_line_account = payment.journal_id.default_debit_account_id
                        if payment.payment_method_code == 'issue_check':
                            liquidity_line_account = payment.journal_id.deferred_check_account_id
                        else:
                            liquidity_line_account = payment.journal_id.default_debit_account_id
                    else:
                        counterpart_amount = -line.reconcile_amount
                        # liquidity_line_account = payment.journal_id.default_credit_account_id
                        if payment.payment_method_code == 'received_third_check':
                            liquidity_line_account = payment.journal_id.holding_check_account_id
                        else:
                            liquidity_line_account = payment.journal_id.default_credit_account_id


                    if payment.currency_id == company_currency:
                        balance = counterpart_amount
                        write_off_balance = write_off_amount
                        counterpart_amount = write_off_amount = 0.0
                        currency_id = False
                    else:
                        balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id, payment.payment_date)
                        write_off_balance = payment.currency_id._convert(write_off_amount, company_currency, payment.company_id, payment.payment_date)
                        currency_id = payment.currency_id.id

                    if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
                        if payment.journal_id.currency_id == company_currency:
                            liquidity_line_currency_id = False
                        else:
                            liquidity_line_currency_id = payment.journal_id.currency_id.id
                        liquidity_amount = company_currency._convert(
                            balance, payment.journal_id.currency_id, payment.company_id, payment.payment_date)
                    else:
                        liquidity_line_currency_id = currency_id
                        liquidity_amount = counterpart_amount

                    rec_pay_line_name = ''
                    if payment.payment_type == 'transfer':
                        rec_pay_line_name = payment.name
                    else:
                        if payment.partner_type == 'customer':
                            if payment.payment_type == 'inbound':
                                rec_pay_line_name += _("Customer Payment")
                            elif payment.payment_type == 'outbound':
                                rec_pay_line_name += _("Customer Credit Note")
                        elif payment.partner_type == 'supplier':
                            if payment.payment_type == 'inbound':
                                rec_pay_line_name += _("Vendor Credit Note")
                            elif payment.payment_type == 'outbound':
                                rec_pay_line_name += _("Vendor Payment")
                        if payment.invoice_ids:
                            rec_pay_line_name += ': %s' % ', '.join(payment.invoice_ids.mapped('name'))

                    if payment.payment_type == 'transfer':
                        liquidity_line_name = _('Transfer to %s') % payment.destination_journal_id.name
                    else:
                        liquidity_line_name = payment.name


                    transfer_move_vals_extra['line_ids'].append((0, 0, {
                        'name': rec_pay_line_name + " : " + line.invoice_id.name,
                        'amount_currency': counterpart_amount + write_off_amount if currency_id else 0.0,
                        'currency_id': currency_id,
                        'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                        'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                        'date_maturity': payment.payment_date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': payment.destination_account_id.id,
                        'payment_id': payment.id,
                        'invoice_id': line.invoice_id.id,
                    }))

                balance = payment_total_amount - check_use_amount
                if check_use_amount != payment_total_amount and payment.payment_type == 'inbound':
                    transfer_move_vals_extra['line_ids'].append((0, 0, {
                        'name': rec_pay_line_name,
                        'amount_currency': counterpart_amount + write_off_amount if currency_id else 0.0,
                        'currency_id': currency_id,
                        'debit': balance or 0.0,
                        'credit':  0.0,
                        'date_maturity': payment.payment_date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': payment.destination_account_id.id,
                        'payment_id': payment.id,
                    }))
                elif check_use_amount != payment_total_amount and payment.payment_type in ('outbound', 'transfer'):
                    transfer_move_vals_extra['line_ids'].append((0, 0, {
                        'name': rec_pay_line_name,
                        'amount_currency': counterpart_amount + write_off_amount if currency_id else 0.0,
                        'currency_id': currency_id,
                        'debit': 0.0 ,
                        'credit': balance or 0.0,
                        'date_maturity': payment.payment_date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': payment.destination_account_id.id,
                        'payment_id': payment.id,
                    }))
                all_move_vals.append(transfer_move_vals_extra)

        return all_move_vals
