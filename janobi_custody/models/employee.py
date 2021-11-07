# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    custody_value = fields.Float('Custody Value', default=0.0)


class Company(models.Model):
    _inherit = 'res.company'

    financial_manager = fields.Many2one('res.users', 'Financial Manager')
