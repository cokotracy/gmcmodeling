from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class HRAttendanceTransferLog(models.Model):
    _name = 'hr.attendance.transfer.log'
    _rec_name = 'type'

    type = fields.Selection(
        string='Type',
        selection=[('employee', 'Employee'),
                   ('department', 'Department'),
                   ('all', 'All')],
        required=True, default='all')

    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
        required=False)

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=False)

    date_from = fields.Date(
        string='Date From',
        required=True)

    date_to = fields.Date(
        string='Date To',
        required=True)

    date = fields.Date('Date', default=fields.Date.today())

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User', default=lambda self: self.env.uid, readonly=True)

    attendance_log_ids = fields.One2many(
        comodel_name='hr.attendance.log',
        inverse_name='transfer_log_id',
        string='Attendance Log',
        required=False)

    without_sign_count = fields.Integer(
        string='Without Sign Count',
        required=False)

    without_out_count = fields.Integer(
        string='Without Out Count',
        required=False)

    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'),
                   ('confirm', 'Confirmed'),
                   ('transfer', 'Transferred')],
        required=False, default='draft')

    def action_get_log(self):
        log = self.env['hr.attendance.log'].search(
            [('transferred', '=', False),
             '|',
             '&',
             ('check_in', '>=', self.date_from),
             ('check_in', '<=', self.date_to),
             '&',
             ('check_out', '>=', self.date_from),
             ('check_out', '<=', self.date_to)
             ])
        if self.type == 'employee':
            empl_log = log.filtered(lambda l: l.employee_id.id == self.employee_id.id)
        elif self.type == 'department':
            empl_log = log.filtered(lambda l: l.employee_id.department_id.id == self.department_id.id)
        else:
            empl_log = log
        self.attendance_log_ids = [(6, 0, empl_log.ids)]

    def action_confirm(self):
        if not self.attendance_log_ids:
            return
        self.write({
            'state': 'confirm'
        })

    def action_transfer(self):
        last_checkin = False

        for line in self.attendance_log_ids:
            # Get employee contract
            empl_contract = self.env['hr.contract'].search(
                [('employee_id', '=', line.employee_id.id),
                 ('state', '=', 'open')])

            # Check if there is working schedule.
            if not empl_contract or not empl_contract.resource_calendar_id:
                raise ValidationError(_('%s must has running contract with working schedule.' % (line.employee_id)))

            empl_working_sch = empl_contract.resource_calendar_id.attendance_ids
            check_in = line.check_in
            check_out = line.check_out

            if not check_in and not check_out:
                continue

            if not check_in:
                current_day = line.check_out.weekday()
                day_check_in = empl_working_sch.filtered(lambda w: w.dayofweek == str(current_day)).hour_from
                time_day_check_in = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(day_check_in) * 60, 60))
                time_obj = datetime.strptime(time_day_check_in, '%H:%M')
                check_in = datetime.combine(line.check_out.date(), time_obj.time())
                if last_checkin:
                    check_in = last_checkin
                    last_checkin = False

            if not check_out:
                overnigth = self.env['hr.over.night'].search(
                    [('date_from', '<=', line.check_in.date()), ('date_to', '>=', line.check_in.date())], limit=1)
                if overnigth and line.employee_id.id in overnigth.employee_ids.ids:
                    last_checkin = check_in
                    continue
                else:
                    current_day = line.check_in.weekday()
                    day_check_out = empl_working_sch.filtered(lambda w: w.dayofweek == str(current_day)).hour_to
                    time_day_check_out = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(day_check_out) * 60, 60))
                    time_obj = datetime.strptime(time_day_check_out, '%H:%M')
                    check_out = datetime.combine(line.check_in.date(), time_obj.time())

            
            self.env['hr.attendance'].create({
                'employee_id': line.employee_id.id,
                'check_in': check_in,
                'check_out': check_out
            })


            line.transferred = True

        self.write({
            'state': 'transfer'
        })
