# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime,date

# selection_values = []


class daily_activitySubmittal(models.Model):
    _name = 'daily_activity.submittal'
    _inherit = 'mail.thread'

    def get_default_company(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=get_default_company,
                                 required=False, )

    projectID = fields.Char(string="Project ID", compute='get_project_data',store=True )
    project_id = fields.Many2one(comodel_name="project.project", string="Project Name", required=False, )
    client_id = fields.Many2one(comodel_name="res.partner", string="Client Name", required=False, )
    client_manager_id = fields.Char(string="Client Manager", required=False, )
    client_specialist_id = fields.Many2one(comodel_name='res.partner',string="Attention", compute='get_project_data',store=True )

    prepared_by_id = fields.Many2one(comodel_name="res.users", string="Prepared By", required=False, )
    daily_activityID = fields.Char(string="Man Power ID", required=False, )
    submission_date = fields.Date(string="Submisstion Date", required=False, )
    daily_activity_seq_num = fields.Integer(string="", required=False, )
    weather = fields.Selection(string="Weather", selection=[('sunny', 'Sunny'), ('cloudy', 'Cloudy'),('rainy', 'Rainy'),('dusty', 'Dusty'), ], required=False, )
    humidity = fields.Selection(string="Humidity", selection=[('low', 'Low'), ('medium', 'Medium'),('high', 'High') ], required=False, )
    main_contractor = fields.Char(string="Main Contractor", required=False, )

    # STAFF
    project_manager = fields.Char(string="Project Manager", required=False, )
    site_manager = fields.Char(string="Site Manager", required=False, )
    engineers = fields.Char(string="Engineers", required=False, )
    admin = fields.Char(string="Admin", required=False, )
    technicians = fields.Char(string="Technicians", required=False, )
    safety_officer = fields.Char(string="Safety Officer", required=False, )
    indir_labour = fields.Char(string="Indir Labour", required=False, )
    operator = fields.Char(string="Operator", required=False, )
    mechanic = fields.Char(string=" Mechanic", required=False, )
    electricians = fields.Char(string="Electricians", required=False, )
    welders = fields.Char(string="Welders", required=False, )
    drivers = fields.Char(string="Drivers", required=False, )
    # DIRECT LABOUR
    foreman = fields.Char(string="Foreman", required=False, )
    charge_hand = fields.Char(string="Charge Hand", required=False, )
    steel_fixer = fields.Char(string="Steel Fixer", required=False, )
    carpenter = fields.Char(string="Carpenter", required=False, )
    mason = fields.Char(string="Mason", required=False, )
    plasterer = fields.Char(string="Plasterer", required=False, )
    office_boys = fields.Char(string="Office Boys", required=False, )
    plumbers = fields.Char(string="Plumbers", required=False, )
    unSkilled = fields.Char(string="UnSkilled", required=False, )
    night_watchman = fields.Char(string="Night Watchman", required=False, )
    cleaner = fields.Char(string="Cleaner", required=False, )
    store_keeper = fields.Char(string="Store Keeper", required=False, )
    gate_keeper = fields.Char(string="Gate Keeper", required=False, )
    # TYPE
    backhoe = fields.Char(string="Backhoe", required=False, )
    backhoe_status = fields.Selection(string="Status", selection=[('idle', 'IDLE'), ('repair', 'REPAIR'), ], required=False, )

    wheel_loader = fields.Char(string="Wheel Loader", required=False, )
    wheel_loader_status = fields.Selection(string="Status", selection=[('idle', 'IDLE'), ('repair', 'REPAIR'), ], required=False, )

    tipper = fields.Char(string="Tipper", required=False, )
    tipper_status = fields.Selection(string="Status", selection=[('idle', 'IDLE'), ('repair', 'REPAIR'), ], required=False, )

    rooler_compactor = fields.Char(string="Rooler Compactor", required=False, )
    rooler_compactor_status = fields.Selection(string="Status", selection=[('idle', 'IDLE'), ('repair', 'REPAIR'), ], required=False, )

    mobile_crane = fields.Char(string="Mobile Crane", required=False, )
    mobile_crane_status = fields.Selection(string="Status", selection=[('idle', 'IDLE'), ('repair', 'REPAIR'), ], required=False, )

    tower_crane = fields.Char(string="Tower Crane", required=False, )
    tower_crane_status = fields.Selection(string="Status", selection=[('idle', 'IDLE'), ('repair', 'REPAIR'), ], required=False, )

    transit_mixer = fields.Char(string="Transit Mixer", required=False, )
    transit_mixer_status = fields.Selection(string="Status", selection=[('idle', 'IDLE'), ('repair', 'REPAIR'), ], required=False, )

    concrete_vibrator = fields.Char(string="Concrete Vibrator", required=False, )
    concrete_vibrator_status = fields.Selection(string="Status", selection=[('idle', 'IDLE'), ('repair', 'REPAIR'), ], required=False, )

    welding_machine = fields.Char(string="Welding Machine", required=False, )
    welding_machine_status = fields.Selection(string="Status", selection=[('idle', 'IDLE'), ('repair', 'REPAIR'), ], required=False, )

    generator = fields.Char(string="Generator", required=False, )
    generator_status = fields.Selection(string="Status", selection=[('idle', 'IDLE'), ('repair', 'REPAIR'), ], required=False, )

    bar_bending_cutting = fields.Char(string="Bar Bending/Cutting", required=False, )
    bar_bending_cutting_status = fields.Selection(string="Status", selection=[('idle', 'IDLE'), ('repair', 'REPAIR'), ], required=False, )

    pick_up_trucks = fields.Char(string="Pick up Trucks", required=False, )
    pick_up_trucks_status = fields.Selection(string="Status", selection=[('idle', 'IDLE'), ('repair', 'REPAIR'), ], required=False, )

    bobcat_telescopic = fields.Char(string="Bobcat Telescopic", required=False, )
    bobcat_telescopic_status = fields.Selection(string="Status", selection=[('idle', 'IDLE'), ('repair', 'REPAIR'), ], required=False, )
    dc_id = fields.Many2one(comodel_name="document.control", string="", required=False, )
    revision_no_seq = fields.Integer(string="", required=False, )

    def action_dc_send(self):

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference("wc_document_control", 'email_template_daily_activity_submittal')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'daily_activity.submittal',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,

            'proforma': self.env.context.get('proforma', True),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


    @api.depends('project_id')
    def get_project_data(self):
        self.projectID = self.project_id.project_no
        self.client_id = self.project_id.partner_id.id

    @api.model
    def create(self, values):
        # Add code here
        res = super(daily_activitySubmittal, self).create(values)
        prev_daily_activity_num = []
        for rec in self.env['daily_activity.submittal'].search([('project_id','=',res.project_id.id)]).mapped('daily_activity_seq_num'):
            if rec != False:
                prev_daily_activity_num.append(int(rec))

        res.daily_activity_seq_num = max(prev_daily_activity_num) + 1 if prev_daily_activity_num else 1
        seq_const = str('PROJ-') + str(res.projectID) + '/MP-'
        res.daily_activityID = seq_const + str(res.daily_activity_seq_num)

        return res








