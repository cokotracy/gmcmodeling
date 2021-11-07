# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import re
import base64

from binascii import Error as binascii_error
from collections import defaultdict
from operator import itemgetter
from email.utils import formataddr
from odoo.http import request

from odoo import _, api, fields, models, modules, tools
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools import groupby

_logger = logging.getLogger(__name__)
_image_dataurl = re.compile(r'(data:image/[a-z]+?);base64,([a-z0-9+/\n]{3,}=*)\n*([\'"])(?: data-filename="([^"]*)")?',
                            re.I)


class DocumentControlLineCopy(models.Model):
    _name = 'document.control.line.copy'

    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )
    code = fields.Selection(
        [('a', 'Approved as submitted'), ('b', 'Approved with comments'), ('c', 'Revised and Re submitial required'),
         ('d', 'Disapproved see attached sheet'), ('e', 'Under Preview'), ('p', 'Pending')], string='code', default='e')
    product_type = fields.Char(string="Type", required=False, )

    sheet_no = fields.Char(string="Sheet No", required=False, )

    categ_id = fields.Many2one(comodel_name="product.category", string="Category", required=False, )
    copy = fields.Integer(string="Copy", required=False, )
    attachment = fields.Binary(string="Attachment", )
    specification = fields.Many2one(comodel_name="res.partner", string="Specification",
                                    domain=[('supplier_rank', '!=', 0)], required=False, )
    supplier = fields.Text("Supplier")
    description = fields.Char(string="Description", required=False, )
    return_date = fields.Date(string="Return Date", required=False, default=fields.Date.context_today)
    procurement_list_sample_line = fields.Many2one(comodel_name="procurment.list.lines", string="", required=False, )

    doc_count = fields.Integer(compute='_compute_count_of_attachemnt')
    dc_id = fields.Many2one(comodel_name="document.control", string="", required=False, )

    def _compute_count_of_attachemnt(self):
        for d in self:
            if d.id:
                d.doc_count = self.env['procurment.list.lines.attachment'].search_count(
                    [('procurment_line_ref.id', '=', d.procurement_list_sample_line.id)])
            else:
                d.doc_count = 0

    def attachment_view(self):
        self.ensure_one()
        domain = [('procurment_line_ref', '=', self.procurement_list_sample_line.id)]
        return {
            'name': 'Attachments',
            'domain': domain,
            'res_model': 'procurment.list.lines.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_procurment_line_ref': '%s'}" % self.procurement_list_sample_line.id
        }


