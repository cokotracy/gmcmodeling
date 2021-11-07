# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date


class Partners(models.Model):
    _inherit = 'res.partner'

    register_no = fields.Char(string="رقم التسجيل", required=False, )
    register_no_exp_date = fields.Date(string="Exp Date", required=False, )

    file_no = fields.Char(string="رقم الملف", required=False, )
    file_no_exp_date = fields.Date(string="Exp Date", required=False, )

    national_ID = fields.Char(string="الرقم القومي", required=False, )
    national_ID_exp_date = fields.Date(string="Exp Date", required=False, )

    mission_code = fields.Char(string="كود المأمورية المختصة", required=False, )


    dealing_nature = fields.Selection(string="طبيعة التعامل", selection=[('1', '1'), ('2', '2'),('3', '3'),('4', '4'),('5', '5'),('6', '6'),('7', '7'),('8', '8'),('9', '9'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20') ], required=False, )



    def check_expiration_date(self):
        for rec in self.env['res.partner'].search([]):
            date_today = datetime.strptime(str(date.today()), '%Y-%m-%d').date()
            billing_group = self.env.ref('account.group_account_manager')
            billing_group_users = []
            if billing_group.users:
                for user in billing_group.users:
                    billing_group_users.append(user.partner_id.id)
            if rec.register_no_exp_date:
                register_no_exp_date = datetime.strptime(str(rec.register_no_exp_date), '%Y-%m-%d').date()

                diff_register_no_exp_date = register_no_exp_date - relativedelta(months=1)
                diff_register_no_days_date = datetime.strptime(str(diff_register_no_exp_date), '%Y-%m-%d').date()
                if date_today == diff_register_no_days_date:
                        thread_pool = self.env['mail.thread']
                        thread_pool.message_notify(
                            partner_ids=billing_group_users,
                            subject=str('Partner Register No Notification'),
                            body=str('Partner Register No of ' + str(rec.name) + ' will expired in ' + str(
                                rec.register_no_exp_date)) + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                                rec.id) + '&view_type=form&model=res.partner&action=" style="font-weight: bold">' + str(
                                rec.name) + '</a>',
                            email_from=self.env.user.company_id.catchall or self.env.user.company_id.email, )

            if rec.file_no_exp_date:
                file_no_exp_date = datetime.strptime(str(rec.file_no_exp_date), '%Y-%m-%d').date()

                diff_file_no_exp_date = file_no_exp_date - relativedelta(months=1)
                diff_file_no_exp_date = datetime.strptime(str(diff_file_no_exp_date), '%Y-%m-%d').date()
                if date_today == diff_file_no_exp_date:
                    thread_pool = self.env['mail.thread']
                    thread_pool.message_notify(
                        partner_ids=billing_group_users,
                        subject=str('Partner File No Notification'),
                        body=str('Partner File No of ' + str(rec.name) + ' will expired in ' + str(
                            rec.file_no_exp_date)) + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                            rec.id) + '&view_type=form&model=res.partner&action=" style="font-weight: bold">' + str(
                            rec.name) + '</a>',
                        email_from=self.env.user.company_id.catchall or self.env.user.company_id.email, )

            if rec.national_ID_exp_date:
                national_ID_exp_date = datetime.strptime(str(rec.national_ID_exp_date), '%Y-%m-%d').date()

                diff_national_ID_exp_date = national_ID_exp_date - relativedelta(months=1)
                diff_national_ID_exp_date = datetime.strptime(str(diff_national_ID_exp_date), '%Y-%m-%d').date()
                if date_today == diff_national_ID_exp_date:
                    thread_pool = self.env['mail.thread']
                    thread_pool.message_notify(
                        partner_ids=billing_group_users,
                        subject=str('Partner National ID Notification'),
                        body=str('Partner National ID of ' + str(rec.name) + ' will expired in ' + str(
                            rec.national_ID_exp_date)) + ' click here to open: <a target=_BLANK href="/web?#id=' + str(
                            rec.id) + '&view_type=form&model=res.partner&action=" style="font-weight: bold">' + str(
                            rec.name) + '</a>',
                        email_from=self.env.user.company_id.catchall or self.env.user.company_id.email, )






class AccountTax(models.Model):
    _inherit = 'account.tax'

    discount_type = fields.Selection(string="نـوع الخصـم", selection=[('1', '1'), ('2', '2'),('3', '3'),('4', '4'),('5', '5'),('6', '6'),('7', '7'),('8', '8'),('9', '9'),('10', '10'),('11', '11'),('12', '12'),('13', '13'),('14', '14'),('15', '15'),('16', '16'),('17', '17'),('18', '18'),('19', '19'),('20', '20') ], required=False, )

