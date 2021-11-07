from openerp import SUPERUSER_ID, api, fields, models, _

class account_invoice(models.Model):
    _inherit = "account.move"
    
    
    def action_move_create(self):
        
        purchase_id = -1
        letter_of_credit = -1
        purchase_order =  self.env['purchase.order'].search([])
        for pick in purchase_order:
            if pick.invoice_ids:
                for inv_id in pick.invoice_ids:
                    if inv_id.id == self.id:
                        purchase_id = pick.id
                        if pick.letter_of_credit.id:
                            letter_of_credit = pick.letter_of_credit.id
        
        if letter_of_credit <= -1:
            return super(account_invoice, self).action_move_create()
        else:
            """ Creates invoice related analytics and financial move lines """
            lc_liability_account = self.env['ir.values'].get_default('letter_of_credit.config.settings', 'lc_liability_account')
            account_move = self.env['account.move']
    
            for inv in self:
                
                #lc_liability_account = inv.account_id.id
                
                if not inv.journal_id.sequence_id:
                    raise UserError(_('Please define sequence on the journal related to this invoice.'))
                if not inv.invoice_line_ids:
                    raise UserError(_('Please create some invoice lines.'))
                if inv.move_id:
                    continue
    
                ctx = dict(self._context, lang=inv.partner_id.lang)
    
                if not inv.date_invoice:
                    inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
                date_invoice = inv.date_invoice
                company_currency = inv.company_id.currency_id
    
                # create move lines (one per invoice line + eventual taxes and analytic lines)
                iml = inv.invoice_line_move_line_get()
                iml += inv.tax_line_move_line_get()
                
                diff_currency = inv.currency_id != company_currency
                # create one move line for the total and possibly adjust the other lines amount
                total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)
    
                name = inv.name or '/'
                if inv.payment_term_id:
                    totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=inv.currency_id.id).compute(total, date_invoice)[0]
                    res_amount_currency = total_currency
                    ctx['date'] = date_invoice
                    for i, t in enumerate(totlines):
                        if inv.currency_id != company_currency:
                            amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                        else:
                            amount_currency = False
    
                        # last line: add the diff
                        res_amount_currency -= amount_currency or 0
                        if i + 1 == len(totlines):
                            amount_currency += res_amount_currency
    
                        iml.append({
                            'type': 'dest',
                            'name': name,
                            'price': t[1],
                            'account_id': lc_liability_account,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'invoice_id': inv.id
                        })
                else:
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': total,
                        'account_id': lc_liability_account,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
                part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
                line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
                line = inv.group_lines(iml, line)
    
                journal = inv.journal_id.with_context(ctx)
                line = inv.finalize_invoice_move_lines(line)
                
                date = inv.date or date_invoice
                move_vals = {
                    'ref': inv.reference,
                    'line_ids': line,
                    'journal_id': journal.id,
                    'date': date,
                    'narration': inv.comment,
                }
                ctx['company_id'] = inv.company_id.id
                ctx['dont_create_taxes'] = True
                ctx['invoice'] = inv
                ctx_nolang = ctx.copy()
                ctx_nolang.pop('lang', None)
                move = account_move.with_context(ctx_nolang).create(move_vals)
                # Pass invoice in context in method post: used if you want to get the same
                # account move reference when creating the same invoice after a cancelled one:
                move.post()
                # make the invoice point to that move
                vals = {
                    'move_id': move.id,
                    'date': date,
                    'move_name': move.name,
                }
                inv.with_context(ctx).write(vals)
        return True
        