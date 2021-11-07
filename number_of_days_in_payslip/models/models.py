# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import calendar
import datetime


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    number_of_days = fields.Integer(string="Number Of Days", required=False, compute="get_num_of_days")

    @api.depends('employee_id')
    def get_num_of_days(self):
        for rec in self:
            rec.number_of_days = rec.number_of_days
            date_now = fields.Date.today()
            year = date_now.year
            month = date_now.month
            d = calendar.monthrange(year, month)
            a = list(d)
            rec.number_of_days = a[1]


class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    number_of_days = fields.Integer(string="Number Of Days", required=False, compute="get_number_of_days")

    @api.depends('date_from', 'date_to')
    def get_number_of_days(self):
        for rec in self:
            rec.number_of_days = rec.number_of_days
            rec.number_of_days = rec.date_to.day - rec.date_from.day