class DocumentControlLine(models.Model):
    _name = 'document.control.line'

    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )
    code = fields.Selection(
        [('a', 'Approved as submitted'), ('b', 'Approved with comments'), ('c', 'Revised and Re submitial required'),
         ('d', 'Disapproved see attached sheet'), ('e', 'Under Preview'), ('p', 'Pending')], string='code', default='e')
    product_type = fields.Char(string="Type", required=False, )

    sheet_no = fields.Char(string="Sheet No", required=False, )

    categ_id = fields.Many2one(comodel_name="product.category", string="Category", required=False, )
    copy = fields.Integer(string="Copy", required=False, )
    attachment = fields.Binary(string="Attachment", )
    specification = fields.Many2one(comodel_name="res.partner", string="Specification",
                                    domain=[('supplier_rank', '!=', 0)], required=False)
    # def specification_com(self):
    #     dcl=self.env['procurment.list.lines'].search([])
    #     for x in dcl:
    #         self.specification=x.vendor
    #         print("ddddddddddddddddddddddddddddddddddddddddddddd")
    #         print(self.specification.name)
    #         print("ddddddddddddddddddddddddddddddddddddddddddddd")

    # for x in dcl:
    #     if x.vendor:
    #         self.specification=x.vendor
    #         print("ddddddddddddddddddddddddddddddddddddddddddddd")
    #         print(self.specification.name)
    #
    #         print("ddddddddddddddddddddddddddddddddddddddddddddd")
    #
    #     else:
    #         pass
    supplier = fields.Text("Supplier")
    transaction_id = fields.Char(string="Submital Number", compute='get_action_code', required=False, store=True)
    revision_no = fields.Char(string="Revision No", compute='get_action_code', required=False, store=True)
    projectID = fields.Char(string="Project ID", compute='get_action_code', required=False, store=True)
    ref = fields.Char(string="Ref", compute='get_action_code', required=False, store=True)
    project_id = fields.Many2one(comodel_name="project.project", compute='get_action_code', string="Project Name",
                                 required=False, store=True)
    scope_of_work_id = fields.Many2one(comodel_name="work.scope", compute='get_action_code', string="Scope Of Work",
                                       required=False, store=True)
    submittal_type = fields.Selection(string="Submittal Type",
                                      selection=[('dc', 'Document Control'), ('mt', 'Material'), ('dw', 'Drawing'),
                                                 ('hse', 'HSE'), ('rams', 'RAMS')], required=False,
                                      tracking=True)
    submission_date = fields.Date(string="Submission Date", required=False, compute='get_action_code', store=True)
    description = fields.Char(string="Description", required=False, )
    return_date = fields.Date(string="Return Date", required=False, )

    dc_id = fields.Many2one(comodel_name="document.control", string="", required=False, )
    dc_old_id = fields.Many2one(comodel_name="document.control", string="", required=False, )
    procurement_list_sample_line = fields.Many2one(comodel_name="procurment.list.lines", string="", required=False, )

    action_code = fields.Char(string="Action Code", required=False, compute='get_action_code', store=True)

    doc_count = fields.Integer(compute='_compute_count_of_attachemnt')

    def _compute_count_of_attachemnt(self):
        for d in self:
            if d.id:
                d.doc_count = self.env['procurment.list.lines.attachment'].search_count(
                    [('procurment_line_ref.id', '=', d.procurement_list_sample_line.id)])
            else:
                d.doc_count = 0

    def attachment_view(self):
        self.ensure_one()
        domain = [('procurment_line_ref', '=', self.procurement_list_sample_line.id)]
        return {
            'name': 'Attachments',
            'domain': domain,
            'res_model': 'procurment.list.lines.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_procurment_line_ref': '%s'}" % self.procurement_list_sample_line.id
        }

    @api.depends('code', 'product_id')
    def get_action_code(self):
        for rec in self:
            if rec.code == 'a':
                rec.action_code = 'A'
            elif rec.code == 'b':
                rec.action_code = 'B'
            elif rec.code == 'c':
                rec.action_code = 'C'
            elif rec.code == 'd':
                rec.action_code = 'D'
            elif rec.code == 'e':
                rec.action_code = 'E'
            elif rec.code == 'p':
                rec.action_code = 'P'
            else:
                rec.action_code = ' '

            rec.transaction_id = rec.dc_id.transaction_id
            rec.submittal_type = rec.dc_id.submittal_type
            rec.submission_date = rec.dc_id.submission_date
            rec.revision_no = rec.dc_id.revision_no
            rec.projectID = rec.dc_id.projectID
            rec.project_id = rec.dc_id.project_id.id
            rec.ref = rec.dc_id.ref
            rec.scope_of_work_id = rec.dc_id.scope_of_work_id.id


