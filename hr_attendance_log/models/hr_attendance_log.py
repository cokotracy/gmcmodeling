# -- coding: utf-8 --

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    fb_id = fields.Char(string='FP ID')


class HRAttendanceLog(models.Model):
    _name = 'hr.attendance.log'
    _description = 'HR Attendance Log'
    _rec_name = 'employee_id'

    check_in = fields.Datetime(string='Check In')
    check_out = fields.Datetime(string='Check Out')
    attendance_fb_id = fields.Char(string='Finger Print ID')
    transferred = fields.Boolean(string='Transferred')
    transfer_log_id = fields.Many2one('hr.attendance.transfer.log', 'transfer_log_id')

    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee',
                                  readonly=False, required=False)
    copy_employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee',
                                       compute="get_employee_id", readonly=False)

    attendance_rf_id = fields.Char(string='EMP ID', required=False, readonly=False)
    copy_attendance_rf_id = fields.Char(string='EMP ID', required=False, readonly=False,
                                        compute="get_employee_id")

    @api.depends('employee_id', 'attendance_rf_id')
    def get_employee_id(self):
        for rec in self:
            employee = self.env['hr.employee'].search([('fb_id', '=', rec.attendance_rf_id)])
            if rec.attendance_rf_id:
                rec.copy_employee_id = rec.employee_id = employee
                rec.attendance_rf_id = rec.copy_attendance_rf_id = employee.fb_id
            else:
                rec.employee_id = rec.copy_employee_id = rec.employee_id
                rec.attendance_rf_id = rec.copy_attendance_rf_id = rec.employee_id.fb_id
