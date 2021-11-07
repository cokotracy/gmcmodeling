# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    timesheet_cost = fields.Float('Timesheet Cost')
    timesheet_ids = fields.One2many('account.analytic.line', 'maintenance_id', string='Timesheets')


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    maintenance_id = fields.Many2one('maintenance.equipment', string='Maintenance')


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # when the name is not provide by the 'Add a line', we set a default one
            if vals.get('maintenance_id') and not vals.get('account_id'):
                maintenance = self.env['maintenance.equipment'].browse(vals.get('maintenance_id'))
                vals['account_id'] = maintenance.analytic_account_id.id

        result = super(AccountAnalyticLine, self).create(vals_list)