class DocumentControl(models.Model):
    _name = 'document.control'
    _inherit = 'mail.thread'
    _rec_name = 'project_id'
    _description = 'Document Control'

    def get_default_company(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=get_default_company,
                                 required=False, )

    projectID = fields.Char(string="Project ID", required=False, compute='get_project_data', store=True,
                            tracking=True)
    project_id = fields.Many2one(comodel_name="project.project", string="Project Name", required=False,
                                 tracking=True)
    client_id = fields.Many2one(comodel_name="res.partner", string="Client Name", compute='get_project_data',
                                store=True, tracking=True)
    client_specialist_id = fields.Many2one(comodel_name='res.partner', string="Attention", required=False,
                                           tracking=True)
    consultant = fields.Many2one(comodel_name="consultant.consultant", string="Consultant")
    attention = fields.Char(string="Attention", default='Tender Department', required=False,
                            tracking=True)
    prepared_by_id = fields.Many2one(comodel_name="res.users", string="Prepared By", required=False,
                                     tracking=True)
    description = fields.Char(string="Description", required=False, tracking=True,
                              compute="description_compute")

    def description_compute(self):
        dcl = self.env['document.control.line'].search([])
        for x in dcl:
            if x.description:
                self.description = x.description
            else:
                pass

    remarks = fields.Text(string="Remarks", required=False, tracking=True)
    submittal_type = fields.Selection(string="Submittal Type",
                                      selection=[('dc', 'Document Control'), ('mt', 'Material'), ('dw', 'Drawing'),
                                                 ('hse', 'HSE'), ('rams', 'RAMS')], required=False,
                                      tracking=True)
    scope_of_work_id = fields.Many2one(comodel_name="work.scope", string="Scope Of Work", required=False,
                                       tracking=True)
    division = fields.Many2one(comodel_name="division.scope", string="Division", required=False,
                               tracking=True)
    scope_details = fields.Char(string="Scope Details", required=False, tracking=True)
    employee_title = fields.Char(string="Employee Title", compute='get_prepared_by_employee_title', store=True)
    transaction_id = fields.Char(string="Transaction ID", required=False, tracking=True)
    revision_no = fields.Char(string="Revision No", required=False, tracking=True)
    submission_date = fields.Date(string="Submission Date", required=False, default=fields.Date.context_today,
                                  tracking=True)
    specifications = fields.Char(string="Specifications", required=False, tracking=True)

    last_update = fields.Date(string="Last Update", required=False, tracking=True)
    ref = fields.Char(string="Reference", required=False, tracking=True)
    reviewed_by_id = fields.Many2one(comodel_name="hr.employee", string="Reviewed By", required=False,
                                     tracking=True)

    dc_line_ids = fields.One2many(comodel_name="document.control.line", inverse_name="dc_id", string="",
                                  required=False, )
    old_line_ids = fields.One2many(comodel_name="document.control.line", inverse_name="dc_old_id", string="",
                                   required=False, )
    dc_lines_copy = fields.One2many(comodel_name="document.control.line.copy", inverse_name="dc_id", string="",
                                    required=False, )

    trans_dc_seq = fields.Char(string="", required=False, )
    trans_wd_seq = fields.Char(string="", required=False, )
    trans_hse_seq = fields.Char(string="", required=False, )
    trans_rams_seq = fields.Char(string="", required=False, )
    trans_mt_seq = fields.Char(string="", required=False, )
    revision_no_seq = fields.Char(string="")
    is_reviewed = fields.Boolean(string="", )
    parent_dc = fields.Many2one(comodel_name="document.control", string="Parent DC", required=False, )
    procurment_list_id = fields.Many2one(comodel_name="procurment.list", string="", required=False, )
    revisions_num = fields.Integer(string="", compute='get_revisions_num', required=False, )
    mir_counts = fields.Integer(string="", required=False, compute='get_mir_sir_counts')
    sir_counts = fields.Integer(string="", required=False, compute='get_mir_sir_counts')
    x = fields.Boolean()

    mail_partner = fields.Many2many('res.partner', 'partner_values', 'partner_values_id', 'partner_mail_id',
                                    compute="mail_partner_compute")
    subject_2 = fields.Char(string="subjects", compute="mail_partner_compute")
    # Add by omnya 21/06/2021
    state = fields.Selection(selection=[('draft', 'Draft'), ('send_by_email', 'Sent by Email'),
                                        ('pro_list_updated', 'Updated in Procurement List'),
                                        ('resubmitted', 'Resubmitted')], string='Status', default='draft')

    def mail_partner_compute(self):
        for line in self:
            val = []
            val.append((6, 0, [line.client_specialist_id.id, line.project_id.partner_id.id,
                               line.prepared_by_id.partner_id.id]))
            self.mail_partner = val
            self.subject_2 = self.transaction_id + "/" + self.description

    @api.depends('project_id')
    def get_project_data(self):
        self.client_id = self.project_id.partner_id.id
        self.projectID = self.project_id.project_no

    @api.depends('prepared_by_id')
    def get_prepared_by_employee_title(self):
        employee_title = ''
        for rec in self.env['hr.employee'].search([('user_id', '=', self.prepared_by_id.id)], limit=1):
            employee_title = rec.job_id.name
        self.employee_title = employee_title

    def action_dc_send(self):

        self.ensure_one()

        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference("wc_document_control", 'email_template_document_control')[
                1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'document.control',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'proforma': self.env.context.get('proforma', True),
            'force_email': True,
            'default_partner_ids': self.mail_partner.ids,
            'default_subject': self.subject_2,
        }
        self.state = 'send_by_email'
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.depends('mir_counts', 'sir_counts')
    def get_mir_sir_counts(self):
        for rec in self:
            rec.mir_counts = self.env['mir.submittal'].search_count([('dc_id', '=', self.id)])
            rec.sir_counts = self.env['sir.submittal'].search_count([('dc_id', '=', self.id)])

    def create_mir(self):
        mir = self.env['mir.submittal']
        mir_lines = []
        if self.dc_line_ids:

            for dc_line in self.dc_line_ids:
                mir_lines.append((0, 0, {
                    'product_id': dc_line.product_id.id,
                }))
        else:
            for dc_line_copy in self.dc_lines_copy:
                mir_lines.append((0, 0, {
                    'product_id': dc_line_copy.product_id.id,
                }))

        mir.create({

            'projectID': self.projectID,
            'project_id': self.project_id.id,
            'client_id': self.client_id.id,
            'client_specialist_id': self.client_specialist_id.id,
            'prepared_by_id': self.env.user.id,
            'description': self.description,
            'submittal_type': self.submittal_type,
            'scope_of_work_id': self.scope_of_work_id.id,
            'scope_division': self.division.id,
            'scope_details': self.scope_details,
            'consultant': self.consultant.id,
            'submission_date': self.submission_date,
            'mir_line_ids': mir_lines,
            'dc_id': self.id,
        })

    def create_sir(self):
        sir = self.env['sir.submittal']
        sir_lines = []
        if self.dc_line_ids:
            for dc_line in self.dc_line_ids:
                sir_lines.append((0, 0, {
                    'product_id': dc_line.product_id.id,
                }))
        else:
            for dc_line_copy in self.dc_lines_copy:
                sir_lines.append((0, 0, {
                    'product_id': dc_line_copy.product_id.id,
                }))

        sir.create({

            'projectID': self.projectID,
            'project_id': self.project_id.id,
            'client_id': self.client_id.id,
            'client_specialist_id': self.client_specialist_id.id,
            'prepared_by_id': self.env.user.id,
            'description_work': self.description,
            'consultant': self.consultant.id,
            'scope_of_work_id': self.scope_of_work_id.id,
            'scope_division': self.division.id,
            'submission_date': self.submission_date,
            'sir_line_ids': sir_lines,
            'dc_id': self.id,

        })

    @api.depends('revisions_num')
    def get_revisions_num(self):
        self.revisions_num = self.env['document.control'].search_count([('parent_dc', '=', self.id)])

    def resbmittal_button(self):
        if not self.is_reviewed:
            dc = self.env['document.control']
            dc_lines_copy = []
            for dc_line in self.dc_line_ids:
                dc_lines_copy.append((0, 0, {
                    'product_id': dc_line.product_id.id,
                    'code': dc_line.code,
                    'sheet_no': dc_line.sheet_no,
                    'description': dc_line.description,
                    'categ_id': dc_line.categ_id.id,
                    'product_type': dc_line.product_type,
                    'copy': dc_line.copy,
                    'attachment': dc_line.attachment,
                    'specification': dc_line.specification.id,
                    'supplier': dc_line.supplier,
                    'return_date': dc_line.return_date,
                }))
            self.update({'dc_lines_copy': dc_lines_copy})

            revision_no = []
            if int(self.revision_no_seq) == 0:
                current_revision_num = 1
            else:
                for record in self.env['document.control'].search([('parent_dc', '=', self.parent_dc.id)]):
                    revision_no.append(int(record.revision_no_seq))
                current_revision_num = max(revision_no) + 1 if revision_no else 1
            dc.create({
                'projectID': self.projectID,
                'project_id': self.project_id.id,
                'client_id': self.client_id.id,
                'client_specialist_id': self.client_specialist_id.id,
                'prepared_by_id': self.env.user.id,
                'description': self.description,
                'remarks': self.remarks,
                'submittal_type': self.submittal_type,
                'scope_of_work_id': self.scope_of_work_id.id,
                'division': self.division.id,
                'scope_details': self.scope_details,
                'employee_title': self.employee_title,
                'transaction_id': self.transaction_id,
                'revision_no': str(self.transaction_id) + '/REV' + str(current_revision_num),
                'revision_no_seq': str(current_revision_num),
                'submission_date': self.submission_date,
                'specifications': '',
                'procurment_list_id': self.procurment_list_id.id,
                'dc_line_ids': self.dc_line_ids.ids,
                'parent_dc': self.id if self.revision_no_seq == '0' else self.parent_dc.id,
            })

            self.is_reviewed = True

    def update_procurment_list_sample_lines(self):
        self.x = "True"
        new_lines_add = []
        for rec in self.dc_line_ids:
            if rec.id not in self.old_line_ids.ids:
                # if rec.code in ['a','b']:
                new_lines_add.append((0, 0, {
                    'product': rec.product_id.id,
                    'submittal_type': self.submittal_type,
                    'scope_of_work_id': self.scope_of_work_id.id,
                    'code': rec.code,
                    'is_dc_updated': True,
                    'vendor': rec.specification.id,
                }))

        procurement_list_record = None
        procuremnt_rec = self.env['procurment.list'].search([('id', '=', self.procurment_list_id.id)])
        for line in procuremnt_rec:
            line.update({'sub_procurement_lines': new_lines_add})
            procurement_list_record = line
        for line2_update in procuremnt_rec:
            for dc_lines in self.dc_line_ids:
                for proc_line in line2_update.sub_procurement_lines:
                    if proc_line.id == dc_lines.procurement_list_sample_line.id:
                        proc_line.code = dc_lines.code
                        proc_line.returned_date = dc_lines.return_date
                        proc_line.vendor = dc_lines.specification.id

                for proc_line2 in line2_update.procurment_lines:
                    if proc_line2.id == dc_lines.procurement_list_sample_line.id:
                        proc_line2.code = dc_lines.code
                        proc_line2.returned_date = dc_lines.return_date
                        proc_line2.vendor = dc_lines.specification.id
                        proc_line2.note = dc_lines.dc_id.remarks

        self.old_line_ids = self.dc_line_ids.ids
        if procurement_list_record != None:
            if False not in new_lines_add:
                technical_users = []
                technical_group = self.env.ref('wc_document_control.technical_office_group').users
                for user in technical_group:
                    technical_users.append(user.partner_id.id)
                thread_pool = self.env['mail.thread']
                if False not in technical_users:
                    thread_pool.sudo().message_notify(
                        partner_ids=technical_users,
                        subject="Procurement List And DC Notification",
                        body='There is new lines add to this procurement list: <a target=_BLANK href="/web?#id=' + str(
                            procurement_list_record.id) + '&view_type=form&model=procurment.list&action=" style="font-weight: bold">' + str(
                            procurement_list_record.name.name) + '</a>',
                        # email_from=self.env.user.company_id.catchall or self.env.user.company_id.email, )
                        email_from=self.env.user.company_id.email, )

        self.state = 'pro_list_updated'

    def update_procurment_list_sample_lines2(self):
        new_lines_add = []
        for rec in self.dc_line_ids:
            if rec.id not in self.old_line_ids.ids:
                # if rec.code in ['a','b']:
                new_lines_add.append((0, 0, {
                    'product': rec.product_id.id,
                    'submittal_type': self.submittal_type,
                    'scope_of_work_id': self.scope_of_work_id.id,
                    'code': rec.code,
                    'is_dc_updated': True,
                    'vendor': rec.specification.id,
                }))

        procurement_list_record = None
        procuremnt_rec = self.env['procurment.list'].search([('id', '=', self.procurment_list_id.id)])
        for line in procuremnt_rec:
            line.update({'sub_procurement_lines': new_lines_add})
            procurement_list_record = line
        for line2_update in procuremnt_rec:
            for dc_lines in self.dc_line_ids:
                for proc_line in line2_update.sub_procurement_lines:
                    if proc_line.id == dc_lines.procurement_list_sample_line.id:
                        proc_line.code = dc_lines.code
                        proc_line.returned_date = dc_lines.return_date
                        proc_line.vendor = dc_lines.specification.id

                for proc_line2 in line2_update.procurment_lines:
                    if proc_line2.id == dc_lines.procurement_list_sample_line.id:
                        proc_line2.code = dc_lines.code
                        proc_line2.returned_date = dc_lines.return_date
                        proc_line2.vendor = dc_lines.specification.id
                        proc_line2.note = dc_lines.dc_id.remarks

        self.old_line_ids = self.dc_line_ids.ids
        if procurement_list_record != None:
            if False not in new_lines_add:
                technical_users = []
                technical_group = self.env.ref('wc_document_control.technical_office_group').users
                for user in technical_group:
                    technical_users.append(user.partner_id.id)
                thread_pool = self.env['mail.thread']
                if False not in technical_users:
                    thread_pool.sudo().message_notify(
                        partner_ids=technical_users,
                        subject="Procurement List And DC Notification",
                        body='There is new lines add to this procurement list: <a target=_BLANK href="/web?#id=' + str(
                            procurement_list_record.id) + '&view_type=form&model=procurment.list&action=" style="font-weight: bold">' + str(
                            procurement_list_record.name.name) + '</a>',
                        # email_from=self.env.user.company_id.catchall or self.env.user.company_id.email, )
                        email_from=self.env.user.company_id.email, )
    @api.model
    def create(self, values):
        res = super(DocumentControl, self).create(values)
        if not res.transaction_id:
            seq_const = str('PROJ-') + str(res.projectID) + '/' + str(res.scope_of_work_id.code) + '/'

            if res.submittal_type == 'mt':
                res.transaction_id = seq_const + str('TRMT-')
                mt_control = self.env['document.control'].search([('project_id', '=', res.project_id.id),
                                                                  ('scope_of_work_id', '=', res.scope_of_work_id.code),
                                                                  ('transaction_id', 'ilike', res.transaction_id),
                                                                  ('id', '!=', res.id)],
                                                                 order='trans_mt_seq desc',
                                                                 limit=1)
                res.trans_mt_seq = int(mt_control.trans_mt_seq) + 1 if mt_control else 1
                res.transaction_id += str(res.trans_mt_seq)

            if res.submittal_type == 'dc':
                res.transaction_id = seq_const + str('TRDC-')
                dc_control = self.env['document.control'].search([('project_id', '=', res.project_id.id),
                                                                  ('scope_of_work_id', '=', res.scope_of_work_id.code),
                                                                  ('transaction_id', 'ilike', res.transaction_id),
                                                                  ('id', '!=', res.id)],
                                                                 order='trans_dc_seq desc',
                                                                 limit=1)
                res.trans_dc_seq = int(dc_control.trans_dc_seq) + 1 if dc_control else 1
                res.transaction_id += str(res.trans_dc_seq)

            if res.submittal_type == 'dw':
                res.transaction_id = seq_const + str('TRDW-')
                dw_control = self.env['document.control'].search([('project_id', '=', res.project_id.id),
                                                                  ('scope_of_work_id', '=', res.scope_of_work_id.code),
                                                                  ('transaction_id', 'ilike', res.transaction_id),
                                                                  ('id', '!=', res.id)],
                                                                 order='trans_wd_seq desc',
                                                                 limit=1)
                res.trans_wd_seq = int(dw_control.trans_wd_seq) + 1 if dw_control else 1
                res.transaction_id += str(res.trans_wd_seq)

            if res.submittal_type == 'hse':
                res.transaction_id = seq_const + str('HSE-')
                hse_control = self.env['document.control'].search([('project_id', '=', res.project_id.id),
                                                                   ('scope_of_work_id', '=', res.scope_of_work_id.code),
                                                                   ('transaction_id', 'ilike', res.transaction_id),
                                                                   ('id', '!=', res.id)],
                                                                  order='trans_hse_seq desc',
                                                                  limit=1)
                res.trans_hse_seq = int(hse_control.trans_hse_seq) + 1 if hse_control else 1
                res.transaction_id += str(res.trans_hse_seq)

            if res.submittal_type == 'rams':
                res.transaction_id = seq_const + str('RAMS-')
                rams_control = self.env['document.control'].search([('project_id', '=', res.project_id.id),
                                                                    ('scope_of_work_id', '=',
                                                                     res.scope_of_work_id.code),
                                                                    ('transaction_id', 'ilike', res.transaction_id),
                                                                    ('id', '!=', res.id)],
                                                                   order='trans_rams_seq desc',
                                                                   limit=1)
                res.trans_rams_seq = int(rams_control.trans_rams_seq) + 1 if rams_control else 1
                res.transaction_id += str(res.trans_rams_seq)

        if not res.revision_no:
            res.revision_no_seq = 0
            res.revision_no = str(res.transaction_id) + '/REV' + str(res.revision_no_seq)

        res.scope_details = str(dict(res._fields['submittal_type'].selection).get(res.submittal_type)) + '/' + str(
            res.scope_of_work_id.code or '') + '/' + str(res.division.name or '')

        res.old_line_ids = res.dc_line_ids.ids

        return res

    def open_related_revisions(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'document.control',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'name': 'Revisions',
            'target': 'current',
            'domain': [('parent_dc', '=', self.id)],
            'context': {'create': False},

        }

    def open_related_sirs(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sir.submittal',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'name': 'SIR',
            'target': 'current',
            'domain': [('dc_id', '=', self.id)],
            'context': {'create': False},

        }

    def open_related_mirs(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mir.submittal',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'name': 'MIR',
            'target': 'current',
            'domain': [('dc_id', '=', self.id)],
            'context': {'create': False},

        }


