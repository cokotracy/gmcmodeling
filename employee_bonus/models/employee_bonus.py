# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import time


class BonusReason(models.Model):
    _name = 'bonus.reason'
    _description = 'Bonus Reason'

    name = fields.Char(
        string="Name",
        required=True,
    )


class EmployeeBonus(models.Model):
    _name = 'employee.bonus'
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Employee Bonus'
    _rec_name = 'employee_id'
    _order = 'id desc'

    @api.onchange('employee_id')
    def get_department(self):
        for line in self:
            line.department_id = line.employee_id.department_id.id
            line.job_id = line.employee_id.job_id.id
            line.manager_id = line.employee_id.parent_id.id

    @api.model
    def get_currency(self):
        return self.env.user.company_id.currency_id

    name = fields.Char(
        string="Number",
        default='NEW',
        readonly=True,
        copy=False
    )
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        required=True,
    )
    date = fields.Date(
        'Date',
        default=fields.date.today(),
        required=True,
    )
    #     payroll_date = fields.Date(
    #         'Payroll Date',
    #     )
    job_id = fields.Many2one(
        'hr.job',
        string='Job Position',
    )
    reason_id = fields.Many2one(
        'bonus.reason',
        string='Bonus Reason',
        required=True
    )
    manager_id = fields.Many2one(
        'hr.employee',
        string='Manager',
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
    )
    bonus_amount = fields.Float(
        string='Bonus Amount',
        required=True,
    )
    #     inculde_in_payroll = fields.Boolean(
    #         string='Include In Payroll',
    #         default=True,
    #         track_visibility='onchange',
    #     )
    currency_id = fields.Many2one(
        'res.currency',
        default=get_currency,
        string='Currency',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
        readonly=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('approved_dept_manager', 'Approved by Department'),
        ('approved_hr_manager', 'Approved HR Manager'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected')], 'Status',
        readonly=True,
        tracking=True,
        default='draft',
        help="Gives the status of Employee Bonus.",
    )
    notes = fields.Text(
        'Notes',
    )
    emp_user_id = fields.Many2one(
        related='employee_id.user_id',
        store=True,
        string='Employee User',
        readonly=True
    )
    confirm_uid = fields.Many2one(
        'res.users',
        'Confirmed by',
        readonly=True
    )
    confirm_date = fields.Date(
        'Confirmed Date',
        readonly=True
    )
    approved_manager_uid = fields.Many2one(
        'res.users',
        'Approved by Manager',
        readonly=True
    )
    approved_manager_date = fields.Date(
        'Approved Manager Date',
        readonly=True
    )
    approved_date = fields.Date(
        'Approved Department Date',
        readonly=True
    )
    approved_by = fields.Many2one(
        'res.users',
        'Approved by Department',
        readonly=True
    )

    # @api.multi
    def get_confirm(self):
        self.state = 'confirm'
        self.confirm_date = time.strftime('%Y-%m-%d')
        self.confirm_uid = self.env.user.id
        if self.name == 'NEW':
            self.name = self.env['ir.sequence'].next_by_code('emp.bonus')

    # @api.multi
    def get_apprv_dept_manager(self):
        self.state = 'approved_dept_manager'
        self.approved_date = time.strftime('%Y-%m-%d')
        self.approved_by = self.env.user.id

    # @api.multi
    def get_apprv_hr_manager(self):
        self.state = 'approved_hr_manager'
        self.approved_manager_date = time.strftime('%Y-%m-%d')
        # self.payroll_date = time.strftime('%Y-%m-%d')
        self.approved_manager_uid = self.env.user.id

    # @api.multi
    def get_done(self):
        self.state = 'done'

    # @api.multi
    def get_reset(self):
        self.state = 'draft'

    # @api.multi
    def get_cancel(self):
        self.state = 'cancel'

    # @api.multi
    def get_reject(self):
        self.state = 'reject'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
