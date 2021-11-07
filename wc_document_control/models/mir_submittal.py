# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime,date

class MIRLinesCopy(models.Model):
    _name = 'mir.line.copy'

    product_id = fields.Many2one(comodel_name="product.product", string="Item/Qty Required", required=False, )
    delivered_qty = fields.Float(string="Delivered Quantity",  required=False, )
    delivered_note = fields.Text(string="Delivered Note", required=False, )
    test_or_mill_certificate = fields.Char(string="Test/Mill Certificate", required=False, )
    action = fields.Char(string="Action", required=False, )

    mir_id = fields.Many2one(comodel_name="mir.submittal", string="", required=False, )


class MIRLines(models.Model):
    _name = 'mir.line'

    product_id = fields.Many2one(comodel_name="product.product", string="Item/Qty Required", required=False, )
    delivered_qty = fields.Float(string="Delivered Quantity",  required=False, )
    delivered_note = fields.Text(string="Delivered Note", required=False, )
    test_or_mill_certificate = fields.Char(string="Test/Mill Certificate", required=False, )
    action = fields.Char(string="Action", required=False, )

    mir_id = fields.Many2one(comodel_name="mir.submittal", string="", required=False, )

    mirID = fields.Char(string="mirID", compute='get_action_code', required=False, store=True)
    revision_no = fields.Char(string="Revision No", compute='get_action_code', required=False, store=True)
    projectID = fields.Char(string="Project ID", compute='get_action_code', required=False, store=True)
    project_id = fields.Many2one(comodel_name="project.project", compute='get_action_code', string="Project Name",
                                 required=False, store=True)
    scope_of_work_id = fields.Many2one(comodel_name="work.scope", compute='get_action_code', string="Scope Of Work",
                                       required=False, store=True)
    submittal_type = fields.Selection(string="Submittal Type",
                                      selection=[('dc', 'Document Control'), ('mt', 'Material'), ('dw', 'Drawing')],
                                      compute='get_action_code', required=False, store=True)
    submission_date = fields.Date(string="Submission Date", required=False, compute='get_action_code', store=True)
    description = fields.Char(string="Description", required=False, )

    dc_id = fields.Many2one(comodel_name="document.control", string="", required=False, )
    dc_old_id = fields.Many2one(comodel_name="document.control", string="", required=False, )
    procurement_list_sample_line = fields.Many2one(comodel_name="procurment.list.lines", string="", required=False, )

    @api.depends( 'mir_id','product_id','delivered_qty')
    def get_action_code(self):
        for rec in self:
            rec.mirID = rec.mir_id.mirID
            rec.submittal_type = rec.mir_id.submittal_type
            rec.submission_date = rec.mir_id.submission_date
            rec.revision_no = rec.mir_id.revision_no
            rec.projectID = rec.mir_id.projectID
            rec.project_id = rec.mir_id.project_id.id
            rec.scope_of_work_id = rec.mir_id.scope_of_work_id.id


