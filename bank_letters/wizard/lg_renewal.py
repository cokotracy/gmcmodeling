from openerp import fields, models, api, exceptions
from openerp.exceptions import  Warning
from datetime import date

# ------------- A.Salama -------------------


class wizard_lg_renewal(models.TransientModel):
    _name = "wizard_lg_renewal"

    
        # =============== wizard fields ================

    lg_date_end = fields.Date('End Date', required=True)
    lg_renewal_fees = fields.Float('Renewal Fees', required=True)

    def wizard_renewal_lg(self):
        renewal_obj = self.env['account.letter.renewal']
        lg_active_ids = self._context.get('active_ids')
        lg_id = self.env['account.letter'].browse(lg_active_ids)
        if lg_id:
            ref = 'LG Renewal number ' + lg_id.number + ' / ' + lg_id.name
            credit_account_id = lg_id.type == 'credit' and lg_id.journal_id.default_debit_account_id.id \
                                or lg_id.journal_id.default_credit_account_id.id
            move = lg_id.create_journal_entry(lg_id.journal_id.id, date.today(), lg_id.lg_renewal_account_id.id,
                                              credit_account_id, lg_id.name, ref, self.lg_renewal_fees,'renewal')
            if move:
                renewal_obj.create({
                    'move_id': move.id,
                    'letter_id': lg_id.id,
                    'lg_renewal_fees': self.lg_renewal_fees,
                    'lg_date_end': self.lg_date_end,
                })
                lg_id.write({'is_renewal': True,'state': 'renewal'})
            else:
                raise Warning("Something went wrong.\n The Entry doesn't created\n please review your administer.")

