# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools.misc import format_date
from odoo.exceptions import ValidationError
from odoo.fields import Date
from datetime import timedelta
from .int_to_arab_word import ArNumbers


def get_intersection_days(start1, start2, end1, end2):
    latest_starts = max(start1, start2)
    earliest_end = min(end1, end2)
    delta = (earliest_end - latest_starts).days
    return max(0, delta)


class HrReconciliation(models.Model):
    _name = 'hr.reconciliation'
    _description = "HR Reconciliation"

    name = fields.Char(string='Reconciliation no')
    currency_id = fields.Many2one(string="Currency", related='employee_id.currency_id', readonly=True)
    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee', ondelete='cascade', required=True)
    date = fields.Date(string='Reconciliation date')
    line_ids = fields.One2many(string='Additional Information', comodel_name='hr.reconciliation.line',
                               inverse_name='reconciliation_id')
    total_amount = fields.Monetary(string='Reconciliation Amount')
    type = fields.Selection(string='Type', selection=[('leave_allowance', 'Leave Allowance'),
                                                      ('leave_deduction', 'Leave Deduction'),
                                                      ('service_end', 'Service End Allowance'),
                                                      ('resign', 'Resignation')], required=True)

    state = fields.Selection(string='State', selection=[('draft', 'Draft'),
                                                        ('reconciled', 'Reconciled')], default='draft')
    payslip_id = fields.Many2one(string="Payslip", comodel_name='hr.payslip')
    notes = fields.Char(string='Notes')
    total_amount_log = fields.Text(string='Reconciliation Details')

    @api.onchange('employee_id')
    def get_loans(self):
        if self.employee_id :
            # total_loans = 0.0
            # for line in self.employee_id.loan_ids.filtered(lambda x:x.state == 'approve'):
            #     total_loans += line.amount
            # self.env['hr.reconciliation.line'].create({
            # 'name':'??????',
            # 'type':'sub',
            # 'amount':total_loans,
            # 'reconciliation_id':self.id
            # })
            self.write({'line_ids':[(0,0,{
            'name':'??????',
            'type':'sub',
            'amount':self.employee_id.loans_total,
            # 'amount':total_loans,
            })
            #     ,(0,0,{
            # 'name':'?????????? ??????',
            # 'type':'add',
            # 'amount':self.employee_id.contract_id.tickets_price,
            # })
                                    ]})
        else:
            self.line_ids.filtered(lambda x:x.name == '??????').unlink()

    @api.model
    def create(self, vals):
        vals.update({'name': self.env['ir.sequence'].next_by_code('reconciliation.code')})
        record = super(HrReconciliation, self).create(vals)
        # Add Travel tickets line by default from contract data
        contract = record.employee_id.contract_id
        if contract and vals['type'] != 'leave_deduction':
            if contract.number_of_tickets:
                detailed_log = u'?????? ?????????? : '
                if contract.tickets_type == 'land':
                    detailed_log += u' ?????? '
                elif contract.tickets_type == 'naval':
                    detailed_log += u' ???????? '
                else:
                    detailed_log += u' ?????? '
                detailed_log += u' ?????? ?????? ?????? ' + str(contract.number_of_tickets)
                record.line_ids.create({'reconciliation_id': record.id,
                                        'amount': contract.tickets_price,
                                        'type': 'add',
                                        'is_manual': True,
                                        'name': detailed_log})
        return record

    def get_amount(self):
        for record in self:
            contract = record.employee_id.contract_id
            if not contract:
                raise Warning('Employee Should have a contract')
            contract._get_service_duration(Date.to_date(record.date))
            # Number of service days for first 5 years (1825 days)
            base_days = contract.service_duration if contract.service_duration < 1825 else 1825
            # Number of service days after 5 years (1825 days)
            over_days = contract.service_duration - 1825 if contract.service_duration > 1825 else 0
            log = u'?????? ???????? ???????????? = ' + str(contract.service_duration) + '\n'
            # Clear previously created details lines , which was created automatically
            for line in record.line_ids:
                if not line.is_manual:
                    line.unlink()
            total = 0
            if record.type in ['leave_allowance', 'service_end', 'resign']:
                log += u'?????? ?????????? ???????????????? ' + '\n'
                log += u'???????????? ?????????????? = ' + str(round(contract.wage, 2)) + '\n'
                for line in record.employee_id.working_line_ids:
                    if line.state == 'not':
                        work_duration_base = get_intersection_days(contract.date_start, line.work_start_date,
                                                                   (contract.date_start + timedelta(days=base_days)),
                                                                   line.work_end_date)
                        work_duration_over = get_intersection_days(
                            (contract.date_start + timedelta(days=base_days + 1)),
                            line.work_start_date,
                            (contract.date_start + timedelta(
                                days=base_days + over_days)),
                            line.work_end_date) if over_days else 0
                        log += u'?????? ???????????????? = ' + str(line.work_duration) + '\n'
                        amount = (contract.wage / 30 / 365 * 21 * work_duration_base)
                        amount = int(amount) + 1 if amount % 1 >= 0.5 else int(amount)
                        total += amount
                        log += u'?????????? 21 ?????? ?????????? ???????? ???????????? = ' + str(round(amount, 2)) + '\n'
                        detailed_log = u'?????? ?????????? : ???? ???????????? ???? ' + Date.to_string(line.work_start_date) + u' ?????? ' \
                                       + Date.to_string(
                            line.work_start_date + timedelta(days=work_duration_base - 1)) + u' ?????????? 21 ?????? ?????????? '
                        record.line_ids.create({'reconciliation_id': record.id,
                                                'amount': amount,
                                                'type': 'add',
                                                'is_manual': False,
                                                'working_line_id': line.id,
                                                'name': detailed_log})
                        if work_duration_over > 0:
                            amount = (contract.wage / 30 / 365 * 30 * (work_duration_over + 2))
                            amount = int(amount) + 1 if amount % 1 >= 0.5 else int(amount)
                            total += amount
                            log += u'?????????? 30 ?????? ?????????? ???????? ???????????? = ' + str(round(amount, 2)) + '\n'
                            detailed_log = u'?????? ?????????? : ???? ???????????? ???? ' + Date.to_string(
                                line.work_start_date + timedelta(days=work_duration_base)) + u' ?????? ' \
                                           + Date.to_string(line.work_start_date + timedelta(
                                days=work_duration_base + work_duration_over + 1)) + u' ?????????? 30 ?????? ?????????? '
                            record.line_ids.create({'reconciliation_id': record.id,
                                                    'amount': amount,
                                                    'type': 'add',
                                                    'is_manual': False,
                                                    'working_line_id': line.id,
                                                    'name': detailed_log})
                        log += '----------------------' + '\n'

            if record.type == 'leave_deduction':
                log += u'?????? ?????????? ?????????????????? ' + '\n'
                log += u'???????????? ?????????????? = ' + str(round(contract.wage, 2)) + '\n'
                for line in record.employee_id.working_line_ids:
                    if line.state == 'not':
                        work_duration_base = get_intersection_days(contract.date_start, line.work_start_date,
                                                                   (contract.date_start + timedelta(days=base_days)),
                                                                   line.work_end_date)
                        work_duration_over = get_intersection_days(
                            (contract.date_start + timedelta(days=base_days + 1)),
                            line.work_start_date,
                            (contract.date_start + timedelta(
                                days=base_days + over_days)),
                            line.work_end_date) if over_days else 0
                        log += u'?????? ???????????????? = ' + str(line.work_duration) + '\n'
                        amount = (contract.wage / 30 / 365 * 15 * work_duration_base)
                        amount = int(amount) + 1 if amount % 1 >= 0.5 else int(amount)
                        total -= amount
                        log += u'?????????? 15 ?????? ?????????? ???????? ???????????? = ' + str(round(amount, 2)) + '\n'
                        detailed_log = u'?????? ?????????? : ???? ???????????? ???? ' + Date.to_string(
                            line.work_start_date) + u' ?????? ' + Date.to_string(
                            line.work_start_date + timedelta(days=work_duration_base - 1)) + u' ?????????? 15 ?????? ?????????? '
                        record.line_ids.create({'reconciliation_id': record.id,
                                                'amount': amount,
                                                'type': 'sub',
                                                'is_manual': False,
                                                'working_line_id': line.id,
                                                'name': detailed_log})
                        if work_duration_over > 0:
                            amount = (contract.wage / 30 / 365 * 30 * work_duration_over)
                            amount = int(amount) + 1 if amount % 1 >= 0.5 else int(amount)
                            total -= amount
                            log += u'?????????? 30 ?????? ?????????? ???????? ???????????? = ' + str(round(amount, 2)) + '\n'
                            detailed_log = u'?????? ?????????? : ???? ???????????? ???? ' + Date.to_string(
                                line.work_start_date + timedelta(days=work_duration_base)) + u' ?????? ' \
                                           + Date.to_string(line.work_start_date + timedelta(
                                days=work_duration_base + work_duration_over - 1)) + u' ?????????? 30 ?????? ?????????? '
                            record.line_ids.create({'reconciliation_id': record.id,
                                                    'amount': amount,
                                                    'type': 'sub',
                                                    'is_manual': False,
                                                    'working_line_id': line.id,
                                                    'name': detailed_log})
                        log += '----------------------' + '\n'

            if record.type == 'service_end':
                log += u'?????????? ???????? ' + '\n'
                log += u'???????????? ?????????? = ' + str(round(contract.total_wage, 2)) + '\n'
                log += u'?????? ???????? ???????????? ?????? 5 ?????????? = ' + str(base_days) + '\n'
                if over_days:
                    log += u'?????? ???????? ???????????? ?????? 5 ?????????? = ' + str(over_days) + '\n'
                amount = (contract.total_wage / 30 / 365 * 15 * base_days)
                amount = int(amount) + 1 if amount % 1 >= 0.5 else int(amount)
                total += amount
                log += u'???????????? ?????? 5 ?????????? (15 ?????? ??????????) = ' + str(round(amount, 2)) + '\n'
                detailed_log = u'???????????? ?????????? ???????????? : ???? ???????????? ???? ' + Date.to_string(contract.date_start) + u' ?????? ' \
                               + Date.to_string(
                    (contract.date_start + timedelta(days=base_days))) + u' ?????????? 15 ?????? ?????????? '
                record.line_ids.create({'reconciliation_id': record.id,
                                        'amount': amount,
                                        'type': 'add',
                                        'is_manual': False,
                                        'name': detailed_log})
                if over_days:
                    amount = (contract.total_wage / 30 / 365 * 30 * over_days)
                    amount = int(amount) + 1 if amount % 1 >= 0.5 else int(amount)
                    total += amount
                    log += u'???????????? ?????? 5 ?????????? (30 ?????? ??????????) = ' + str(round(amount, 2)) + '\n'
                    detailed_log = u'???????????? ?????????? ???????????? : ???? ???????????? ???? ' + Date.to_string((
                            contract.date_start + timedelta(days=base_days + 1))) + u' ?????? ' \
                                   + Date.to_string((contract.date_start + timedelta(
                        days=base_days + over_days - 1))) + u' ?????????? 30 ?????? ?????????? '
                    record.line_ids.create({'reconciliation_id': record.id,
                                            'amount': amount,
                                            'type': 'add',
                                            'is_manual': False,
                                            'name': detailed_log})
                log += '----------------------' + '\n'
            if record.type == 'resign':
                log += u'?????????????? ' + '\n'
                log += u'???????????? ?????????? = ' + str(round(contract.total_wage, 2)) + '\n'
                log += u'?????? ???????? ???????????? ?????? 5 ?????????? = ' + str(base_days) + '\n'
                if over_days:
                    log += u'?????? ???????? ???????????? ?????? 5 ?????????? = ' + str(over_days) + '\n'
                if base_days == 1825:
                    amount = (contract.total_wage / 30 / 365 * 10 * base_days)
                    amount = int(amount) + 1 if amount % 1 >= 0.5 else int(amount)
                    total += amount
                    log += u'???????????? ?????? 5 ?????????? (10 ???????? ??????????) = ' + str(round(amount, 2)) + '\n'
                    detailed_log = u'???????????? ?????????? ???????????? : ???? ???????????? ???? ' + Date.to_string(contract.date_start) + u' ?????? ' \
                                   + Date.to_string(
                        (contract.date_start + timedelta(days=base_days))) + u' ?????????? 10 ?????? ?????????? '
                    record.line_ids.create({'reconciliation_id': record.id,
                                            'amount': amount,
                                            'type': 'add',
                                            'is_manual': False,
                                            'name': detailed_log})
                else:
                    amount = (contract.total_wage / 30 / 365 * 5 * base_days)
                    amount = int(amount) + 1 if amount % 1 >= 0.5 else int(amount)
                    total += amount
                    log += u'???????????? ?????? 5 ?????????? (5 ???????? ??????????) = ' + str(round(amount, 2)) + '\n'
                    detailed_log = u'???????????? ?????????? ???????????? : ???? ???????????? ???? ' + Date.to_string(
                        contract.date_start) + u' ?????? ' \
                                   + Date.to_string(
                        (contract.date_start + timedelta(days=base_days))) + u' ?????????? 10 ?????? ?????????? '
                    record.line_ids.create({'reconciliation_id': record.id,
                                            'amount': amount,
                                            'type': 'add',
                                            'is_manual': False,
                                            'name': detailed_log})
                if over_days:
                    amount = (contract.total_wage / 30 / 365 * 20 * over_days)
                    amount = int(amount) + 1 if amount % 1 >= 0.5 else int(amount)
                    total += amount
                    log += u'???????????? ?????? 5 ?????????? (20 ?????? ??????????) = ' + str(round(amount, 2)) + '\n'
                    detailed_log = u'???????????? ?????????? ???????????? : ???? ???????????? ???? ' + Date.to_string((
                            contract.date_start + timedelta(days=base_days + 1))) + u' ?????? ' \
                                   + Date.to_string((contract.date_start + timedelta(
                        days=base_days + over_days - 1))) + u' ?????????? 20 ?????? ?????????? '
                    record.line_ids.create({'reconciliation_id': record.id,
                                            'amount': amount,
                                            'type': 'add',
                                            'is_manual': False,
                                            'name': detailed_log})
                log += '----------------------' + '\n'
            for line in record.line_ids:
                if line.is_manual:
                    log += line.name + ' = ' + str(round(line.amount, 2)) + '\n'
                    total = total + line.amount if line.type == 'add' else total - line.amount
            log += '----------------------' + '\n'
            log += u'???????????????? = ' + str(round(total, 2))
            record.total_amount = total
            record.total_amount_log = log

    def set_reconciled(self):
        for record in self:
            record.get_amount()
            name = '%s - %s - %s' % (
                dict(record._fields['type'].selection).get(record.type), record.employee_id.name or '', format_date(
                    self.env, record.date, date_format="MMMM y"))
            record.payslip_id = self.env['hr.payslip'].sudo().create({'employee_id': record.employee_id.id,
                                                                      'date_from': record.date,
                                                                      'date_to': record.date,
                                                                      'is_reconcile': True,
                                                                      'total_reconcile_amount': record.total_amount,
                                                                      'contract_id': record.employee_id.contract_id.id,
                                                                      # 'struct_id': record.employee_id.contract_id.structure_type_id.id,
                                                                      'name': name})
            record.payslip_id.sudo().compute_sheet()
            for line in record.line_ids:
                if line.working_line_id and line.working_line_id.state != 'paid':
                    line.working_line_id.write({'state': 'paid'})
            record.sudo().write({'state': 'reconciled'})

    def open_payslip(self):
        return {
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'hr.payslip',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.payslip_id.id,
        }

    def unlink(self):
        for record in self:
            if record.state == 'reconciled':
                raise ValidationError('You cannot remove a reconciled record!')
            else:
                return super(HrReconciliation, record).unlink()

    def convert_to_letters(self, n, currency, feminine=1):
        cur_text_EGP = '???????? ???????? ??'
        cur_text_USD = '?????????? ???????????? ??'
        cur_text_EUR = '???????? ??'
        cur_text_SAR = '???????? ?????????? ??'
        cur_text_EGP_S = '?????? ?????? ???? ??????'
        cur_text_USD_S = '?????? ?????? ???? ??????'
        cur_text_EUR_S = '?????? ?????? ???? ??????'
        cur_text_SAR_S = '???????? ?????? ???? ??????'
        cur_text_EGP_A = '???????? ???????? ?????? ???? ??????'
        cur_text_USD_A = '?????????? ???????????? ?????? ???? ??????'
        cur_text_EUR_A = '???????? ?????? ???? ??????'
        cur_text_SAR_A = '???????? ?????????? ?????? ???? ??????'

        space = ' '
        n = float(n)
        if int(n) == n:
            n = int(n)
        an = ArNumbers()
        an.setFeminine(feminine)
        res_string = an.int2str(str(n))
        # res_string = res.encode("utf-8")
        if currency:
            if currency == 'EGP':
                if res_string.find("??????????") > 0:
                    res_string = res_string.replace("??????????", cur_text_EGP)
                    res_string = res_string + space + cur_text_EGP_S
                else:
                    res_string = res_string + space + cur_text_EGP_A
            elif currency == 'USD':
                if res_string.find("??????????") > 0:
                    res_string = res_string.replace("??????????", cur_text_USD)
                    res_string = res_string + space + cur_text_USD_S
                else:
                    res_string = res_string + space + cur_text_USD_A
            elif currency == 'EUR':
                if res_string.find("??????????") > 0:
                    res_string = res_string.replace("??????????", cur_text_EUR)
                    res_string = res_string + space + cur_text_EUR_S
                else:
                    res_string = res_string + space + cur_text_EUR_A
            elif currency == 'SAR':
                if res_string.find("??????????") > 0:
                    res_string = res_string.replace("??????????", cur_text_SAR)
                    res_string = res_string + space + cur_text_SAR_S
                else:
                    res_string = res_string + space + cur_text_SAR_A
        return res_string


class HrReconciliationLine(models.Model):
    _name = 'hr.reconciliation.line'
    _description = "HR Reconciliation Line"

    reconciliation_id = fields.Many2one(string='Reconciliation', comodel_name='hr.reconciliation', required=True,
                                        ondelete='cascade')
    name = fields.Char(string='Description', required=True)
    type = fields.Selection(string='Type', selection=[('add', 'Earning'),
                                                      ('sub', 'Deduction')], required=True, default='add')
    is_manual = fields.Boolean(string='Provided by user?', default=True)
    amount = fields.Float(string='Amount', default=0)
    working_line_id = fields.Many2one(string='Working lines', comodel_name='hr.employee.working')


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    is_reconcile = fields.Boolean(string='Is a Reconciliation', default=False)
    total_reconcile_amount = fields.Float(string='Reconciliation Amount')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_reconcile_ids = fields.One2many(string='Reconciliations', comodel_name='hr.reconciliation',
                                             inverse_name='employee_id')
    reconciliations_count = fields.Integer(string='Reconciliations Count', compute='_compute_reconciliations_count')

    def _compute_reconciliations_count(self):
        for record in self:
            record.reconciliations_count = len(record.employee_reconcile_ids)
