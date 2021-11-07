from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class Project(models.Model):
    _inherit = "project.project"

    def get_default_team(self):
        team = self.env['crm.team'].search([('has_team_tender', '=', True)]).id
        return team

    project_no = fields.Char('Project Number')
    project_start_date = fields.Date(string='Project Beginning')
    project_end_date = fields.Date(sting='Project End')
    project_period = fields.Float(sting='Project Period', compute="_get_project_period", store=True)
    validity_date = fields.Date('Validity date')
    invitation_date = fields.Date('invitation date')
    tender_team_ids = fields.Many2many('res.users', string='Tender Persons')
    tender_team_id = fields.Many2one('crm.team', string='Tender Team',
                                     default=lambda self: self.get_default_team())
    state = fields.Selection(
        [('draft', 'Draft'), ('in_progress', 'In Progress'), ('in_hand', 'In Hand'), ('refused', 'Refused'), ],
        string='Status', group_expand='_expand_states', copy=False, tracking=True,
        help='Status of the Tender', default='draft')
    task_count = fields.Integer(string="Job order Count")
    task_ids = fields.One2many(string='Job orders')
    label_tasks = fields.Char(string='Use Job orders as', default='Tasks',
                              help="Label used for the Job orders of the project.", translate=True)

    stock_location_id = fields.Many2one(comodel_name="stock.location", string="Stock Location", required=False, )
    sent = fields.Many2many('res.users', 'user_project_changes_rel', 'project_changes_id', 'sent_id')

    # new date fields..
    submission_date = fields.Date('Tender Submission Date')
    contract_date = fields.Date('Contract Date')
    location_acquisition_date = fields.Date('Location Acquisition Date')
    primary_delivery_date = fields.Date('Primary Delivery Date', compute='get_delivery_date')
    maintenance_duration = fields.Integer('Maintenance Duration')
    final_delivery = fields.Date('Final Delivery Date', compute='get_final_date')
    project_dates_ids = fields.One2many(comodel_name='project.dates', inverse_name='project_id')
    client_specialist_id = fields.Many2one(comodel_name='res.partner', string="Attention", required=False,
                                           tracking=True)
    # client_name = fields.Char(string="Client Name", required=False, related='partner_id.name')
    client_manager = fields.Char(string="Client Manager", required=False, related='client_specialist_id.name')
    # location_id = fields.Char(string='Location', required=True)


    @api.onchange('project_no')
    def onchange_project_no(self):
        for project in self:
            if project.project_no:
                project.job_order_no = project.project_no
                project.project_ID = project.project_no

    @api.onchange('location_id')
    def onchange_location_id(self):
        for project in self:
            if project.location_id:
                project.location = project.location_id

    @api.onchange('project_start_date')
    def onchange_project_start_date(self):
        for project in self:
            if project.project_start_date:
                project.start_date = project.project_start_date

    @api.onchange('final_delivery')
    def onchange_final_delivery(self):
        for project in self:
            if project.final_delivery:
                project.hand_over_date = project.final_delivery

    @api.depends('project_start_date', 'project_end_date')
    def _get_project_period(self):
        if self.project_end_date and self.project_start_date:
            d1 = datetime.strptime(str(self.project_start_date), "%Y-%m-%d")
            d2 = datetime.strptime(str(self.project_end_date), "%Y-%m-%d")
            self.project_period = (abs((d2 - d1).days))
        else:
            self.project_period = 0

    def get_delivery_date(self):
        for item in self:
            item.primary_delivery_date = False
            if item.project_start_date and item.project_period:
                date_1 = datetime.strptime(str(item.project_start_date), "%Y-%m-%d")
                item.primary_delivery_date = date_1 + timedelta(days=int(item.project_period))

    def get_final_date(self):
        for item in self:
            item.final_delivery = False
            if item.primary_delivery_date and item.maintenance_duration:
                date_1 = datetime.strptime(str(item.primary_delivery_date), "%Y-%m-%d")
                item.final_delivery = date_1 + timedelta(days=int(item.maintenance_duration))

    def _get_report_base_filename(self):
        self.ensure_one()
        return 'Project-%s' % (self.name)

    @api.model
    def create(self, vals_list):
        if vals_list.get('project_no'):
            vals_list.update({'job_order_no': vals_list.get('project_no'), 'project_ID': vals_list.get('project_no')})
        if vals_list.get('location_id'):
            vals_list.update({'location': vals_list.get('location_id')})
        if vals_list.get('project_start_date'):
            vals_list.update({'start_date': vals_list.get('project_start_date')})
        if vals_list.get('final_delivery'):
            vals_list.update({'hand_over_date': vals_list.get('final_delivery')})
        res = super(Project, self).create(vals_list)
        # prev_projects_num = []
        # for rec in self.env['project.project'].search([]).mapped('project_no'):
        #     if rec:
        #         prev_projects_num.append(int(rec))
        if res.tender_team_id:
            res.tender_team_ids = [(6, 0, res.tender_team_id.member_ids.ids)]
            notification_ids = []
            for person in res.tender_team_ids:
                notification_ids.append((0, 0, {
                    'res_partner_id': person.partner_id.id,
                    'notification_type': 'inbox'}))

            res.sent = [(6, 0, res.tender_team_ids.ids)]
            res.send_notification(notification_ids)

        # res.project_no = max(prev_projects_num) + 1 if prev_projects_num else 1
        return res

    def send_notification(self, ids):
        if ids:
            self.message_post(body='This project has been created!', message_type='notification',
                              author_id=self.env.user.partner_id.id, notification_ids=ids)

    def write(self, vals):
        res = super(Project, self).write(vals)
        team = self.env['crm.team'].search([('has_team_tender', '=', True)])
        for rec in self:
            if not rec.tender_team_id and team:
                rec.tender_team_id = team.id
                rec.tender_team_ids = [(6, 0, team.member_ids.ids)]

        notification_ids = []
        for person in self.tender_team_ids:
            if person.id in self.sent.ids:
                pass
            else:
                notification_ids.append((0, 0, {
                    'res_partner_id': person.partner_id.id,
                    'notification_type': 'inbox'}))
                old = self.sent.ids
                old.append(person.id)
                self.sent = [(6, 0, old)]
        self.send_notification(notification_ids)

        return res

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    def project_in_progress(self):
        self.state = 'in_progress'

    def update_tender(self):
        length = len(self.project_tender_ids.filtered(lambda x: x.item_type == 'view'))

        project_tasks = self.env['project.task'].search([('project_id', '=', self.id)]).sorted(lambda x: x.id)[:length]

        procurment_list = self.env['procurment.list'].search([('name', '=', self.id)])
        procurment_list_lines = self.env['procurment.list.lines'].search([('procurment_id', '=', procurment_list.id)])

        list = []
        for task_id in project_tasks:
            for cost_id in task_id.job_cost_ids:
                for p_line in procurment_list_lines:
                    if cost_id.name == p_line.name:
                        child = p_line.sequance + 50
                        for product in cost_id.job_cost_line_ids:
                            if product.product_id.type == 'product':
                                # procurment_list_lines = self.env['procurment.list.lines'].search([('procurment_id','=',procurment_list.id),('product','=',product.id)])
                                found_in = procurment_list_lines.filtered(lambda
                                                                              x: x.product.id == product.product_id.id and x.sequance > p_line.sequance and x.sequance < p_line.sequance + 100)
                                if len(found_in) == 0:
                                    # // check if there is an duplicate search on procurment_list_lines for the line
                                    dic = {'sequance': child,
                                           'job_cost_line_id': product.id,
                                           'project_id': self.id, 'job_id': task_id.id, 'cost_id': cost_id.id,
                                           'work_item_code': '',
                                           'name': '', 'item_type': '',
                                           'product_code': 'Material', 'product': product.product_id.id, 'vendor': '',
                                           'code': '',
                                           'send_to_pr': False, 'send_to_po': False, 'procurment_id': '',
                                           'action_line': 0,
                                           'planned_qty': product.product_qty, 'cost_price': product.cost_price,
                                           'uom_id': product.uom_id.id,
                                           'qty_actually': '',
                                           'job_type_id': product.job_type_id.id}
                                    # pll = pll.create(dic)
                                    list.append((0, 0, dic))
                                    child += 1

                        for product in cost_id.subcontractor_line_ids:
                            if product.product_id.type == 'product':
                                # procurment_list_lines = self.env['procurment.list.lines'].search([('procurment_id','=',procurment_list.id),('product','=',product.id)])
                                found_in = procurment_list_lines.filtered(lambda
                                                                              x: x.product.id == product.product_id.id and x.sequance > p_line.sequance and x.sequance < p_line.sequance + 100)
                                if len(found_in) == 0:
                                    dic = {'sequance': child,
                                           'job_cost_line_id': product.id,
                                           'project_id': self.id, 'job_id': task_id.id, 'cost_id': cost_id.id,
                                           'work_item_code': '',
                                           'name': '', 'item_type': '',
                                           'product_code': 'subcontractor', 'product': product.product_id.id,
                                           'vendor': '',
                                           'code': '',
                                           'send_to_pr': False, 'send_to_po': False, 'procurment_id': '',
                                           'action_line': 0,
                                           'planned_qty': product.product_qty, 'cost_price': product.cost_price,
                                           'uom_id': product.uom_id.id,
                                           'qty_actually': '',
                                           'job_type_id': product.job_type_id.id}
                                    list.append((0, 0, dic))
                                    child += 1

                        for product in cost_id.job_labour_line_ids:
                            if product.product_id.type == 'product':
                                # procurment_list_lines = self.env['procurment.list.lines'].search([('procurment_id','=',procurment_list.id),('product','=',product.id)])
                                found_in = procurment_list_lines.filtered(lambda
                                                                              x: x.product.id == product.product_id.id and x.sequance > p_line.sequance and x.sequance < p_line.sequance + 100)
                                if len(found_in) == 0:
                                    dic = {'sequance': child,
                                           'job_cost_line_id': product.id,
                                           'project_id': self.id, 'job_id': task_id.id, 'cost_id': cost_id.id,
                                           'work_item_code': '',
                                           'name': '', 'item_type': '',
                                           'product_code': 'labour', 'product': product.product_id.id, 'vendor': '',
                                           'code': '',
                                           'send_to_pr': False, 'send_to_po': False, 'procurment_id': '',
                                           'action_line': 0,
                                           'planned_qty': '', 'cost_price': product.cost_price, 'uom_id': '',
                                           'qty_actually': '', 'job_type_id': product.job_type_id.id}
                                    # pll = pll.create(dic)
                                    list.append((0, 0, dic))
                                    child += 1

                        for product in cost_id.equipment_line_ids:
                            if product.product_id.type == 'product':
                                # procurment_list_lines = self.env['procurment.list.lines'].search([('procurment_id','=',procurment_list.id),('product','=',product.id)])
                                found_in = procurment_list_lines.filtered(lambda
                                                                              x: x.product.id == product.product_id.id and x.sequance > p_line.sequance and x.sequance < p_line.sequance + 100)
                                if len(found_in) == 0:
                                    dic = {'sequance': child,
                                           'job_cost_line_id': product.id,
                                           'project_id': self.id, 'job_id': task_id.id, 'cost_id': cost_id.id,
                                           'work_item_code': '',
                                           'name': '', 'item_type': '',
                                           'product_code': 'equipment', 'product': product.product_id.id, 'vendor': '',
                                           'code': '',
                                           'send_to_pr': False, 'send_to_po': False, 'procurment_id': '',
                                           'action_line': 0,
                                           'planned_qty': '', 'cost_price': product.cost_price, 'uom_id': '',
                                           'qty_actually': '', 'job_type_id': product.job_type_id.id}
                                    # pll = pll.create(dic)
                                    list.append((0, 0, dic))
                                    child += 1
                        for product in cost_id.job_overhead_line_ids:
                            if product.product_id.type == 'product':
                                # procurment_list_lines = self.env['procurment.list.lines'].search([('procurment_id','=',procurment_list.id),('product','=',product.id)])
                                found_in = procurment_list_lines.filtered(lambda
                                                                              x: x.product.id == product.product_id.id and x.sequance > p_line.sequance and x.sequance < p_line.sequance + 100)
                                if len(found_in) == 0:
                                    dic = {'sequance': child,
                                           'job_cost_line_id': product.id,
                                           'project_id': self.id, 'job_id': task_id.id, 'cost_id': cost_id.id,
                                           'work_item_code': '',
                                           'name': '', 'item_type': '',
                                           'product_code': 'overhead', 'product': product.product_id.id, 'vendor': '',
                                           'code': '',
                                           'send_to_pr': False, 'send_to_po': False, 'procurment_id': '',
                                           'action_line': 0,
                                           'planned_qty': product.product_qty, 'cost_price': product.cost_price,
                                           'uom_id': product.uom_id.id,
                                           'qty_actually': '',
                                           'job_type_id': product.job_type_id.id}
                                    # pll = pll.create(dic)
                                    list.append((0, 0, dic))
                                    child += 1

                        for product in cost_id.other_line_ids:
                            if product.product_id.type == 'product':
                                # procurment_list_lines = self.env['procurment.list.lines'].search([('procurment_id','=',procurment_list.id),('product','=',product.id)])
                                found_in = procurment_list_lines.filtered(lambda
                                                                              x: x.product.id == product.product_id.id and x.sequance > p_line.sequance and x.sequance < p_line.sequance + 100)
                                if len(found_in) == 0:
                                    dic = {'sequance': child,
                                           'job_cost_line_id': product.id,
                                           'project_id': self.id, 'job_id': task_id.id, 'cost_id': cost_id.id,
                                           'work_item_code': '',
                                           'name': '', 'item_type': '',
                                           'product_code': 'other', 'product': product.product_id.id, 'vendor': '',
                                           'code': '',
                                           'send_to_pr': False, 'send_to_po': False, 'procurment_id': '',
                                           'action_line': 0,
                                           'planned_qty': product.product_qty, 'cost_price': product.cost_price,
                                           'uom_id': product.uom_id.id,
                                           'qty_actually': '', 'job_type_id': product.job_type_id.id}
                                    # pll = pll.create(dic)
                                    list.append((0, 0, dic))
                                    child += 1

        procurment_list.procurment_lines = list

    def confirm_tender(self):
        stock_locations = self.env['stock.location'].create({'name': self.location_id, 'usage': 'internal'})
        self.stock_location_id = stock_locations.id

        list = []
        root = 99
        for task in self.task_ids.sorted(lambda x: x.id):
            dic = {
                'sequance': root,
                'job_cost_line_id': '',
                'project_id': self.id, 'job_id': task.id, 'cost_id': '', 'work_item_code': task.tender_id.code,
                'name': task.name,
                'item_type': 'view',
                'product_code': '', 'product': '', 'vendor': '', 'code': '',
                'send_to_pr': False, 'send_to_po': False, 'procurment_id': '', 'action_line': 0,
                'planned_qty': '', 'cost_price': '', 'uom_id': '', 'qty_actually': ''}
            list.append((0, 0, dic))
            parent = root + 1
            for rec in task.job_cost_ids.sorted(lambda x: x.id):
                rec.state = 'approve'
                dic = {'sequance': parent,
                       'job_cost_line_id': '',
                       'project_id': self.id, 'job_id': task.id, 'cost_id': rec.id,
                       'work_item_code': rec.tender_id.code,
                       'name': rec.name, 'item_type': 'transaction',
                       'product_code': '', 'product': '', 'vendor': '', 'code': '',
                       'send_to_pr': False, 'send_to_po': False, 'procurment_id': '', 'action_line': 0,
                       'planned_qty': '', 'cost_price': '', 'uom_id': '', 'qty_actually': ''}
                list.append((0, 0, dic))

                child = parent + 1

                for product in rec.job_cost_line_ids.sorted(lambda x: x.id):
                    if product.product_id.type == 'product':
                        dic = {'sequance': child,
                               'job_cost_line_id': product.id,
                               'project_id': self.id, 'job_id': task.id, 'cost_id': rec.id, 'work_item_code': '',
                               'name': '', 'item_type': '',
                               'product_code': 'Material', 'product': product.product_id.id, 'vendor': '', 'code': '',
                               'send_to_pr': False, 'send_to_po': False, 'procurment_id': '', 'action_line': 0,
                               'planned_qty': product.product_qty, 'cost_price': product.cost_price,
                               'uom_id': product.uom_id.id,
                               'qty_actually': '',
                               'job_type_id': product.job_type_id.id}
                        # pll = pll.create(dic)
                        list.append((0, 0, dic))
                        child += 1
                for product in rec.subcontractor_line_ids.sorted(lambda x: x.id):
                    if product.product_id.type == 'product':
                        dic = {'sequance': child,
                               'job_cost_line_id': product.id,
                               'project_id': self.id, 'job_id': task.id, 'cost_id': rec.id, 'work_item_code': '',
                               'name': '', 'item_type': '',
                               'product_code': 'subcontractor', 'product': product.product_id.id, 'vendor': '',
                               'code': '',
                               'send_to_pr': False, 'send_to_po': False, 'procurment_id': '', 'action_line': 0,
                               'planned_qty': product.product_qty, 'cost_price': product.cost_price,
                               'uom_id': product.uom_id.id,
                               'qty_actually': '',
                               'job_type_id': product.job_type_id.id}
                        # pll = pll.create(dic)
                        list.append((0, 0, dic))
                        child += 1
                for product in rec.job_labour_line_ids.sorted(lambda x: x.id):
                    if product.product_id.type == 'product':
                        dic = {'sequance': child,
                               'job_cost_line_id': product.id,
                               'project_id': self.id, 'job_id': task.id, 'cost_id': rec.id, 'work_item_code': '',
                               'name': '', 'item_type': '',
                               'product_code': 'labour', 'product': product.product_id.id, 'vendor': '', 'code': '',
                               'send_to_pr': False, 'send_to_po': False, 'procurment_id': '', 'action_line': 0,
                               'planned_qty': '', 'cost_price': product.cost_price, 'uom_id': '', 'qty_actually': '',
                               'job_type_id': product.job_type_id.id}
                        # pll = pll.create(dic)
                        list.append((0, 0, dic))
                        child += 1
                for product in rec.equipment_line_ids.sorted(lambda x: x.id):
                    if product.product_id.type == 'product':
                        dic = {'sequance': child,
                               'job_cost_line_id': product.id,
                               'project_id': self.id, 'job_id': task.id, 'cost_id': rec.id, 'work_item_code': '',
                               'name': '', 'item_type': '',
                               'product_code': 'equipment', 'product': product.product_id.id, 'vendor': '', 'code': '',
                               'send_to_pr': False, 'send_to_po': False, 'procurment_id': '', 'action_line': 0,
                               'planned_qty': '', 'cost_price': product.cost_price, 'uom_id': '', 'qty_actually': '',
                               'job_type_id': product.job_type_id.id}
                        # pll = pll.create(dic)
                        list.append((0, 0, dic))
                        child += 1
                for product in rec.job_overhead_line_ids.sorted(lambda x: x.id):
                    if product.product_id.type == 'product':
                        dic = {'sequance': child,
                               'job_cost_line_id': product.id,
                               'project_id': self.id, 'job_id': task.id, 'cost_id': rec.id, 'work_item_code': '',
                               'name': '', 'item_type': '',
                               'product_code': 'overhead', 'product': product.product_id.id, 'vendor': '', 'code': '',
                               'send_to_pr': False, 'send_to_po': False, 'procurment_id': '', 'action_line': 0,
                               'planned_qty': product.product_qty, 'cost_price': product.cost_price,
                               'uom_id': product.uom_id.id,
                               'qty_actually': '',
                               'job_type_id': product.job_type_id.id}
                        # pll = pll.create(dic)
                        list.append((0, 0, dic))
                        child += 1
                for product in rec.other_line_ids.sorted(lambda x: x.id):
                    if product.product_id.type == 'product':
                        dic = {'sequance': child,
                               'job_cost_line_id': product.id,
                               'project_id': self.id, 'job_id': task.id, 'cost_id': rec.id, 'work_item_code': '',
                               'name': '', 'item_type': '',
                               'product_code': 'other', 'product': product.product_id.id, 'vendor': '', 'code': '',
                               'send_to_pr': False, 'send_to_po': False, 'procurment_id': '', 'action_line': 0,
                               'planned_qty': product.product_qty, 'cost_price': product.cost_price,
                               'uom_id': product.uom_id.id,
                               'qty_actually': '',
                               'job_type_id': product.job_type_id.id}
                        # pll = pll.create(dic)
                        list.append((0, 0, dic))
                        child += 1

                parent += 100

            frac = int(str(parent)[2:]) - 100
            root = parent + abs(frac) - 1

        for line in self.project_tender_ids:
            if not line.related_task_id:
                raise ValidationError(_('You should add related job order in project tender lines..'))

        dic = {'discount': self.discount, 'name': self.id, 'project_no': self.project_no,
               'partner_id': self.partner_id.id, 'start_date': self.project_start_date,
               'end_date': self.project_end_date, 'procurment_lines': list,
               'analytic_account_id': self.analytic_account_id.id, 'location_id': stock_locations.id,
               'client_specialist_id': self.client_specialist_id.id, 'consultant': self.consultant_id and self.consultant_id.id}
        pl = self.env['procurment.list']
        pl.create(dic)

        project_task = self.env['project.task']
        key_personel_lines = []
        for k_p_l in self.key_personnel_ids:
            key_personel_lines.append((0, 0, {
                'position_id': k_p_l.position_id.id,
                'employee_id': k_p_l.employee_id.id,
                'mobile': k_p_l.mobile,
                'email_id': k_p_l.email_id,
            }))
        project_task.create({
            'name': 'Job Order Report Data',
            'project_id': self.id,
            'job_order_no': self.job_order_no,
            'project_ID': self.project_ID,
            'client_name': self.client_name,
            'client_manager': self.client_manager,
            'entry_date': self.entry_date,
            'location': self.location,
            'po_number': self.po_number,
            'po_date': self.po_date,
            'start_date': self.start_date,
            'hand_over_date': self.hand_over_date,
            'key_personnel_ids': key_personel_lines,
            'stage_id': self.env['project.task.type'].search([('name', '=', 'Coordinator')]).id,
        })
        self.state = 'in_hand'
        for rec in self.job_cost_ids:
            rec.state = 'confirm'
            if self.analytic_account_id:
                rec.analytic_id = self.analytic_account_id.id
        for rec in self.task_ids:
            rec.state = 'in_hand'

        for record in self.env['automatic.tasks'].search([('sequence', '!=', 0)]):
            project_task.create({
                'name': record.name,
                'project_id': self.id,
                'date_start': self.project_start_date,
                'date_end': self.project_end_date,
                'is_job_document': True if record.is_job_document else False,
                'is_job_schedule': True if record.is_job_schedule else False,
                'stage_id': record.stage_id.id,
            })

        return True

    def refuse_tender(self):
        self.state = 'refused'
        for rec in self.job_cost_ids:
            rec.state = 'cancel'
        for rec in self.task_ids:
            rec.state = 'cancel'


class ProjectDates(models.Model):
    _name = 'project.dates'

    hold_date = fields.Date(string='Hold Date')
    restart_date = fields.Date(string='Restart Date')
    extra_duration = fields.Integer(string='Extra Duration', compute='_get_extra_period')
    notes = fields.Text(string='Comment')
    attachment_ids = fields.Many2many(string="Attachment",
                                      comodel_name='ir.attachment', copy=False)
    project_id = fields.Many2one(comodel_name='project.project')


    @api.depends('hold_date', 'restart_date')
    def _get_extra_period(self):
        if self.hold_date and self.restart_date:
            d1 = datetime.strptime(str(self.hold_date), "%Y-%m-%d")
            d2 = datetime.strptime(str(self.restart_date), "%Y-%m-%d")
            self.extra_duration = ((d2 - d1).days)
        else:
            self.extra_duration = 0
