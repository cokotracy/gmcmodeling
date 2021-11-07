# -*- coding: utf-8 -*-

from odoo import models, fields, api

class BankStatementLine(models.Model):
    _inherit="account.bank.statement.line"

    reference = fields.Char(string="Reference")
