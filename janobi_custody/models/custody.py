# -*- coding: utf-8 -*-
import time
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class Custody(models.Model):
    _name = 'custody.custody'
    _description = "Custody"
    _rec_name = 'name'
    _order = 'date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Custody Sequence', copy=False, readonly=1)
    employee = fields.Many2one('hr.employee', 'Employee', tracking=True, required='1', readonly=True,
                               states={'new': [('readonly', False)]})

    color = fields.Integer('Color Index', default=0)
    employee_user_id = fields.Many2one(string='Employee User', related="employee.user_id")
    department = fields.Many2one('hr.department', 'Department', related="employee.department_id")
    date = fields.Datetime('Date', default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S', ),
                           tracking=True, readonly=True)
    approve_date = fields.Datetime('Approve Date',
                                   states={'approve': [('readonly', '1')]}, tracking=True)
    reject_date = fields.Datetime('Reject Date',
                                  states={'reject': [('readonly', '1')]}, tracking=True)
    line_ids = fields.One2many(comodel_name="custody.line", inverse_name="custody", required=False, string='Lines',
                               tracking=True)
    state = fields.Selection(selection=[('new', 'New'), ('locked', 'Locked'), ('progress', 'In Progress'),
                                        ('manager', 'Direct Manager Approved'), ('accountant', 'Accountant Approved'),
                                        ('direct_manager_reject', 'Direct Manager Rejected'),
                                        ('accountant_reject', 'Accountant Rejected'),
                                        ('approve', 'Approved'), ('reject', 'Rejected')], tracking=True,
                             default='new')
    old_custody_value = fields.Float('Old Custody Value', readonly=True, tracking=True)
    custody_value = fields.Float('Custody Value', readonly=True, states={'new': [('readonly', False)]}, tracking=True)
    paid_value = fields.Float('Paid Value', compute='get_paid', tracking=True)
    approved_custody_value = fields.Float('Approved Custody Value', tracking=True, readonly=True)
    rejected_custody_value = fields.Float('Rejected Custody Value', readonly=True, tracking=True)
    balance = fields.Float('Balance', readonly=True)
    bio = fields.Text('Bio', tracking=True, readonly=True, states={'new': [('readonly', False)],
                                                                   'progress': [('readonly', False)], })
    bank_account = fields.Char('Bank Account', readonly=True, tracking=True, states={'new': [('readonly', False)],
                                                                                     'progress': [
                                                                                         ('readonly', False)], })

    _sql_constraints = [
        ('check_custody_value', 'CHECK(custody_value >= 0)',
         'The Value Cannot be negative!'),
        ('check_custody_name', 'unique(name)',
         'Custody number already existed!'),
    ]

    @api.model
    def create(self, vals):
        vals.update({'name': self.env['ir.sequence'].next_by_code('custody.code')})
        employee = self.env['hr.employee'].search([('id', '=', vals['employee'])])
        vals.update({'old_custody_value': employee.custody_value})
        return super(Custody, self).create(vals)

    @api.onchange("line_ids")
    def get_paid(self):
        for one in self:
            one.paid_value = 0
            if one.line_ids:
                for line in one.line_ids:
                    one.paid_value += line.value

    @api.onchange("employee")
    def set_old_custody_value(self):
        if self.state == 'new':
            self.old_custody_value = self.employee.custody_value

    def check_date(self):
        for custody in self.env['custody.custody'].search([]):
            delta = datetime.now() - custody.date
            if custody.state == 'progress' and delta.days >= 7:
                custody.action_lock()

    def action_progress(self):
        self.employee.custody_value += self.custody_value
        self.state = 'progress'
        if self.employee.department_id:
            if self.employee.department_id.manager_id:
                self.env['mail.activity'].create({
                    'res_id': self.id,
                    'res_model_id': self.env['ir.model']._get('custody.custody').id,
                    'activity_type_id': 6,
                    'summary': 'Important!!',
                    'note': "Custody is Created For employee %s.!" % (self.employee.name),
                    'user_id': self.employee.department_id.manager_id.user_id.id,
                })

    def action_lock(self):
        self.state = 'locked'

    def action_direct_manager_reject(self):
        self.state = 'direct_manager_reject'

    def action_accountant_reject(self):
        self.state = 'accountant_reject'

    def action_reject(self):
        self.rejected_custody_value = self.paid_value
        self.balance = self.old_custody_value + self.custody_value
        self.employee.custody_value = self.balance
        self.reject_date = datetime.now()
        self.state = 'reject'

    def action_direct_manager(self):
        self.ensure_one()
        approved_lines_value = 0

        for line in self.line_ids:
            if line.approve:
                approved_lines_value += line.value
        if approved_lines_value > 0:
            self.approved_custody_value = approved_lines_value
            self.balance = self.old_custody_value + self.custody_value - self.approved_custody_value
            self.rejected_custody_value = self.paid_value - self.approved_custody_value
            if self.rejected_custody_value < 0:
                self.rejected_custody_value = 0
            self.state = 'manager'
            if self.employee.company_id.financial_manager:
                self.env['mail.activity'].create({
                    'res_id': self.id,
                    'res_model_id': self.env['ir.model']._get('custody.custody').id,
                    'activity_type_id': 6,
                    'summary': 'Important!!',
                    'note': "Custody is approved by direct manager.!",
                    'user_id': self.employee.company_id.financial_manager.id,
                })
        else:
            raise UserError("You should select lines to approve")

    def action_accountant(self):
        self.ensure_one()
        approved_lines_value = 0

        for line in self.line_ids:
            if line.approve:
                approved_lines_value += line.value
        if approved_lines_value > 0:
            self.approved_custody_value = approved_lines_value
            self.balance = self.old_custody_value + self.custody_value - self.approved_custody_value
            self.rejected_custody_value = self.paid_value - self.approved_custody_value
            if self.rejected_custody_value < 0:
                self.rejected_custody_value = 0
            self.state = 'accountant'
        else:
            raise UserError("You should select lines to approve")

    def action_approve(self):
        self.ensure_one()
        approved_lines_value = 0

        for line in self.line_ids:
            if line.approve:
                approved_lines_value += line.value
        if approved_lines_value > 0:
            self.approved_custody_value = approved_lines_value
            self.balance = self.old_custody_value + self.custody_value - self.approved_custody_value
            self.rejected_custody_value = self.paid_value - self.approved_custody_value
            if self.rejected_custody_value < 0:
                self.rejected_custody_value = 0
            self.employee.custody_value = self.balance
            self.approve_date = datetime.now()
            self.state = 'approve'
        else:
            raise UserError("You should select lines to approve")


