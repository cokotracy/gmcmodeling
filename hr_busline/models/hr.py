# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    busline_id = fields.Many2one('hr.bus.line', string='Bus Line')


class HrEmployee(models.AbstractModel):
    _inherit = 'hr.employee'

    busline_id = fields.Many2one('hr.bus.line', string='Bus Line')
