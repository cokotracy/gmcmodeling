# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrBusLine(models.Model):
    _name = 'hr.bus.line'
    _description = "Bus Line"

    name = fields.Text(string='Name')