class CustodyLines(models.Model):
    _name = 'custody.line'
    _rec_name = 'description'

    custody = fields.Many2one(comodel_name="custody.custody", string="Custody", required=False, ondelete='cascade')
    custody_state = fields.Selection(related='custody.state', store=1)
    date = fields.Datetime('Date', default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S', ))
    employee = fields.Many2one(related='custody.employee', store=1)
    department = fields.Many2one(related='custody.department', store=1)
    description = fields.Char('Description', required=True)
    value = fields.Float('Value', required=True)
    attachment = fields.Binary('Attachment',store=True)
    attachment2 = fields.Binary('PDF')
    attachment3 = fields.Binary('Image')
    partner_id = fields.Many2one('res.partner', string='Customer')
    asset_id = fields.Many2one('account.asset', string='Asset')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    approve = fields.Boolean('Approve', default=False)

    _sql_constraints = [
        ('check_value', 'CHECK(value > 0)',
         'The Value Cannot be negative!')
    ]

    @api.model
    def create(self, vals):
        vals['attachment2'] = vals['attachment']
        vals['attachment3'] = vals['attachment']
        return super(CustodyLines, self).create(vals)

    @api.model
    def fix_old_lines(self):
        for line in self:
            self.attachment2 = self.attachment
            self.attachment3 = self.attachment
