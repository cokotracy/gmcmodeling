# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime,date

class SiteSubmittal(models.Model):
    _name = 'site.submittal'
    _inherit = 'mail.thread'

    def get_default_company(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=get_default_company,
                                 required=False, )

    projectID = fields.Char(string="Project ID", required=False, )
    project_id = fields.Many2one(comodel_name="project.project", string="Project Name", required=False, )
    client_id = fields.Many2one(comodel_name="res.partner", string="Client Name", required=False, )
    client_manager_id = fields.Char(string="Client Manager", required=False, )
    prepared_by_id = fields.Many2one(comodel_name="res.users", string="Prepared By", required=False, )
    subject = fields.Char(string="Subject", required=False, )
    question = fields.Text(string="Question", required=False, )
    suggestion = fields.Text(string="Suggestion", required=False, )
    answer = fields.Text(string="Answer", required=False, )
    submittal_type = fields.Selection(string="Submittal Type", selection=[('dc', 'Document Control'), ('mt', 'Material'),('dw','Drawing') ], required=False, )
    scope_of_work_id = fields.Many2one(comodel_name="work.scope", string="Scope Of Work", required=False, )
    scope_division = fields.Many2one(comodel_name="division.scope",string="Scope Division", required=False, )
    scope_details = fields.Char(string="Scope Details", required=False, )
    code = fields.Selection([('open', 'Open'), ('closed', 'Closed'), ], string='Status',)
    siteID = fields.Char(string="site ID", required=False, )
    revision_no = fields.Char(string="Revision No", required=False, )
    submission_date = fields.Date(string="Submisstion Date", required=False,)
    last_update = fields.Datetime(string="Last Update", required=False,)
    drawing_ref = fields.Char(string="Drawing Reference", required=False, )
    site_seq_num = fields.Integer(string="", required=False, )
    trans_mt_seq = fields.Integer(string="",  )
    trans_dc_seq = fields.Integer(string="",  )
    trans_wd_seq = fields.Integer(string="",  )
    parent_site = fields.Many2one(comodel_name="site.submittal", string="", required=False, )
    revision_no_seq = fields.Integer(string="", required=False, )
    is_reviewed = fields.Boolean(string="",  )
    revisions_num = fields.Integer(string="", compute='get_revisions_num', required=False, )

    @api.depends('revisions_num')
    def get_revisions_num(self):
        self.revisions_num = self.env['site.submittal'].search_count([('parent_site', '=', self.id)])

    @api.onchange('project_id')
    def get_project_data(self):
        self.projectID = self.project_id.project_no

    def resbmittal_button(self):
        site = self.env['site.submittal']
        revision_no = []
        if int(self.revision_no_seq) == 0:
            current_revision_num = 1
        else:
            for record in self.env['site.submittal'].search([('parent_site','=',self.parent_site.id)]):
                revision_no.append(int(record.revision_no_seq))
            current_revision_num = max(revision_no) + 1 if revision_no else 1

        site.create({

            'projectID': self.projectID,
            'project_id': self.project_id.id,
            'client_id': self.client_id.id,
            'client_manager_id':self.client_manager_id,
            'prepared_by_id': self.prepared_by_id.id,
            'subject': self.subject,
            'question': self.question,
            'suggestion': self.suggestion,
            'answer': self.answer,
            'submittal_type': self.submittal_type,
            'scope_of_work_id': self.scope_of_work_id.id,
            'scope_division': self.scope_division.id,
            'scope_details': self.scope_details,
            'code': self.code,
            'submission_date': self.submission_date,
            'last_update': self.last_update,
            'drawing_ref': self.drawing_ref,
            'siteID': self.siteID,
            'revision_no': str(self.siteID) + '/REV' + str(current_revision_num),
            'revision_no_seq': str(current_revision_num),
            'parent_site':self.id if self.revision_no_seq == 0 else self.parent_site.id,
        })

        self.is_reviewed = True


    @api.model
    def create(self, values):
        # Add code here
        res = super(SiteSubmittal, self).create(values)
        if not res.siteID:
            prev_trans_mt_num = []
            prev_trans_dc_num = []
            prev_trans_wd_num = []
            for rec in self.env['site.submittal'].search([('project_id','=',res.project_id.id)]):
                if rec != False:
                    if res.submittal_type == 'mt':
                        if rec.submittal_type == 'mt':
                            prev_trans_mt_num.append(int(rec.trans_mt_seq))
                    if res.submittal_type == 'dc':
                        if rec.submittal_type == 'dc':
                            prev_trans_dc_num.append(int(rec.trans_dc_seq))
                    if res.submittal_type == 'dw':
                        if rec.submittal_type == 'dw':
                            prev_trans_wd_num.append(int(rec.trans_wd_seq))
            seq_const = str('PROJ-') + str(res.projectID) + '/' + str(res.scope_of_work_id.code) + '/'
            if res.submittal_type == 'mt':
                res.trans_mt_seq = max(prev_trans_mt_num) + 1 if prev_trans_mt_num else 1
                res.siteID = seq_const + str('SFMT-') + str(res.trans_mt_seq)
            if res.submittal_type == 'dc':
                res.trans_dc_seq = max(prev_trans_dc_num) + 1 if prev_trans_dc_num else 1
                res.siteID = seq_const + str('SFDC-') + str(res.trans_dc_seq)
            if res.submittal_type == 'dw':
                res.trans_wd_seq = max(prev_trans_wd_num) + 1 if prev_trans_wd_num else 1
                res.siteID = seq_const + str('SFDW-') + str(res.trans_wd_seq)

            res.scope_details = str(dict(res._fields['submittal_type'].selection).get(res.submittal_type)) + '/' + str(
                res.scope_of_work_id.code or '') + '/' + str(res.scope_division.name or '')

        if not res.revision_no:
            res.revision_no_seq = 0
            res.revision_no = str(res.siteID) + '/REV' + str(res.revision_no_seq)

        return res


    def open_related_revisions(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'site.submittal',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'name': 'Revisions',
            'target': 'current',
            'domain': [('parent_site', '=', self.id)],
            'context': {'create':False },

        }
