# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import ValidationError


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    @api.constrains('request_date_from')
    def _check_leave_limit(self):
        for req in self:
            if req.holiday_status_id.flag_monthly_limit:
                leave_ids = self.env['hr.leave'].search(
                    [('employee_id', '=', req.employee_id.id),
                     ('holiday_status_id', '=', req.holiday_status_id.id),
                     ('state', '=', 'validate')])
                leaves = 0.00
                exceed = False
                if leave_ids:
                    current_leave_date = req.request_date_from
                    current_leave_year = int(current_leave_date.year)
                    current_leave_month = int(current_leave_date.month)
                    for leave in leave_ids:
                        leave_date = leave.request_date_from
                        year = int(leave_date.year)
                        month = int(leave_date.month)
                        if year == current_leave_year and \
                                month == current_leave_month:
                            if leave._get_leave_take_in() == 'day':
                                leaves += leave.number_of_days_display
                            elif leave._get_leave_take_in() == 'hour':
                                leaves += leave._get_requested_hours()
                remaining = req.holiday_status_id.leave_limit_days - float(leaves)
                if float(req.number_of_days_display) > float(remaining) and req._get_leave_take_in() == 'day':
                    exceed = True
                if float(req._get_requested_hours()) > float(remaining) and req._get_leave_take_in() == 'hour':
                    exceed = True
                if exceed:
                    raise ValidationError(
                        _("You Monthly Leave Limit is : %s\nYou have "
                          "already taken %s leaves in this month\nNow your "
                          "remaining leaves are :  %s") %
                        (req.holiday_status_id.leave_limit_days,
                         float(leaves),
                         float(remaining)))

    def _get_requested_hours(self):
        if self.request_unit_half:
            requested_hours = 4.0
        elif self.request_unit_hours and self.request_hour_from and self.request_hour_to:
            requested_hours = float(self.request_hour_to) - float(self.request_hour_from)
        else:
            requested_hours = self.number_of_hours_display
        return requested_hours

    def _get_leave_take_in(self):
        return self.holiday_status_id.request_unit