class MIRSubmittal(models.Model):
    _name = 'mir.submittal'
    _inherit = 'mail.thread'

    def get_default_company(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=get_default_company,
                                 required=False, )

    projectID = fields.Char(string="Project ID", required=False, )
    project_id = fields.Many2one(comodel_name="project.project", string="Project Name", required=False, )
    client_id = fields.Many2one(comodel_name="res.partner", string="Client Name", required=False, )
    client_manager_id = fields.Char(string="Client Manager", required=False, )
    consultant = fields.Many2one(comodel_name="consultant.consultant", string="Consultant")

    client_specialist_id = fields.Many2one(comodel_name='res.partner',string="Attention", required=False, )

    prepared_by_id = fields.Many2one(comodel_name="res.users", string="Prepared By", required=False, )
    discipline = fields.Char(string="Discipline", required=False, )
    subject = fields.Char(string="Subject", required=False, )
    description = fields.Text(string="Description", required=False, )
    submittal_type = fields.Selection(string="Submittal Type", selection=[('dc', 'Document Control'), ('mt', 'Material'),('dw','Drawing') ], required=False, )
    scope_of_work_id = fields.Many2one(comodel_name="work.scope", string="Scope Of Work", required=False, )
    scope_division = fields.Many2one(comodel_name="division.scope",string="Scope Division", required=False, )
    scope_details = fields.Char(string="Scope Details", required=False, )
    code = fields.Selection(
        [('e', 'UNDER REVIEW'), ('a', 'RELEASED'), ('b', 'RELEASED AS NOTED'),
         ('C', 'REJECTED')], string='Status',default='e')
    location = fields.Char(string="Location", required=False, )
    mirID = fields.Char(string="MIR ID", required=False, )
    revision_no = fields.Char(string="Revision No", required=False, )
    submission_date = fields.Date(string="Submisstion Date", required=False, )
    drawing_ref = fields.Char(string="Drawing Reference", required=False, )
    supplier = fields.Char(string="Supplier", required=False, )
    manufacturer = fields.Char(string="Manufacturer", required=False, )
    mir_line_ids = fields.One2many(comodel_name="mir.line", inverse_name="mir_id", string="", required=False, )
    mir_line_copy_ids = fields.One2many(comodel_name="mir.line.copy", inverse_name="mir_id", string="", required=False, )

    mir_seq_num = fields.Integer(string="", required=False, )
    trans_mt_seq = fields.Integer(string="", )
    trans_dc_seq = fields.Integer(string="", )
    trans_wd_seq = fields.Integer(string="", )
    parent_mir = fields.Many2one(comodel_name="mir.submittal", string="", required=False, )
    revision_no_seq = fields.Integer(string="", required=False, )
    is_reviewed = fields.Boolean(string="", )
    revisions_num = fields.Integer(string="", compute='get_revisions_num', required=False, )
    dc_id = fields.Many2one(comodel_name="document.control", string="", required=False, )

    def action_dc_send(self):

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference("wc_document_control", 'email_template_mir_submittal')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'mir.submittal',
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
        self.revisions_num = self.env['mir.submittal'].search_count([('parent_mir', '=', self.id)])

    @api.onchange('project_id')
    def get_project_data(self):
        self.projectID = self.project_id.project_no

    def resbmittal_button(self):
        mir = self.env['mir.submittal']
        mir_lines_copy = []
        for mir_line in self.mir_line_ids:
            mir_lines_copy.append((0, 0, {
                'product_id': mir_line.product_id.id,
                'delivered_qty': mir_line.delivered_qty,
                'delivered_note': mir_line.delivered_note,
                'test_or_mill_certificate': mir_line.test_or_mill_certificate,
                'action': mir_line.action,
            }))
        self.update({'mir_line_copy_ids': mir_lines_copy})

        revision_no = []
        if int(self.revision_no_seq) == 0:
            current_revision_num = 1
        else:
            for record in self.env['mir.submittal'].search([('parent_mir', '=', self.parent_mir.id)]):
                revision_no.append(int(record.revision_no_seq))
            current_revision_num = max(revision_no) + 1 if revision_no else 1

        mir.create({

            'projectID': self.projectID,
            'project_id': self.project_id.id,
            'client_id': self.client_id.id,
            'client_manager_id': self.client_manager_id,
            'client_specialist_id': self.client_specialist_id.id,
            'prepared_by_id': self.prepared_by_id.id,
            'discipline': self.discipline,
            'consultant': self.consultant.id,
            'consultant_mp': self.consultant_mp,
            'subject': self.subject,
            'description': self.description,
            'submittal_type': self.submittal_type,
            'scope_of_work_id': self.scope_of_work_id.id,
            'scope_division': self.scope_division.id,
            'scope_details': self.scope_details,
            'code': self.code,
            'location': self.location,
            'mirID': self.mirID,
            'revision_no': str(self.mirID) + '/REV' + str(current_revision_num),
            'submission_date':self.submission_date,
            'drawing_ref':self.drawing_ref,
            'supplier':self.supplier,
            'manufacturer':self.manufacturer,
            'revision_no_seq': str(current_revision_num),
            'parent_mir': self.id if self.revision_no_seq == 0 else self.parent_mir.id,
            'mir_line_ids': self.mir_line_ids.ids,
        })

        self.is_reviewed = True

    @api.model
    def create(self, values):
        # Add code here
        res = super(MIRSubmittal, self).create(values)
        if not res.mirID:
            prev_trans_mt_num = []
            prev_trans_dc_num = []
            prev_trans_wd_num = []
            for rec in self.env['mir.submittal'].search([('project_id','=',res.project_id.id)]):
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
                res.mirID = seq_const + str('MIRMT-') + str(res.trans_mt_seq)
            if res.submittal_type == 'dc':
                res.trans_dc_seq = max(prev_trans_dc_num) + 1 if prev_trans_dc_num else 1
                res.mirID = seq_const + str('MIRDC-') + str(res.trans_dc_seq)
            if res.submittal_type == 'dw':
                res.trans_wd_seq = max(prev_trans_wd_num) + 1 if prev_trans_wd_num else 1
                res.mirID = seq_const + str('MIRDW-') + str(res.trans_wd_seq)

            res.scope_details = str(dict(res._fields['submittal_type'].selection).get(res.submittal_type)) + '/' + str(
                res.scope_of_work_id.code or '') + '/' + str(res.scope_division.name or '')

        if not res.revision_no:
            res.revision_no_seq = 0
            res.revision_no = str(res.mirID) + '/REV' + str(res.revision_no_seq)




        return res

    def open_related_revisions(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mir.submittal',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'name': 'Revisions',
            'target': 'current',
            'domain': [('parent_mir', '=', self.id)],
            'context': {'create':False },

        }





