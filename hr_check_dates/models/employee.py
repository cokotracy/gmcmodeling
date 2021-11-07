# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime, timedelta

employee_dates_list = [(0, 'medical_end_date', 'تاريخ انتهاء التأمين الطبي'),
                       (1, 'residency_end_date', 'تاريخ انتهاء الإقامة'),
                       (2, 'passport_end_date', 'تاريخ انتهاء جواز السفر'),
                       (3, 'syndicate_membership_end_date', 'تاريخ انتهاء عضوية النقابة'),
                       (4, 'visa_expire_date', 'تاريخ انتهاء التأشيرة'),
                       (5, 'driving_license_end_date', 'تاريخ انتهاء رخصة القيادة'),
                       (6, 'contract_end_date', 'تاريخ انتهاء العقد')]


# Subtract a number of days from specific date
def get_difference(date, days):
    return date - timedelta(days=days)


# Check if a specific date in 90-Days interval before or not
def check_in_90days(date):
    today_date = datetime.today().date()
    if get_difference(date, 90) == today_date:
        return True
    else:
        return False


# Check if a specific date in 30-Days interval before or not
def check_in_30days(date):
    today_date = datetime.today().date()
    if get_difference(date, 30) == today_date:
        return True
    else:
        return False


# Check if a specific date in 7-Days interval before or not
def check_in_7days(date):
    today_date = datetime.today().date()
    if get_difference(date, 7) == today_date:
        return True
    else:
        return False


# Check if a specific date in 1-Days interval before or not
def check_in_1days(date):
    today_date = datetime.today().date()
    if get_difference(date, 1) == today_date:
        return True
    else:
        return False


# Check if a specific date equal today or not
def check_is_today(date):
    today_date = datetime.today().date()
    if today_date.day == date.day and today_date.month == date.month:
        return True
    else:
        return False


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    contract_end_date = fields.Date(string='Contract End Date',related='contract_id.date_end')

    # Send an email with specific employee data
    def send_mail(self, email_template_xml_id, employee_id):
        template_id = self.env.ref(email_template_xml_id)
        template_id.send_mail(employee_id, force_send=True)

    def check_date(self, date, field_english_name, field_arabic_name, employee_id):
        if check_in_90days(date):
            if employee_id.company_id.hr_employee_ids and field_english_name == 'contract_end_date':
                for user in employee_id.company_id.hr_employee_ids:
                    self.env['mail.activity'].create({
                        'res_id': employee_id.id,
                        'res_model_id': self.env['ir.model']._get('hr.employee').id,
                        'activity_type_id': 6,
                        'summary': field_arabic_name,
                        'note': "سينتهى هذا التاريخ فى خلال 90 يوم",
                        'user_id': user.id,
                    })
        elif check_in_30days(date):
            if employee_id.company_id.hr_employee_ids:
                for user in employee_id.company_id.hr_employee_ids:
                    self.env['mail.activity'].create({
                        'res_id': employee_id.id,
                        'res_model_id': self.env['ir.model']._get('hr.employee').id,
                        'activity_type_id': 6,
                        'summary': field_arabic_name,
                        'note': "سينتهى هذا التاريخ فى خلال 30 يوم",
                        'user_id': user.id,
                    })
        elif check_in_7days(date):
            if employee_id.company_id.hr_employee_ids:
                for user in employee_id.company_id.hr_employee_ids:
                    self.env['mail.activity'].create({
                        'res_id': employee_id.id,
                        'res_model_id': self.env['ir.model']._get('hr.employee').id,
                        'activity_type_id': 6,
                        'summary': field_arabic_name,
                        'note': "سينتهى هذا التاريخ فى خلال 7 أيام",
                        'user_id': user.id,
                    })
        elif check_in_1days(date):
            if employee_id.company_id.hr_employee_ids:
                for user in employee_id.company_id.hr_employee_ids:
                    self.env['mail.activity'].create({
                        'res_id': employee_id.id,
                        'res_model_id': self.env['ir.model']._get('hr.employee').id,
                        'activity_type_id': 6,
                        'summary': field_arabic_name,
                        'note': "سينتهى هذا التاريخ فى خلال يوم واحد",
                        'user_id': user.id,
                    })

    # Use check_date
    def check_any_date(self):
        for employee in self.env['hr.employee'].search([]):
            if employee.birthday:
                birthday_email = 'hr_check_dates.email_birthday_wishes_employee_template'
                if check_is_today(employee.birthday):
                    self.send_mail(birthday_email, employee.id)
            for field in employee_dates_list:
                if getattr(employee, field[1]):
                    emp_id = employee
                    # field_name = employee._fields[field[1]].string
                    date = getattr(employee, field[1])
                    field_english_name = field[1]
                    field_arabic_name = field[2]
                    self.check_date(date, field_english_name, field_arabic_name, emp_id)


class Company(models.Model):
    _inherit = 'res.company'

    hr_employee_ids = fields.Many2many(string='HR Employees', comodel_name='res.users')
