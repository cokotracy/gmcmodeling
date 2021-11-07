# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: cybrosys(<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################
import pytz
from datetime import datetime
import logging
# from odoo.custom.biobusiness.oh_hr_zk_attendance.zk import ZK
from .zk.base import ZK
# from . import zklib
# from . zkconst import *
from struct import unpack
from odoo import _

from odoo import api, fields, models
from odoo import _, exceptions

from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    device_id = fields.Integer(string='Biometric Device ID')
    machine_id = fields.Many2one('zk.machine', 'Biometric Machine')
    dummy = fields.Boolean('Dummy?')

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        pass

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """overriding the __check_validity function for employee attendance."""
        pass


class ZkMachine(models.Model):
    _name = 'zk.machine'

    name = fields.Char(string='Machine IP', required=True)
    port_no = fields.Integer(string='Port No', required=True)
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)

    def clear_attendance(self):
        for info in self:
            try:
                machine_ip = info.name
                port = info.port_no
                zk = ZK(machine_ip, port)
                conn = zk.connect()
                if conn:
                    conn.disable_device()
                    clear_data = zk.get_attendance()
                    if clear_data:
                        zk.clear_attendance()
                        self._cr.execute("""delete from zk_machine_attendance""")
                    else:
                        raise UserError(_('Unable to get the attendance log, please try again later.'))
                else:
                    raise UserError(_('Unable to connect, please check the parameters and network connections.'))
                conn.enable_device()
            except:
                raise ValidationError('Warning !!! Machine is not connected')

    @api.model
    def cron_download(self):
        machines = self.env['zk.machine'].search([])
        for machine in machines:
            machine.download_attendance()

    def download_attendance(self):
        _logger.info("++++++++++++Fingerprint Cron Executed++++++++++++++++++++++")
        zk_attendance = self.env['zk.machine.attendance']
        att_obj = self.env['hr.attendance.log']
        for machine in self:
            machine_ip = machine.name
            port = machine.port_no
            zk = ZK(machine_ip, port, force_udp=True, timeout=200)
            conn = zk.connect()
            if conn:
                conn.disable_device()
                # This # code use to create employee if it search and got no results.
                # employee_ids = self.env['hr.employee'].search([]).mapped('device_id')
                # users = zk.get_users()
                # Use to create employees if not exists
                # for user in users:
                #     if user.user_id and int(user.user_id) not in employee_ids:
                #         self.env['hr.employee'].create(
                #             {'device_id': int(user.user_id), 'name': str(user.name), 'machine_id': machine.id})

                # Attendances returned from machine.
                attendance = zk.get_attendance()
                print(attendance)
                if attendance:
                    try:
                        for attend_record in attendance:
                            # TODO In case Punch Type in [0, 1, 2, 3, 4, 5] To Avoid Raise Exception
                            if attend_record.punch not in [0, 1, 2, 3, 4, 5]:
                                continue
                            print(attend_record.timestamp, attend_record.punch, '222222222222222222')
                            atten_time = attend_record.timestamp
                            print('atten_time1 =', atten_time)
                            atten_time = datetime.strptime(
                                atten_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                            print('atten_time2 =', atten_time)
                            local_tz = pytz.timezone(self.env.user.partner_id.tz or 'UTC')
                            print('local_tz =', local_tz)
                            local_dt = local_tz.localize(atten_time, is_dst=None)
                            print('local_dt = ', local_dt)
                            utc_dt = local_dt.astimezone(pytz.utc)
                            print('utc_dt1 =', utc_dt)
                            utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                            print('utc_dt2 = ', utc_dt)
                            atten_time = datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S")
                            print('atten_time3 =', atten_time)
                            atten_time = fields.Datetime.to_string(atten_time)
                            print('atten_time4 =', atten_time)
                            get_user_id = self.env['hr.employee'].search([('machine_id', '=', machine.id),
                                                                          ('device_id', '=',
                                                                           int(attend_record.user_id))])
                            print(get_user_id, '555')
                            if get_user_id:
                                print('ooooooooooooooooooooooooooooo')
                                duplicate_atten_ids = zk_attendance.search(
                                    [('device_id', '=', int(attend_record.user_id)),
                                     ('punching_time', '=', atten_time), ('machine_id', '=', machine.id)])
                                print(duplicate_atten_ids)
                                if duplicate_atten_ids:
                                    continue
                                else:
                                    print(' in else ')
                                    for user in get_user_id:
                                        print(atten_time, str(attend_record.punch))
                                        zk_attendance.create({'employee_id': user.id,
                                                              'device_id': int(attend_record.user_id),
                                                              'machine_id': machine.id,
                                                              'attendance_type': '1',
                                                              'punch_type': str(attend_record.punch),
                                                              'punching_time': atten_time,
                                                              'address_id': machine.address_id.id})
                                        print(zk_attendance.id, '77')
                                        print(user.id, user.fb_id, '5454545')
                                        att_var = att_obj.search([('employee_id', '=', user.id),
                                                                  ('check_out', '=', False),
                                                                  ('attendance_rf_id', '=', user.fb_id)
                                                                  ])  # ('machine_id', '=', machine.id)
                                        print(att_var)
                                        print(attend_record.timestamp)
                                        print('attend_record.punch = ', attend_record.punch, attend_record.status)
                                        if str(attend_record.punch) == '0':  # check-in
                                            print(' check in ')
                                            if not att_var:
                                                print(' not att_var ')
                                                att_obj.create({'employee_id': user.id,
                                                                'check_in': atten_time,
                                                                'attendance_rf_id': user.fb_id,
                                                                })  # 'machine_id': machine.id
                                            else:
                                                print(' is att_var ')
                                                attend_date = fields.Datetime.from_string(atten_time).date()
                                                att_var_list = []
                                                for rec in att_var:
                                                    att_var_list.append(rec.check_in.date())
                                                if attend_date not in att_var_list:
                                                    att_obj.create({'employee_id': user.id,
                                                                    'check_in': atten_time,
                                                                    'attendance_rf_id': user.fb_id,
                                                                    })  # 'machine_id': machine.id

                                        if str(attend_record.punch) == '1':  # check-out
                                            print(' check out ')
                                            attend_date = fields.Datetime.from_string(atten_time).date()
                                            if len(att_var) == 1:
                                                if att_var.check_in.date() != attend_date:
                                                    att_obj.create(
                                                        {'employee_id': user.id, 'check_in': atten_time,
                                                         'check_out': atten_time,
                                                         'attendance_rf_id': user.fb_id
                                                         })  # 'machine_id': machine.id,
                                                    # 'dummy': True
                                                else:
                                                    att_var.write({'check_out': atten_time})
                                            else:
                                                att_var1 = att_obj.search(
                                                    [('employee_id', '=', user.id),
                                                     ('attendance_rf_id', '=', user.fb_id)]).filtered(
                                                    lambda x: fields.Datetime.from_string(
                                                        x.check_in).date() == attend_date)  # ('machine_id', '=', machine.id
                                                if att_var1:
                                                    att_var1[0].write({'check_out': atten_time})
                                                else:
                                                    att_obj.create(
                                                        {'employee_id': user.id, 'check_in': atten_time,
                                                         'check_out': atten_time,
                                                         'attendance_rf_id': user.fb_id,
                                                         })
                                                    # 'machine_id': machine.id, 'dummy': True
                            else:
                                employee_name = 'Fingerprint Employee' + '-' + attend_record.user_id
                                employee = self.env['hr.employee'].create(
                                    {'device_id': int(attend_record.user_id), 'name': employee_name,
                                     'machine_id': machine.id})
                                att_vals = {
                                    'employee_id': employee.id,
                                    'device_id': int(attend_record.user_id),
                                    'machine_id': machine.id,
                                    'attendance_type': '1',
                                    'punch_type': str(attend_record.punch),
                                    'punching_time': atten_time,
                                    'check_in': atten_time,
                                    'address_id': machine.address_id.id
                                }
                                zk_attendance.create(att_vals)
                                att_obj.create({
                                    'employee_id': employee.id,
                                    'check_in': atten_time,
                                    'attendance_rf_id': employee.fb_id
                                    # 'machine_id': machine.id
                                })
                        conn.enable_device()
                    except Exception as e:
                        print("Process terminate : {}".format(e))
                    finally:
                        if conn:
                            conn.disconnect()

                else:
                    raise UserError(_('Unable to get the attendance log, please try again later.'))

            else:
                raise UserError(_('Unable to connect, please check the parameters and network connections.'))
