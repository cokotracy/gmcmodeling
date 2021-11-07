# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime,date

class variationSubmittal(models.Model):
    _name = 'variation.submittal'
    _inherit = 'mail.thread'

    def get_default_company(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=get_default_company,
                                 required=False, )

    projectID = fields.Char(string="Project ID", compute='get_project_data',store=True )
    project_id = fields.Many2one(comodel_name="project.project", string="Project Name", required=False, )
    client_id = fields.Many2one(comodel_name="res.partner", string="Client Name", required=False, )
    contractor = fields.Char(string="Contractor", required=False, )
    client_manager_id = fields.Char(string="Client Manager", required=False, )
    client_specialist_id = fields.Many2one(comodel_name='res.partner',string="Attention", compute='get_project_data',store=True )
    prepared_by_id = fields.Many2one(comodel_name="res.users", string="Prepared By", required=False, )
    consultant = fields.Many2one(comodel_name="consultant.consultant", string="Consultant")
    consultant_pm = fields.Char(string="Consultant PM", required=False, )
    code = fields.Selection(
        [('a', 'Approved as submitted'), ('b', 'Approved with comments'), ('c', 'Revised and Re submitial required'),
         ('d', 'Disapproved see attached sheet'),('e', 'Under review'),('p', 'Pending')], string='Status',default='e')
    variationID = fields.Char(string="CHange Req ID", required=False, )
    revision_no = fields.Char(string="Revision No", required=False, )
    submission_date = fields.Date(string="Submisstion Date", required=False, )

    po_date = fields.Date(string="PO Date", required=False, )
    current_completion_date = fields.Date(string="PO Date", required=False, )
    revised_completion_date = fields.Date(string="Revised Completion Date", required=False, )
    po_loi_no = fields.Char(string="PO /Loi No", required=False, )
    delivery_validity = fields.Float(string="Delivery Validity", required=False, )
    quotation_validity = fields.Float(string="Quotation Validity", required=False, )
    initial_contract_amount = fields.Float(string="Initial Contract Amount", required=False, )
    previously_approved_variation = fields.Float(string="Previously Approved Variation", required=False, )
    requested_variation_amount = fields.Float(string="Requested Variation Amount", required=False, )
    accumulated_contract_amount = fields.Float(string="Accumulated Contract Amount", required=False, )
    total_amount = fields.Char(string="Total Amount", required=False, )
    title = fields.Selection(string="Title",
                             selection=[('var_order', 'Variation Order'), ('var_proposal', 'Variation Proposal'),
                                        ('var_submission', 'Variation Submission'),
                                        ('note_claim', 'Notification Of Claim')], required=False, )
    subject = fields.Char(string="Subject", required=False, )
    justification = fields.Char(string="Justification", required=False, )
    narative_of_work = fields.Text(string="Narative Of Work", required=False, )
    description = fields.Text(string="Description", required=False, )
    remarks = fields.Text(string="Remarks", required=False, )
    amount_in_words = fields.Char(string="Amount In Words", required=False, )

    variation_seq_num = fields.Integer(string="", required=False, )
    dc_id = fields.Many2one(comodel_name="document.control", string="", required=False, )
    parent_variation = fields.Many2one(comodel_name="variation.submittal", string="", required=False, )
    revision_no_seq = fields.Integer(string="", required=False, )
    is_reviewed = fields.Boolean(string="", )
    revisions_num = fields.Integer(string="", compute='get_revisions_num', required=False, )

    def action_dc_send(self):

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference("wc_document_control", 'email_template_variation_submittal')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'variation.submittal',
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
        self.revisions_num = self.env['variation.submittal'].search_count([('parent_variation', '=', self.id)])

    @api.depends('project_id')
    def get_project_data(self):
        self.projectID = self.project_id.project_no
        self.client_id = self.project_id.partner_id.id

    def resbmittal_button(self):
        variation = self.env['variation.submittal']


        revision_no = []
        if int(self.revision_no_seq) == 0:
            current_revision_num = 1
        else:
            for record in self.env['variation.submittal'].search([('parent_variation', '=', self.parent_variation.id)]):
                revision_no.append(int(record.revision_no_seq))
            current_revision_num = max(revision_no) + 1 if revision_no else 1

        variation.create({

            'projectID': self.projectID,
            'project_id': self.project_id.id,
            'client_id': self.client_id.id,
            'client_manager_id': self.client_manager_id,
            'client_specialist_id': self.client_specialist_id.id,
            'prepared_by_id': self.prepared_by_id.id,
            'consultant': self.consultant.id,
            'consultant_pm': self.consultant_pm,
            'subject': self.subject,
            'po_date': self.po_date,
            'po_loi_no': self.po_loi_no,
            'delivery_validity': self.delivery_validity,
            'quotation_validity': self.quotation_validity,
            'initial_contract_amount': self.initial_contract_amount,
            'previously_approved_variation': self.previously_approved_variation,
            'requested_variation_amount': self.requested_variation_amount,
            'accumulated_contract_amount': self.accumulated_contract_amount,
            'current_completion_date': self.current_completion_date,
            'revised_completion_date': self.revised_completion_date,
            'total_amount': self.total_amount,
            'title': self.title,
            'narative_of_work': self.narative_of_work,
            'remarks': self.remarks,
            'amount_in_words': self.amount_in_words,
            'code': self.code,
            'submission_date': self.submission_date,
            'description': self.description,
            'variationID': self.variationID,
            'revision_no': str(self.variationID) + '/REV' + str(current_revision_num),
            'revision_no_seq': str(current_revision_num),
            'parent_variation': self.id if self.revision_no_seq == 0 else self.parent_variation.id,
        })

        self.is_reviewed = True

    @api.model
    def create(self, values):
        # Add code here
        res = super(variationSubmittal, self).create(values)
        prev_variation_num = []
        for rec in self.env['variation.submittal'].search([('project_id','=',res.project_id.id)]).mapped('variation_seq_num'):
            if rec != False:
                prev_variation_num.append(int(rec))

        res.variation_seq_num = max(prev_variation_num) + 1 if prev_variation_num else 1
        seq_const = str('PROJ-') + str(res.projectID) + '/VAR-'
        res.variationID = seq_const + str(res.variation_seq_num)
        if not res.revision_no:
            res.revision_no_seq = 0
            res.revision_no = str(res.variationID) + '/REV' + str(res.revision_no_seq)


        return res

    def open_related_revisions(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'variation.submittal',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'name': 'Revisions',
            'target': 'current',
            'domain': [('parent_variation', '=', self.id)],
            'context': {'create':False },

        }





