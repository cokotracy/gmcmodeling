# -*- coding: utf-8 -*-
from odoo import models, fields


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    flag_monthly_limit = fields.Boolean(string="Monthly Leave Limit")
    leave_limit_days = fields.Float(string="Leave Limit")