class WorkScope(models.Model):
    _name = 'work.scope'
    _rec_name = 'name'
    _description = ''

    name = fields.Char(string="Name", required=False, )
    code = fields.Char(string="Code", required=False, )


class Division(models.Model):
    _name = 'division.scope'
    _rec_name = 'name'
    _description = ''

    name = fields.Char(string="Name", required=False, )


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def _message_read_dict_postprocess(self, messages, message_tree):
        """ Post-processing on values given by message_read. This method will
            handle partners in batch to avoid doing numerous queries.

            :param list messages: list of message, as get_dict result
            :param dict message_tree: {[msg.id]: msg browse record as super user}
        """
        # 1. Aggregate partners (author_id and partner_ids), attachments and tracking values
        partners = self.env['res.partner'].sudo()
        attachments = self.env['ir.attachment']
        message_ids = list(message_tree.keys())
        email_notification_tree = {}
        # By rebrowsing all the messages at once, we ensure all the messages
        # to be on the same prefetch group, enhancing that way the performances
        for message in self.sudo().browse(message_ids):
            if message.author_id:
                partners |= message.author_id
            # find all notified partners
            email_notification_tree[message.id] = message.notification_ids.filtered(
                lambda n: n.notification_type == 'email' and n.res_partner_id.active and
                          (n.notification_status in (
                              'bounce', 'exception', 'canceled') or n.res_partner_id.partner_share))
            if message.attachment_ids:
                attachments |= message.attachment_ids
        partners |= self.env['mail.notification'].concat(*email_notification_tree.values()).mapped('res_partner_id')
        # Read partners as SUPERUSER -> message being browsed as SUPERUSER it is already the case
        partners_names = partners.name_get()
        partner_tree = dict((partner[0], partner) for partner in partners_names)

        # 2. Attachments as SUPERUSER, because could receive msg and attachments for doc uid cannot see
        attachments_data = attachments.sudo().read(['id', 'name', 'mimetype'])
        safari = request and request.httprequest.user_agent.browser == 'safari'
        attachments_tree = dict((attachment['id'], {
            'id': attachment['id'],
            'filename': attachment['name'],
            'name': attachment['name'],
            'mimetype': 'application/octet-stream' if safari and attachment['mimetype'] and 'video' in attachment[
                'mimetype'] else attachment['mimetype'],
        }) for attachment in attachments_data)

        # 3. Tracking values
        tracking_values = self.env['mail.tracking.value'].sudo().search([('mail_message_id', 'in', message_ids)])
        message_to_tracking = dict()
        tracking_tree = dict.fromkeys(tracking_values.ids, False)
        for tracking in tracking_values:
            groups = tracking.field_groups
            if not groups or self.env.is_superuser() or self.user_has_groups(groups):
                message_to_tracking.setdefault(tracking.mail_message_id.id, list()).append(tracking.id)
                tracking_tree[tracking.id] = {
                    'id': tracking.id,
                    'changed_field': tracking.field_desc,
                    'old_value': tracking.get_old_display_value()[0],
                    'new_value': tracking.get_new_display_value()[0],
                    'field_type': tracking.field_type,
                }

        # 4. Update message dictionaries
        for message_dict in messages:
            message_id = message_dict.get('id')
            message = message_tree[message_id]
            if message.author_id:
                author = partner_tree[message.author_id.id]
            else:
                author = (0, message.email_from)
            customer_email_status = (
                    (all(n.notification_status == 'sent' for n in message.notification_ids if
                         n.notification_type == 'email') and 'sent') or
                    (any(n.notification_status == 'exception' for n in message.notification_ids if
                         n.notification_type == 'email') and 'exception') or
                    (any(n.notification_status == 'bounce' for n in message.notification_ids if
                         n.notification_type == 'email') and 'bounce') or
                    'ready'
            )
            customer_email_data = []
            for notification in email_notification_tree[message.id]:
                customer_email_data.append((partner_tree[notification.res_partner_id.id][0],
                                            partner_tree[notification.res_partner_id.id][1],
                                            notification.notification_status))

            attachment_ids = []
            main_attachment = None
            if message.attachment_ids:
                has_access_to_model = message.model and self.env[message.model].check_access_rights('read',
                                                                                                    raise_exception=False)
                if message.res_id and issubclass(self.pool[message.model],
                                                 self.pool['mail.thread']) and has_access_to_model:
                    main_attachment = self.env[message.model].browse(message.res_id).message_main_attachment_id
                for attachment in message.attachment_ids:
                    if attachment.id in attachments_tree:
                        attachments_tree[attachment.id]['is_main'] = main_attachment == attachment
                        attachment_ids.append(attachments_tree[attachment.id])

            tracking_value_ids = []
            for tracking_value_id in message_to_tracking.get(message_id, list()):
                if tracking_value_id in tracking_tree:
                    tracking_value_ids.append(tracking_tree[tracking_value_id])

            message_dict.update({
                'author_id': author,
                'customer_email_status': customer_email_status,
                'customer_email_data': customer_email_data,
                'attachment_ids': attachment_ids,
                'tracking_value_ids': tracking_value_ids,
            })

        return True


