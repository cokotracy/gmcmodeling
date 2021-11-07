# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Contracts(models.Model):
    _name = 'contracts'

    name = fields.Char(string="Name", required=False, )
    customer_account_id = fields.Many2one(comodel_name="account.account",
                                          string="Customer/Subcontractor Account", required=False, )
    revenue_account_id = fields.Many2one(comodel_name="account.account",
                                         string="Revenue/Expense Account", required=False, )
    is_owner_contract = fields.Boolean(string='Owner Contract')
    is_subcontractor_contract = fields.Boolean(string='Subcontractor Contract')
    terms_conditions = fields.Html(string="Contract Terms and Conditions", required=False, )
