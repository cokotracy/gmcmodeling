# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError,UserError
from datetime import date, datetime
from odoo import api, fields, models, _
from odoo.osv import expression
import calendar


class HrEmployeeWorking(models.Model):
    _name = 'hr.employee.working'
    _description = "Employee Working"

    currency_id = fields.Many2one(string="Currency", related='employee_id.currency_id', readonly=True)
    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee', ondelete='cascade', required=True)
    visa_no = fields.Char(string='Visa no', required=True)
    visa_date = fields.Date(string='Visa date')
    visa_cost = fields.Monetary(string='Visa cost', compute='_get_cost')
    leave_date = fields.Date(string='Leave date')
    arrival_date = fields.Date(string='Arrival date')
    duration = fields.Integer(string='Duration', compute='_get_duration')
    work_start_date = fields.Date(string='Work Start date')
    work_end_date = fields.Date(string='Work End date')
    work_duration = fields.Integer(string='Work Duration', compute='_get_work_duration')
    notes = fields.Char(string='Notes')
    state = fields.Selection(string='State', selection=[('not', 'Not Paid'),
                                                        ('paid', 'Paid')], default='not')

    @api.depends('duration')
    @api.onchange('duration')
    def _get_cost(self):
        for record in self:
            if record.duration:
                if record.duration <= 0:
                    record.visa_cost = 0
                elif 1 <= record.duration <= 60:
                    record.visa_cost = 200
                elif 60 < record.duration <= 90:
                    record.visa_cost = 300
                elif 90 < record.duration <= 120:
                    record.visa_cost = 400
                elif 120 < record.duration <= 150:
                    record.visa_cost = 500
                elif 150 < record.duration <= 180:
                    record.visa_cost = 600
            else:
                record.visa_cost = 0

    @api.depends('leave_date', 'arrival_date')
    @api.onchange('leave_date', 'arrival_date')
    def _get_duration(self):
        for record in self:
            if record.arrival_date and record.leave_date:
                record.duration = (record.arrival_date - record.leave_date).days + 1
            else:
                record.duration = 0

    @api.depends('work_start_date', 'work_end_date')
    @api.onchange('work_start_date', 'work_end_date')
    def _get_work_duration(self):
        for record in self:
            if record.work_start_date and record.work_end_date:
                record.work_duration = (record.work_end_date - record.work_start_date).days + 1
            else:
                record.work_duration = 0

    def unlink(self):
        for record in self:
            if record.state == 'paid':
                raise ValidationError('You cannot remove a paid line!')
            else:
                return super(HrEmployeeWorking, record).unlink()


class HrEmployeeLoan(models.Model):
    _name = 'hr.employee.loan'
    _description = "Employee Loan"

    currency_id = fields.Many2one(string="Currency", related='employee_id.currency_id', readonly=True)
    employee_id = fields.Many2one(string='Employee', comodel_name='hr.employee', ondelete='cascade', required=True)
    date = fields.Date(string='Date')
    desc = fields.Char(string='Description')
    amount = fields.Monetary(string='Amount')
    install_count = fields.Integer(string='Installments Count', default=1)
    install_amount = fields.Monetary(string='Installment Amount', compute='_get_installment_amount')
    loan_document = fields.Binary(string='Loan Document')
    state = fields.Selection(string='State', selection=[('draft', 'Draft'),
                                                        ('approve', 'Approved')], default='draft')
    installment_type = fields.Selection(selection=[('manual', 'Manual'),
                                                        ('automated', 'Automated')],)
    loan_lines = fields.One2many('hr.employee.loan.lines','employee_loan_id')

    @api.depends('amount', 'install_count')
    @api.onchange('amount', 'install_count')
    def _get_installment_amount(self):
        for record in self:
            if record.amount and record.install_count:
                record.install_amount = record.amount / record.install_count
            else:
                record.install_amount = 0

    def calculate_installment(self):
        if self.amount and self.install_count >0:
            ids=[]
            for r in range(self.install_count) :
                line = {
                    'date':  (datetime.strptime(str(self.date),'%Y-%m-%d') + relativedelta(months=r)) ,
                    'amount':  self.amount/self.install_count
                    }
                loan_line = self.env['hr.employee.loan.lines'].create(line)
                ids.append(loan_line.id)
            self.loan_lines = [(6, 0, ids)]


    def set_approved(self):
        for record in self:
            record.employee_id._get_total_loans()
            record.write({'state': 'approve'})

    def unlink(self):
        for record in self:
            if record.state == 'approve':
                raise ValidationError('You cannot remove an approved loan!')
            else:
                return super(HrEmployeeLoan, record).unlink()

    @api.constrains('loan_lines')
    def check_loan_lines(self):
        for rec in self:
            total =0
            for line in rec.loan_lines :
                total += line.amount
            if rec.loan_lines:
                if total != rec.amount :
                    raise UserError('Total amount in loan lines must be = loan amount !!')




