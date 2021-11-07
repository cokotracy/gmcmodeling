# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date


class change_reqSubmittal(models.Model):
    _name = 'change_req.submittal'
    _inherit = 'mail.thread'

    def get_default_company(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=get_default_company,
                                 required=False, )

    projectID = fields.Char(string="Project ID", compute='get_project_data', store=True)
    project_id = fields.Many2one(comodel_name="project.project", string="Project Name", required=False, )
    client_id = fields.Many2one(comodel_name="res.partner", string="Client Name", required=False, )
    client_manager_id = fields.Char(string="Client Manager", required=False, )
    client_specialist_id = fields.Many2one(comodel_name='res.partner', string="Attention", compute='get_project_data',
                                           store=True)

    prepared_by_id = fields.Many2one(comodel_name="res.users", string="Prepared By", required=False, )
    consultant = fields.Many2one(comodel_name="consultant.consultant", string="Consultant")
    consultant_pm = fields.Char(string="Consultant PM", required=False, )
    scope_of_work_id = fields.Many2one(comodel_name="work.scope", string="Scope Of Work", required=False, )
    scope_division = fields.Many2one(comodel_name="division.scope", string="Scope Division", required=False, )
    scope_details = fields.Char(string="Scope Details", required=False,tracking=True)

    code = fields.Selection(
        [('a', 'Approved as submitted'), ('b', 'Approved with comments'), ('c', 'Revised and Re submitial required'),
         ('d', 'Disapproved see attached sheet'), ('e', 'Under Preview'), ('p', 'Pending')], string='Status',
        default='e')
    change_reqID = fields.Char(string="CHange Req ID", required=False, )
    revision_no = fields.Char(string="Revision No", required=False, )
    submission_date = fields.Date(string="Submisstion Date", required=False, )
    change_req_seq_num = fields.Integer(string="", required=False, )

    dc_id = fields.Many2one(comodel_name="document.control", string="", required=False, )

    parent_change_req = fields.Many2one(comodel_name="change_req.submittal", string="", required=False, )
    revision_no_seq = fields.Integer(string="", required=False, )
    is_reviewed = fields.Boolean(string="", )
    revisions_num = fields.Integer(string="", compute='get_revisions_num', required=False, )

    impac_on_cost = fields.Selection(string="Impact On Cost", selection=[('yes', 'Yes'), ('no', 'No'), ],
                                     required=False, )
    impac_on_schedule = fields.Selection(string="Impact On Schedule", selection=[('yes', 'Yes'), ('no', 'No'), ],
                                         required=False, )
    impac_on_resources = fields.Selection(string="Impact On Resources", selection=[('yes', 'Yes'), ('no', 'No'), ],
                                          required=False, )
    risk_associated = fields.Selection(string="Risk Associated", selection=[('yes', 'Yes'), ('no', 'No'), ],
                                       required=False, )
    cost_impact_in_sar = fields.Char(string="Cost Impact In SAR", required=False, )
    area_of_change = fields.Selection(string="Area Of Change",
                                      selection=[('scope', 'Scope'), ('schedule', 'Schedule'), ('material', 'Material'),
                                                 ('budget', 'Budget'), ('quality', 'Quality')], required=False, )
    ref_no = fields.Char(string="Reference No", required=False, )
    time_impact = fields.Char(string="Time Impact", required=False, )
    requested_by = fields.Char(string="Requested By", required=False, )
    subject = fields.Char(string="Subject", required=False, )
    description_work = fields.Text(string="Description", required=False, )
    justification = fields.Text(string="Justification", required=False, )
    impact_description = fields.Text(string="Impact Description", required=False, )
    alternatives = fields.Text(string="Alternatives", required=False, )

    @api.depends('revisions_num')
    def get_revisions_num(self):
        self.revisions_num = self.env['change_req.submittal'].search_count([('parent_change_req', '=', self.id)])

    @api.depends('project_id')
    def get_project_data(self):
        self.projectID = self.project_id.project_no
        self.client_id = self.project_id.partner_id.id

    def resbmittal_button(self):
        rfi = self.env['change_req.submittal']

        revision_no = []
        if int(self.revision_no_seq) == 0:
            current_revision_num = 1
        else:
            for record in self.env['change_req.submittal'].search(
                    [('parent_change_req', '=', self.parent_change_req.id)]):
                revision_no.append(int(record.revision_no_seq))
            current_revision_num = max(revision_no) + 1 if revision_no else 1

        rfi.create({

            'projectID': self.projectID,
            'project_id': self.project_id.id,
            'client_id': self.client_id.id,
            'client_manager_id': self.client_manager_id,
            'client_specialist_id': self.client_specialist_id.id,
            'prepared_by_id': self.prepared_by_id.id,
            'subject': self.subject,
            'consultant': self.consultant.id,
            'consultant_pm': self.consultant_pm,
            'description_work': self.description_work,
            'scope_of_work_id': self.scope_of_work_id.id,
            'scope_division': self.scope_division.id,
            'code': self.code,
            'submission_date': self.submission_date,
            'change_reqID': self.change_reqID,
            'revision_no': str(self.change_reqID) + '/REV' + str(current_revision_num),
            'revision_no_seq': str(current_revision_num),
            'parent_change_req': self.id if self.revision_no_seq == 0 else self.parent_change_req.id,
        })

        self.is_reviewed = True

    @api.model
    def create(self, values):
        # Add code here
        res = super(change_reqSubmittal, self).create(values)
        prev_change_req_num = []
        for rec in self.env['change_req.submittal'].search([('project_id', '=', res.project_id.id)]).mapped(
                'change_req_seq_num'):
            if rec != False:
                prev_change_req_num.append(int(rec))

        res.change_req_seq_num = max(prev_change_req_num) + 1 if prev_change_req_num else 1
        seq_const = str('PROJ-') + str(res.projectID) + '/CR-'
        res.change_reqID = seq_const + str(res.change_req_seq_num)
        if not res.revision_no:
            res.revision_no_seq = 0
            res.revision_no = str(res.change_reqID) + '/REV' + str(res.revision_no_seq)
        res.scope_details = str(dict(res._fields['submittal_type'].selection).get(res.submittal_type)) + '/' + str(
            res.scope_of_work_id.code or '') + '/' + str(res.scope_division.name or '')

        return res

    def open_related_revisions(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'change_req.submittal',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'name': 'Revisions',
            'target': 'current',
            'domain': [('parent_change_req', '=', self.id)],
            'context': {'create': False},

        }
