from openerp import fields, models, api, exceptions
from openerp.exceptions import  Warning
from datetime import date

# ------------- A.Salama -------------------


class wizard_lg_draw(models.TransientModel):
    _name = "wizard_lg_draw"

    # =============== wizard fields ================
    account_id = fields.Many2one(comodel_name='account.account', string="WithDraw Account", required=True,
                                 domain=[('user_type_id', '=', 'Bank and Cash')])

    def wizard_draw_lg(self):
        lg_active_ids = self._context.get('active_ids')
        lg_id = self.env['account.letter'].browse(lg_active_ids)
        if lg_id:
            ref = 'LG With Draw number ' + lg_id.number + ' / ' + lg_id.name
            lg_id.create_journal_entry(lg_id.journal_id.id, date.today(), self.account_id.id,
                                       lg_id.lc_margin_account_id.id, lg_id.name, ref, lg_id.lc_value)