class DocumentControl2(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def get_record_data(self, values):
        """ Returns a defaults-like dict with initial values for the composition
        wizard when sending an email related a previous email (parent_id) or
        a document (model, res_id). This is based on previously computed default
        values. """
        result, subject = {}, False
        if values.get('parent_id'):
            parent = self.env['mail.message'].browse(values.get('parent_id'))
            result['record_name'] = parent.record_name,
            subject = tools.ustr(parent.subject or parent.record_name or '')
            if not values.get('model'):
                result['model'] = parent.model
            if not values.get('res_id'):
                result['res_id'] = parent.res_id
            partner_ids = values.get('partner_ids', list()) + parent.partner_ids.ids
            result['partner_ids'] = partner_ids

        elif values.get('model') and values.get('res_id'):
            doc_name_get = self.env[values.get('model')].browse(values.get('res_id')).name_get()
            result['record_name'] = doc_name_get and doc_name_get[0][1] or ''
            subject = tools.ustr(result['record_name'])
        # re_prefix = _('Re:')
        # if subject and not (subject.startswith('Re:') or subject.startswith(re_prefix)):
        #     subject = "%s %s" % (re_prefix, subject)
        # result['subject'] = subject

        return result


class DocumentControl27(models.Model):
    _inherit = 'mail.template'

    def generate_recipients(self, results, res_ids):
        """Generates the recipients of the template. Default values can ben generated
        instead of the template values if requested by template or context.
        Emails (email_to, email_cc) can be transformed into partners if requested
        in the context. """
        self.ensure_one()

        if self.use_default_to or self._context.get('tpl_force_default_to'):
            records = self.env[self.model].browse(res_ids).sudo()
            default_recipients = self.env['mail.thread']._message_get_default_recipients_on_records(records)
            for res_id, recipients in default_recipients.items():
                results[res_id].pop('partner_to', None)
                results[res_id].update(recipients)

        records_company = None
        if self._context.get('tpl_partners_only') and self.model and results and 'company_id' in self.env[
            self.model]._fields:
            records = self.env[self.model].browse(results.keys()).read(['company_id'])
            records_company = {rec['id']: (rec['company_id'][0] if rec['company_id'] else None) for rec in records}

        for res_id, values in results.items():
            partner_ids = values.get('partner_ids', list())
            if self._context.get('tpl_partners_only'):
                mails = tools.email_split(values.pop('email_to', '')) + tools.email_split(values.pop('email_cc', ''))
                Partner = self.env['res.partner']
                if records_company:
                    Partner = Partner.with_context(default_company_id=records_company[res_id])
                # for mail in mails:
                #     partner_id = Partner.find_or_create(mail)
                #     partner_ids.append(partner_id)
            values.pop('partner_to', '')
            partner_to = self.env['document.control'].mail_partner.ids

            if partner_to:
                # placeholders could generate '', 3, 2 due to some empty field values
                # tpl_partner_ids = [int(pid) for pid in partner_to.split(',') if pid]
                tpl_partner_ids = self.env['document.control'].mail_partner.ids

                partner_ids += self.env['res.partner'].sudo().browse(tpl_partner_ids).exists().ids
            results[res_id]['partner_ids'] = partner_ids
        return results
    

