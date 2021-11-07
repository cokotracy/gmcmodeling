from odoo import fields, models, api, SUPERUSER_ID



class ProjectTender(models.Model):
    _name = "project.tender"

    name = fields.Text(required=True, copy=True, string='Work Item')
    code = fields.Char(copy=True, string='Code', )
    project_id = fields.Many2one('project.project', string='Project', required=True)
    tender_qty = fields.Float(string='Tender Qty')
    uom_id = fields.Many2one(comodel_name="uom.uom", string="Uom", required=False, )
    tender_rate = fields.Integer(string='Tender Rate')
    item_type = fields.Selection(selection=[('view', 'view'), ('transaction', 'transaction'), ], string="Type",
                                 required=True, )
    job_cost_id = fields.One2many('job.costing', 'tender_id', )
    job_cost_total = fields.Float(string='Breakdown Cost', compute='get_total_cost')
    customer_cost = fields.Float(string='Final Cost')
    related_product = fields.Many2one(comodel_name="product.product", string="Product", required=False)
    project_profit = fields.Float(string='Over head & Profit %')
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount')
    total_amount_unit = fields.Float(string='Unit Final', compute='_compute_total_amount')
    task_id = fields.One2many('project.task', 'tender_id', ondelete="cascade")
    related_task_id = fields.Many2one('project.task', string='Related Job order', required=False)
    discount = fields.Float(string="Discount %", required=False)
    total_amount_unit_before_discount = fields.Float(string="Total Before Discount",
                                                     compute='get_total_amount_unit_before_discount', required=False)
    lump_sum_qty = fields.Integer(string='DWG')

    @api.depends('project_profit', 'job_cost_total', 'customer_cost', 'tender_qty', 'lump_sum_qty')
    def get_total_amount_unit_before_discount(self):
        for rec in self:
            rec.total_amount_unit_before_discount = 0.0
            if rec.lump_sum_qty != 0:
                if not rec.customer_cost:
                    rec.total_amount = (rec.lump_sum_qty * (rec.job_cost_total)) + (rec.lump_sum_qty * (
                                            rec.job_cost_total) * rec.project_profit / 100)

                else:
                    rec.total_amount = (rec.lump_sum_qty * (rec.customer_cost)) + (rec.lump_sum_qty * (
                                        rec.customer_cost) * rec.project_profit / 100)
            else:
                rec.total_amount = (rec.tender_qty * (
                    rec.job_cost_total if not rec.customer_cost else rec.customer_cost)) + (
                                           rec.tender_qty * (
                                       rec.job_cost_total if not rec.customer_cost else rec.customer_cost) * rec.project_profit / 100)
            if rec.tender_qty > 0.0:
                if rec.lump_sum_qty != 0:
                    rec.total_amount_unit_before_discount = rec.total_amount / rec.lump_sum_qty
                else:
                    rec.total_amount_unit_before_discount = rec.total_amount / rec.tender_qty
            else:
                rec.total_amount_unit_before_discount = rec.total_amount

    @api.depends('job_cost_id')
    def get_total_cost(self):
        for rec in self:
            rec.job_cost_total = 0
            if rec.job_cost_id and rec.job_cost_id.tender_qty > 0:

                rec.job_cost_total = rec.job_cost_id.jobcost_total / rec.job_cost_id.tender_qty
            else:
                rec.job_cost_total = 0

    @api.depends('lump_sum_qty', 'project_profit', 'job_cost_total', 'customer_cost', 'tender_qty', 'project_profit',
                 'discount')
    def _compute_total_amount(self):
        for rec in self:
            if rec.lump_sum_qty != 0:
                if not rec.customer_cost:
                    profit = rec.lump_sum_qty * (
                        rec.job_cost_total) * rec.project_profit / 100
                    rec.total_amount = (rec.lump_sum_qty * (
                        rec.job_cost_total)) + profit
                else:
                    profit = rec.lump_sum_qty * (
                        rec.customer_cost) * rec.project_profit / 100
                    rec.total_amount = (rec.lump_sum_qty * (
                        rec.customer_cost)) + profit
                if rec.lump_sum_qty > 0.0:
                    rec.total_amount_unit = rec.total_amount / rec.lump_sum_qty
                    if 0 < rec.discount < 100:
                        rec.total_amount_unit -= (rec.total_amount_unit * rec.discount / 100)
                else:
                    rec.total_amount_unit = rec.total_amount
                    if 0 < rec.discount < 100:
                        rec.total_amount_unit -= rec.total_amount_unit * rec.discount / 100
            else:
                rec.total_amount = (rec.tender_qty * (
                    rec.job_cost_total if not rec.customer_cost else rec.customer_cost)) + (
                                           rec.tender_qty * (
                                       rec.job_cost_total if not rec.customer_cost else rec.customer_cost) * rec.project_profit / 100)

                if rec.tender_qty > 0.0:
                    rec.total_amount_unit = rec.total_amount / rec.tender_qty
                    if 0 < rec.discount < 100:
                        rec.total_amount_unit -= rec.total_amount_unit * rec.discount / 100
                else:
                    rec.total_amount_unit = rec.total_amount
                    if 0 < rec.discount < 100:
                        rec.total_amount_unit -= rec.total_amount_unit * rec.discount / 100

                rec.total_amount = rec.tender_qty * rec.total_amount_unit

    @api.model
    def create(self, vals):
        if vals['item_type'] != 'view':
            project_id = self.env['project.project'].search([('id', '=', vals['project_id'])])
            if project_id:
                vals['job_cost_id'] = self.env['job.costing'].create({'name': vals['name'],
                                                                      'analytic_id': project_id.analytic_account_id.id,

                                                                      'project_id': vals['project_id'],
                                                                      })
        else:
            vals['task_id'] = self.env['project.task'].create({'name': vals['name'],
                                                               'project_id': vals['project_id'],
                                                               })
        return super(ProjectTender, self).create(vals)