class HrEmployeeLoanLines(models.Model):
    _name = 'hr.employee.loan.lines'
    _description = "Employee Loan Lines"

    date = fields.Date()
    amount = fields.Float()
    employee_loan_id = fields.Many2one('hr.employee.loan')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)
    project_id = fields.Many2one(string='Current Project', comodel_name='project.project')
    code = fields.Char(string='Employee Reference', copy=False)
    coach_user_id = fields.Many2one(string='Coach User ID', related='coach_id.user_id')
    blood_group = fields.Char(string='Blood Group')

    # Labor Office Tab
    visa_no = fields.Char(string='Visa no')
    visa_career = fields.Char(string='Visa career')
    visa_expire_date = fields.Date(string='Visa expire date')
    visa_cost = fields.Monetary(string='Visa cost')
    date_of_arrival = fields.Date(string='Date of arrival')
    employee_labor_office_number = fields.Char(string='Employee no in labor office')
    company_labor_office_number = fields.Char(string='Company no in labor office')
    company_name = fields.Many2one(string='Company Name', comodel_name='res.company')
    boundary_number = fields.Char(string='Boundary number')
    port_of_entry = fields.Selection(selection=[('jouf', 'Jouf Regional Airport'),
                                                ('arar', 'Arar Domestic Airport'),
                                                ('nayef', 'Prince Nayef bin Abdul Aziz International Airport'),
                                                ('abdullah', 'King Abdullah International Airport'),
                                                ('sultan', 'Prince Sultan Bin Abdulaziz Regional Airport'),
                                                ('abdulaziz', 'King Abdulaziz International Airport'),
                                                ('gurayat', 'Gurayat Domestic Airport'),
                                                ('khaled', 'King Khaled International Airport'),
                                                ('duba', 'Port of Duba'),
                                                ('jeddah', 'Jeddah Islamic Port'),
                                                ('yanbu', 'Yanbu Commercial Port')])

    # Social Insurance Tab
    employee_social_insurance_number = fields.Char(string='Employee social insurance number')
    company_social_insurance_number = fields.Char(string='Company social insurance number')
    social_insurance_pay = fields.Monetary(string='Insurance payment')
    social_insurance_min_pay = fields.Monetary(string='Insurance minimum payment')
    social_insurance_enroll_date = fields.Date(string='Enroll date')

    # Medical Insurance Tab
    medical_policy_number = fields.Char(string='Policy number')
    age = fields.Integer(string='Age', readonly=True, compute='_compute_age')
    medical_start_date = fields.Date(string='Medical Start date')
    medical_end_date = fields.Date(string='Medical End date')
    annual_medical_pay = fields.Monetary(string='Annual payment')
    monthly_medical_pay = fields.Monetary(string='Monthly payment')
    medical_card_document = fields.Binary(string='Employee medical card')

    # Residence Tab
    residency_number = fields.Char(string='Residency number')
    residency_issue_place = fields.Char(string='Residency issue place')
    residency_issue_date = fields.Date(string='Residency issue date')
    residency_end_date = fields.Date(string='Residency end date')
    passport_number = fields.Char(string='Passport number')
    passport_issue_place = fields.Char(string='Passport issue place')
    passport_issue_date = fields.Date(string='Passport issue date')
    passport_end_date = fields.Date(string='Passport end date')
    labor_license_cost = fields.Monetary(string='Labor license cost')
    passport_fees = fields.Monetary(string='Passport fees')
    residency_cost = fields.Monetary(string='Residency cost', readonly=True, compute='_compute_residency_cost')
    residency_total_cost = fields.Monetary(string='Residency total cost', readonly=True,
                                           compute='_compute_residency_cost')
    residency_deduction_type = fields.Selection([('500','اول مره'),('1000','متكرر')],string='Residency deductions')
    @api.onchange('residency_deduction_type')
    def set_ded_res(self):
        if self.residency_deduction_type == '500':
            self.residency_deduction = 500
        if self.residency_deduction_type == '1000':
            self.residency_deduction = 1000
    residency_deduction = fields.Monetary(string='Residency deductions')
    sponsorship_transfer = fields.Boolean('Sponsorship transfer', default=False)
    sponsor_name = fields.Char(string='Sponsor')
    residency_document = fields.Binary(string='Residency card')

    # Syndicate Tab
    syndicate_name = fields.Selection(string='Syndicate', selection=[('eng', 'Engineering'),
                                                                     ('comm', 'Commercial Professions'),
                                                                     ('work', 'Workers'),
                                                                     ('drive', 'Drivers'),
                                                                     ('sci', 'Scientists'),
                                                                     ('law', 'Lawyers'),
                                                                     ('doc', 'Doctors')])
    syndicate_category = fields.Char(string='Category')
    syndicate_membership_id = fields.Char(string='Syndicate Membership number')
    syndicate_membership_start_date = fields.Date(string='Syndicate Membership start date')
    syndicate_membership_end_date = fields.Date(string='Syndicate Membership end date')
    syndicate_card = fields.Binary(string='Syndicate card')

    # WPS Tab
    employee_wps_number = fields.Char(string='Employee WPS number')
    main_bank_account = fields.Char(string='Bank account')
    main_transferred_amount = fields.Monetary(string='Transferred amount')
    main_bank_commission = fields.Monetary(string='Bank commission')
    sub_bank_account = fields.Char(string='Bank account')
    sub_transferred_amount = fields.Monetary(string='Transferred amount')
    sub_bank_commission = fields.Monetary(string='Bank commission')

    # Driving Tab
    driving_license_number = fields.Char(string='License number')
    driving_license_origin = fields.Selection(string='License origin', selection=[('eg', 'Egyptian'),
                                                                                  ('sa', 'Saudi'),
                                                                                  ('pk', 'Pakistani'),
                                                                                  ('ind', 'Indian'),
                                                                                  ('other', 'Other')])
    driving_license_type = fields.Selection(string='License type', selection=[('personal', 'Personal'),
                                                                              ('light', 'Light Transportation'),
                                                                              ('heavy', 'heavy Transportation'),
                                                                              ('machine', 'Machine'),
                                                                              ('other', 'Other')])
    driving_license_end_date = fields.Date(string='License End date')
    car_type = fields.Char(string='Car or machine type')
    driving_license_card = fields.Binary(string='License card')

    # Working Tab
    working_line_ids_edit = fields.Boolean(compute="_compute_working_line_ids_edit")
    def _compute_working_line_ids_edit(self):
        for this in self:
            if this.contract_id:
                now = datetime.now().date()
                date_start = this.contract_id.date_start
                delta = now - date_start
                if delta.days > 365:
                    this.working_line_ids_edit = True
                elif len(self.env['approval.request'].search([('is_disclaimer','=',True),('employee_id','=',this.id),('request_status','=','approved')])) > 0:
                    this.working_line_ids_edit = True
                else:
                    this.working_line_ids_edit = False
            else:
                this.working_line_ids_edit = False
    working_line_ids = fields.One2many(string='Working lines', comodel_name='hr.employee.working',
                                       inverse_name='employee_id')

    # Loans Tab
    loan_ids = fields.One2many(string='Loans', comodel_name='hr.employee.loan', inverse_name='employee_id', )
    loans_total = fields.Float(string='Total Remaining Loans', compute='get_loans_installment')

    @api.model
    def create(self, vals):
        vals.update({'code': self.env['ir.sequence'].next_by_code('employee.code')})
        address_home_id = self.env['res.partner'].create({
        'name':vals['name'],
        })
        vals['address_home_id'] = address_home_id.id
        return super(HrEmployee, self).create(vals)

    def name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                display_name = record.name + ' [' + record.code + ']'
                result.append((record.id, display_name))
            if not record.code:
                display_name = record.name + ' []'
                result.append((record.id, display_name))
        return result

    # @api.model
    # def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
    #     args = args or []
    #     domain = []
    #     if name:
    #         domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
    #         if operator in expression.NEGATIVE_TERM_OPERATORS:
    #             domain = ['&'] + domain
    #     employee_ids = self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
    #     return models.lazy_name_get(self.browse(employee_ids).with_user(name_get_uid))

    @api.depends('birthday')
    def _compute_age(self):
        for record in self:
            if record.birthday:
                record.age = relativedelta(date.today(), record.birthday).years
            else:
                record.age = 0

    @api.depends('labor_license_cost', 'passport_fees', 'residency_deduction')
    def _compute_residency_cost(self):
        for record in self:
            record.residency_cost = record.passport_fees
            record.residency_total_cost = record.labor_license_cost + record.passport_fees + record.residency_deduction

    @api.depends('loan_ids')
    @api.onchange('loan_ids')
    def _get_total_loans(self):
        for record in self:
            total_loans = 0
            for loan in record.loan_ids:
                month_difference = relativedelta(date.today(), loan.date.replace(day=1)).months
                if month_difference < loan.install_count and date.today() >= loan.date and loan.state == 'approve':
                    total_loans += (loan.install_count - month_difference) * loan.install_amount
            record.loans_total = total_loans

    @api.depends('name')
    def get_loans_installment(self):
        for rec in self:
            rec.loans_total = False
            loans = self.env['employee.loan'].sudo().search([('employee_id', '=', rec.name),
                                                             ('state', '=', 'done'), ], )
            total_installment_paid = 0
            total_installment_not_paid = 0
            for loan in loans:
                for line in loan.installment_lines:
                    if line.is_paid:
                        total_installment_paid += line.total_installment
                    else:
                        total_installment_not_paid += line.total_installment
                rec.loans_total = total_installment_not_paid

    # To be called from the Loans salary rule code
    def _get_loans_installment(self, date):
        self.ensure_one()
        total_install = 0
        for loan in self.loan_ids:
            month_difference = relativedelta(date, loan.date.replace(day=1)).months
            if month_difference < loan.install_count and date >= loan.date:
                total_install += loan.install_amount
        return total_install

    def _get_work_days_count(self, date_from, date_to):
        self.ensure_one()
        date_from = datetime.combine(date_from, datetime.min.time())
        date_to = datetime.combine(date_to, datetime.max.time())
        return self.env['hr.work.entry'].search_count(
            [('employee_id', '=', self.id), ('work_entry_type_id.code', '=', 'WORK100'),
             ('date_start', '>=', date_from), ('date_start', '<=', date_to)])

    _sql_constraints = [
        ('_unique_employee_name', 'unique (name)', 'Employee name already exist.'),
        ('_unique_employee_email', 'unique (work_email)', 'Employee e-mail already exist.'),
    ]

    approver_lines = fields.One2many('approval.approver.employee','employee_id')


class ApprovalApproverEmployee(models.Model):
    _name = 'approval.approver.employee'
    _description = 'Approver'

    user_id = fields.Many2one('res.users', string="User")
    status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], string="Status", default="new", readonly=True)

    date = fields.Date('Date')
    employee_id  = fields.Many2one('hr.employee')