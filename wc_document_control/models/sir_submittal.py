# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime,date



class SIRSubmittal(models.Model):
    _name = 'sir.submittal'
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
    subject = fields.Char(string="Subject", required=False, )
    description_work = fields.Text(string="Description Of work", required=False, )
    consultant = fields.Many2one(comodel_name="consultant.consultant", string="Consultant")
    consultant_pm = fields.Char(string="Consultant PM", required=False, )
    scope_of_work_id = fields.Many2one(comodel_name="work.scope", string="Scope Of Work", required=False, )
    scope_division = fields.Many2one(comodel_name="division.scope",string="Scope Division", required=False, )
    code = fields.Selection(
        [('a', 'Approved as submitted'), ('b', 'Approved with comments'), ('c', 'Revised and Re submitial required'),
         ('d', 'Disapproved see attached sheet'),('e', 'Under Preview'),('p', 'Pending')], string='Status',default='e')
    sirID = fields.Char(string="SIR ID", required=False, )
    revision_no = fields.Char(string="Revision No", required=False, )
    submission_date = fields.Date(string="Submisstion Date", required=False, )
    return_date = fields.Date(string="Return Date", required=False, )
    location = fields.Char(string="Location", required=False, )
    sir_seq_num = fields.Integer(string="", required=False, )

    dc_id = fields.Many2one(comodel_name="document.control", string="", required=False, )

    parent_sir = fields.Many2one(comodel_name="sir.submittal", string="", required=False, )
    revision_no_seq = fields.Integer(string="", required=False, )
    is_reviewed = fields.Boolean(string="", )
    revisions_num = fields.Integer(string="", compute='get_revisions_num', required=False, )

    def action_dc_send(self):

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference("wc_document_control", 'email_template_sir_submittal')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'sir.submittal',
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



    @api.depends('revisions_num')
    def get_revisions_num(self):
        self.revisions_num = self.env['sir.submittal'].search_count([('parent_sir', '=', self.id)])

    @api.depends('project_id')
    def get_project_data(self):
        self.projectID = self.project_id.project_no
        self.client_id = self.project_id.partner_id.id

    def resbmittal_button(self):
        rfi = self.env['sir.submittal']
        revision_no = []
        if int(self.revision_no_seq) == 0:
            current_revision_num = 1
        else:
            for record in self.env['sir.submittal'].search([('parent_sir', '=', self.parent_sir.id)]):
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
            'description_work': self.description_work,
            'consultant': self.consultant.id,
            'consultant_pm': self.consultant_pm,
            'scope_of_work_id': self.scope_of_work_id.id,
            'scope_division': self.scope_division.id,
            'code': self.code,
            'submission_date': self.submission_date,
            'return_date': self.return_date,
            'location': self.location,
            'sirID': self.sirID,
            'revision_no': str(self.sirID) + '/REV' + str(current_revision_num),
            'revision_no_seq': str(current_revision_num),
            'parent_sir': self.id if self.revision_no_seq == 0 else self.parent_sir.id,
        })

        self.is_reviewed = True

    @api.model
    def create(self, values):
        # Add code here
        res = super(SIRSubmittal, self).create(values)
        prev_sir_num = []
        for rec in self.env['sir.submittal'].search([('project_id','=',res.project_id.id)]).mapped('sir_seq_num'):
            if rec != False:
                prev_sir_num.append(int(rec))

        res.sir_seq_num = max(prev_sir_num) + 1 if prev_sir_num else 1
        seq_const = str('PROJ-') + str(res.projectID) + '/' + str(res.scope_of_work_id.code) + '/SIR-'
        res.sirID = seq_const + str(res.sir_seq_num)
        if not res.revision_no:
            res.revision_no_seq = 0
            res.revision_no = str(res.sirID) + '/REV' + str(res.revision_no_seq)


        return res

    def open_related_revisions(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sir.submittal',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'name': 'Revisions',
            'target': 'current',
            'domain': [('parent_sir', '=', self.id)],
            'context': {'create':False },

        }





