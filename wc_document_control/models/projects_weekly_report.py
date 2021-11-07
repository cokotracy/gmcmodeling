# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date


class ProjectsWeeklyReports(models.Model):
    _name = 'projects.weekly.report'
    _inherit = 'mail.thread'
    _rec_name = 'project_id'
    _description = ''

    def get_default_company(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=get_default_company,
                                 required=False, )

    project_id = fields.Many2one(comodel_name="project.project", string="Project Name", required=False,
                                 tracking=True)
    date = fields.Date(string="Date", required=False, default=fields.Date.context_today, tracking=True)
    phases = fields.Char(string="Phases", required=False, )
    arch_work_planned = fields.Float(string="Arch.Work Planned %", tracking=True, required=False, )
    arch_work_actual = fields.Float(string="Arch.Work Aactual %", tracking=True, required=False, )
    arch_variance = fields.Float(string="Arch Variance %", compute='get_arch_variance', tracking=True,
                                 store=True, required=False, )
    elect_work_planned = fields.Float(string="Elect.Work Planned %", tracking=True, required=False, )
    elect_work_actual = fields.Float(string="Elect.Work Aactual %", tracking=True, required=False, )
    elect_variance = fields.Float(string="Elect Variance %", tracking=True, compute='get_elect_variance',
                                  store=True, required=False, )
    plumping_work_planned = fields.Float(string="Plumping.Work Planned %", tracking=True,
                                         required=False, )
    plumping_work_actual = fields.Float(string="Plumping.Work Aactual %", tracking=True, required=False, )
    plumping_variance = fields.Float(string="Plumping Variance %", tracking=True,
                                     compute='get_plumping_variance', store=True, required=False, )
    hvac_work_planned = fields.Float(string="HVAC.Work Planned %", tracking=True, required=False, )
    hvac_work_actual = fields.Float(string="HVAC.Work Aactual %", tracking=True, required=False, )
    hvac_variance = fields.Float(string="HVAC Variance %", tracking=True, compute='get_hvac_variance',
                                 store=True, required=False, )
    ff_work_planned = fields.Float(string="FF.Work Planned %", tracking=True, required=False, )
    ff_work_actual = fields.Float(string="FF.Work Aactual %", tracking=True, required=False, )
    ff_variance = fields.Float(string="FF Variance %", tracking=True, compute='get_ff_variance',
                               store=True, required=False, )
    summary_work_planned = fields.Float(string="Summary.Work Planned %", tracking=True, required=False, )
    summary_work_actual = fields.Float(string="Summary.Work Aactual %", tracking=True, required=False, )
    summary_variance = fields.Float(string="Summary Variance %", tracking=True,
                                    compute='get_summary_variance', store=True, required=False, )
    notes = fields.Text(string="Notes", tracking=True, required=False, )
    remaining_time = fields.Float(string="Remaining Time", tracking=True, required=False, )
    start_bl = fields.Date(string="Start BL", tracking=True, required=False, )
    start_act = fields.Date(string="Start AcT", tracking=True, required=False, )
    finish_bl = fields.Date(string="Finish BL", tracking=True, required=False, )
    finish_act = fields.Date(string="Finish AcT", tracking=True, required=False, )
    delay = fields.Float(string="Delay", tracking=True, required=False, )

    @api.depends('arch_work_planned', 'arch_work_actual')
    def get_arch_variance(self):
        self.arch_variance = self.arch_work_actual - self.arch_work_planned

    @api.depends('elect_work_planned', 'elect_work_actual')
    def get_elect_variance(self):
        self.elect_variance = self.arch_work_actual - self.elect_work_planned

    @api.depends('plumping_work_planned', 'plumping_work_actual')
    def get_plumping_variance(self):
        self.plumping_variance = self.plumping_work_actual - self.plumping_work_planned

    @api.depends('hvac_work_planned', 'hvac_work_actual')
    def get_hvac_variance(self):
        self.hvac_variance = self.hvac_work_actual - self.hvac_work_planned

    @api.depends('ff_work_planned', 'ff_work_actual')
    def get_ff_variance(self):
        self.ff_variance = self.ff_work_actual - self.ff_work_planned

    @api.depends('summary_work_planned', 'summary_work_actual')
    def get_summary_variance(self):
        self.summary_variance = self.summary_work_actual - self.summary_work_planned

    def send_notifications(self):
        followers = self.message_partner_ids.ids
        print(followers, 'ffffffffff')

        thread_pool = self.env['mail.thread']
        if False not in followers:
            thread_pool.sudo().message_notify(
                partner_ids=followers,
                subject="Weekly Project Report Notification",
                body='Please Check this Project Weekly Report: <a target=_BLANK href="/web?#id=' + str(
                    self.id) + '&view_type=form&model=projects.weekly.report&action=" style="font-weight: bold">' + str(
                    self.project_id.name) + '</a>',
                # email_from=self.env.user.company_id.catchall or self.env.user.company_id.email, )
                email_from=self.env.user.company_id.email, )