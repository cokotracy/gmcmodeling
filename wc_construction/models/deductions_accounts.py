# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DeductionAccounts(models.Model):
    _name = 'deduction.accounts'

    name = fields.Char(string="Name", required=True, )
    counterpart_account_id = fields.Many2one(comodel_name="account.account", string="Counterpart Account", required=False, )
    down_payment_account_id = fields.Many2one(comodel_name="account.account", string="استحقاق دفعة مقدمه", required=False, )
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=False, )
    deduction_type = fields.Selection(string="Type", selection=[('addition', 'Addition'), ('deduction', 'Deduction'),('down_payment', 'Down Payments'),('performance_bond', 'Performance bond'), ('retention', 'Retention'), ], required=False, )
    is_percentage = fields.Boolean(string="Is Percentage ?",  )
    is_down_payment = fields.Boolean(string="Is Down Payment ?",  )







