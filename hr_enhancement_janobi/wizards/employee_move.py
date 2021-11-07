from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrEmployeeMove(models.Model):
    _name = 'hr.employee.move'
    _description = "Employee Move"

    name = fields.Char(string='Move Reference', copy=False)
    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee', required=True)
    date = fields.Date(string='Date')
    state = fields.Selection(string='State', selection=[('draft', 'Draft'),
                                                        ('approved', 'Approved')], default='draft')
    job_id = fields.Many2one(string='Job', comodel_name='hr.job')
    department_id = fields.Many2one(string='Current Department', comodel_name='hr.department')
    new_department_id = fields.Many2one(string='New Department', comodel_name='hr.department')
    project_id = fields.Many2one(string='Current Project', comodel_name='project.project')
    new_project_id = fields.Many2one(string='New Project', comodel_name='project.project')
    analytic_account_id = fields.Many2one(string='Current Cost Center', comodel_name='account.analytic.account')
    new_analytic_account_id = fields.Many2one(string='New Cost Center', comodel_name='account.analytic.account',
                                              related='new_project_id.analytic_account_id')

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def _get_job(self):
        for record in self:
            if record.employee_id and record.employee_id.job_id:
                record.job_id = record.employee_id.job_id

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def _get_department(self):
        for record in self:
            if record.employee_id and record.employee_id.department_id:
                record.department_id = record.employee_id.department_id

    @api.onchange('employee_id')
    @api.depends('employee_id')
    def _get_project(self):
        for record in self:
            if record.employee_id and record.employee_id.project_id:
                record.project_id = record.employee_id.project_id

    @api.onchange('project_id')
    @api.depends('project_id')
    def _get_analytic_account(self):
        for record in self:
            if record.project_id:
                record.analytic_account_id = record.project_id.analytic_account_id

    def set_approved(self):
        for record in self:
            record.write({'state': 'approved'})
            record.employee_id.write({'department_id': record.new_department_id.id,
                                      'project_id': record.new_project_id.id})
            if record.employee_id.contract_id:
                record.employee_id.contract_id.write({'department_id': record.new_department_id.id,
                                                      'analytic_account_id': record.new_analytic_account_id.id})

    @api.model
    def create(self, vals):
        vals.update({'name': self.env['ir.sequence'].next_by_code('employee.move.code')})
        employee_id = self.env['hr.employee'].browse(vals['employee_id'])
        if 'department_id' not in vals.keys() and employee_id.department_id:
            vals.update({'department_id': employee_id.department_id.id})
        if 'job_id' not in vals.keys() and employee_id.job_id:
            vals.update({'job_id': employee_id.job_id.id})
        if 'project_id' not in vals.keys() and employee_id.project_id:
            vals.update({'project_id': employee_id.project_id.id})
        if employee_id.project_id.analytic_account_id:
            vals.update({'analytic_account_id': employee_id.project_id.analytic_account_id.id})
        return super(HrEmployeeMove, self).create(vals)

    def unlink(self):
        for record in self:
            if record.state == 'approved':
                raise ValidationError('You cannot remove an approved move!')
            else:
                return super(HrEmployeeMove, self).unlink()


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_move_ids = fields.One2many(string='Moves', comodel_name='hr.employee.move', inverse_name='employee_id')
    moves_count = fields.Integer(string='Moves Count', compute='_compute_moves_count')

    def _compute_moves_count(self):
        for record in self:
            record.moves_count = len(record.employee_move_ids)
