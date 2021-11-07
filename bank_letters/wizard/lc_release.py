from openerp import fields, models, api, exceptions
from openerp.exceptions import  Warning
from datetime import date

# ------------- A.Salama -------------------


class wizard_lc_release(models.TransientModel):
    _name = "wizard_lc_release"

    # =============== wizard fields ================
    shipment_val = fields.Float(string="Shipment Amount")
    lc_val = fields.Float(string="LC Amount Deduct")
    loan_val = fields.Float(string="Loan Amount",compute='_get_loan')
    bank_exp = fields.Float(string="Bank Expenses")
    mang_exp = fields.Float(string="Managerial Expenses")
    
    @api.onchange('shipment_val','lc_val')
    def _get_loan(self):
        if self.lc_val and self.shipment_val:
            self.loan_val = self.shipment_val - self.lc_val

    def wizard_release_lc(self):
        lc_active_ids = self._context.get('active_ids')
        lc_id = self.env['account.letter'].browse(lc_active_ids)
        lc_release = self.env['account.letter.release']
        if lc_id:
            lc_release.create({
                'letter_id':lc_id.id,
                'shipment_val':self.shipment_val,
                'lc_val':self.lc_val,
                'loan_val':self.loan_val,
            })
            total_shipment_val = sum(rel.shipment_val for rel in lc_release.search([('letter_id','=',lc_id.id)]))
            if total_shipment_val > lc_id.lc_value:
                raise Warning('You Can not proceed with shipment amount above PO value!!!')
            else:
                partner_payable_account = lc_id.partner_id.property_account_payable_id
                bank_related_account_id = lc_id.journal_id.default_credit_account_id
                if not partner_payable_account:
                    raise Warning("Related partner doesn't have Partner Payable Account!!!")
                if not bank_related_account_id:
                    raise Warning("Related Bank doesn't have Default Credit Account!!!")
                ref = 'Lc With Release number ' + lc_id.number + ' / ' + lc_id.name
                company_currency = self.env.user.company_id.currency_id
                shipment_val = self.shipment_val
                # lc_id.form_for and or
                lc_val = self.lc_val
                loan_val = self.loan_val
                bank_exp_val = self.bank_exp
                mang_exp_val = self.mang_exp
                if company_currency != lc_id.currency_id:
                    shipment_val = lc_id.currency_id.compute(shipment_val, company_currency)
                    lc_val = lc_id.currency_id.compute(lc_val, company_currency)
                    loan_val = lc_id.currency_id.compute(loan_val, company_currency)
                    bank_exp_val = lc_id.currency_id.compute(bank_exp_val, company_currency)
                    mang_exp_val = lc_id.currency_id.compute(mang_exp_val, company_currency)

                shipment_debit_line_vals = {
                    'name': lc_id.name,
                    'account_id': partner_payable_account.id,
                    'debit': shipment_val,
                    'ref': ref,
                    'partner_id':lc_id.partner_id.id,
                    'currency_id': lc_id.currency_id and lc_id.currency_id.id or False,
                }
                if lc_id.form_for:
                    account_id = bank_related_account_id.id
                else:
                    account_id = lc_id.lc_margin_account_id.id
                lc_credit_line_vals = {
                    'name': lc_id.name,
                    'account_id': account_id,
                    'credit': lc_val,
                    'ref': ref,
                    'partner_id': lc_id.partner_id.id,
                    'currency_id': lc_id.currency_id and lc_id.currency_id.id or False,
                    'analytic_account_id': lc_id.form_for and lc_id.analytic_account_id.id or False
    
                }
                loan_credit_line_vals = {
                    'name': lc_id.name,
                    'account_id': lc_id.lc_loan_account_id.id,
                    'credit': loan_val,
                    'ref': ref,
                    'date_maturity': lc_id.lc_date_end,
                    'currency_id': lc_id.currency_id and lc_id.currency_id.id or False,
                    'analytic_account_id': lc_id.analytic_account_id and lc_id.analytic_account_id.id or False,
                    'partner_id': lc_id.partner_id.id,
    
                }

                move_vals = {
                    'name': lc_id.name,
                    'journal_id': lc_id.journal_id.id,
                    'date': date.today(),
                    'ref': ref,
                    'state': 'posted',
                    'letter_id': lc_id.id,
                    'line_ids': [(0, 0, shipment_debit_line_vals),
                                 (0, 0, lc_credit_line_vals),
                                 (0, 0, loan_credit_line_vals)]
                }
                move_one = self.env['account.move'].create(move_vals)
                
                bank_exp_debit_line_vals = {
                    'name': lc_id.name,
                    'account_id': lc_id.lc_commission_account_id.id,
                    'debit': bank_exp_val,
                    'ref': ref,
                    'currency_id': lc_id.currency_id and lc_id.currency_id.id or False,
                }
                mang_exp_debit_line_vals = {
                    'name': lc_id.name,
                    'account_id': lc_id.lc_manag_exp_account_id.id,
                    'debit': mang_exp_val,
                    'ref': ref,
                    'currency_id': lc_id.currency_id and lc_id.currency_id.id or False,
                }
                mang_bank_exp_credit_line_vals = {
                    'name': lc_id.name,
                    'account_id': bank_related_account_id.id,
                    'credit': bank_exp_val + mang_exp_val,
                    'ref': ref,
                    'currency_id': lc_id.currency_id and lc_id.currency_id.id or False,
                    'analytic_account_id': lc_id.analytic_account_id and lc_id.analytic_account_id.id or False,
                }
            
                move_vals['line_ids'] = [
                    (0, 0, bank_exp_debit_line_vals),
                    (0, 0, mang_exp_debit_line_vals),
                    (0, 0, mang_bank_exp_credit_line_vals)]
                move_two = self.env['account.move'].create(move_vals)

                if move_one and move_two:
                    if lc_id.state == 'validate':
                        lc_id.write({'state':'release'})
                    return True
                else:
                    raise Warning(
                        "Something went wrong.\n The Entries doesn't created\n please review your administer.")



            