class KeyPersonnel(models.Model):
    _name = 'key.personnel'

    position_id = fields.Many2one(comodel_name="hr.job", string="Position", required=False, )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee Name", required=False, )
    mobile = fields.Char(string="Mobile", required=False, )
    email_id = fields.Char(string="Email ID", required=False, )
    project_id = fields.Many2one(comodel_name="project.project", string="", required=False, )


class Project(models.Model):
    _inherit = "project.project"

    def update_tender_profit(self):
        for rec in self:
            for tender in rec.project_tender_ids:
                tender.write({'project_profit': self.profit_per})

    def update_tender_discount(self):
        for rec in self:
            for tender in rec.project_tender_ids:
                tender.write({'discount': self.discount})

    def _compute_jobcost_count(self):
        jobcost = self.env['job.costing']
        job_cost_ids = self.mapped('job_cost_ids')
        for project in self:
            project.job_cost_count = jobcost.search_count([('id', 'in', job_cost_ids.ids)])

    job_cost_count = fields.Integer(compute='_compute_jobcost_count')
    job_cost_ids = fields.One2many('job.costing', 'project_id', )
    project_tender_ids = fields.One2many('project.tender', 'project_id', copy=True)
    profit_per = fields.Float(string='Over head & Profit %')
    discount = fields.Float(string='Discount %')

    job_order_no = fields.Char(string="Job Order No", required=False, )
    project_ID = fields.Char(string="Project ID", required=False, )
    client_name = fields.Char(string="Client Name", required=False, related='partner_id.name')
    client_manager = fields.Char(string="Client Manager", required=False, )
    entry_date = fields.Datetime(string="Entry Date", required=False, default=fields.Datetime.now)
    location = fields.Char(string="Location", required=False, )
    po_number = fields.Char(string="PO Number", required=False, )
    po_date = fields.Datetime(string="Po Date", required=False, default=fields.Datetime.now)
    start_date = fields.Date(string="Start Date", required=False, default=fields.Date.context_today)
    hand_over_date = fields.Date(string="Hand Over Date", required=False, default=fields.Date.context_today)
    remarks = fields.Text(string="Remarks", required=False, )
    key_personnel_ids = fields.One2many(comodel_name="key.personnel", inverse_name="project_id", string="",
                                        required=False, )
    # Add by omnya
    lump_sum_project = fields.Boolean(string='LumpSum')
    assigned_to = fields.Many2one(comodel_name='res.users', string='Tasks Assigned To')

    def project_to_jobcost_action(self):
        job_cost = self.mapped('job_cost_ids')
        action = self.env.ref('odoo_job_costing_management.action_job_costing').read()[0]
        action['domain'] = [('id', 'in', job_cost.ids)]
        action['context'] = {'default_project_id': self.id, 'default_analytic_id': self.analytic_account_id.id,
                             'default_user_id': self.user_id.id}
        return action


class ProjectType(models.Model):
    _inherit = 'project.task.type'

    show_in_kanban = fields.Boolean()


class ProjectTask(models.Model):
    _inherit = 'project.task'

    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    tender_id = fields.Many2one('project.tender', string='Tender', )
    state = fields.Selection([('draft', 'Draft'), ('in_hand', 'In Hand'), ('refused', 'Refused'), ('cancel', 'Cancel')],
                             string='Status', group_expand='_expand_states', copy=False, tracking=True,
                             help='Status of the Tender', default='draft')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stages_folded = self.env['project.task.type'].search([('show_in_kanban', '=', True)])
        search_domain = [('id', 'in', stages_folded.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    def _compute_jobcost_count(self):
        jobcost = self.env['job.costing']
        job_cost_ids = self.mapped('job_cost_ids')
        for task in self:
            task.job_cost_count = jobcost.search_count([('id', 'in', job_cost_ids.ids)])

    job_cost_count = fields.Integer(compute='_compute_jobcost_count')
    job_cost_ids = fields.One2many('job.costing', 'task_id', )

    def task_to_jobcost_action(self):
        job_cost = self.mapped('job_cost_ids')
        action = self.env.ref('odoo_job_costing_management.action_job_costing').read()[0]
        action['domain'] = [('id', 'in', job_cost.ids)]
        action['context'] = {'default_task_id': self.id, 'default_project_id': self.project_id.id,
                             'default_analytic_id': self.project_id.analytic_account_id.id,
                             'default_user_id': self.user_id.id}
        return action


