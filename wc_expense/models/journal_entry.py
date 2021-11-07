# -*- coding: utf-8 -*-

from odoo import models, fields, api

class JournalEntry(models.Model):
    _inherit = 'account.move'

    expense_sheet_id = fields.Many2one(comodel_name="hr.expense.sheet", string="Expense Sheet", required=False, )

    payment_id = fields.Many2one(comodel_name="account.payment", string="Account Payment",compute='get_payment', required=False, )

    @api.depends('name','payment_id')
    def get_payment(self):
        self.payment_id = False
        for rec in self.env['account.payment'].search([('account_move_no','=',self.name)]):
            self.payment_id = rec.id
