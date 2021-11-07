# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date


class ProcurementList(models.Model):
    _inherit = 'procurment.list'

    client_specialist_id = fields.Many2one(comodel_name="res.partner", string="Client Specialist", required=False, )
    consultant = fields.Many2one(comodel_name="consultant.consultant", string="Consultant")

    @api.onchange('name')
    def get_clien_specialist(self):
        self.client_specialist_id = self.name.client_specialist_id.id

    # ADD By Ahmed Mokhlef
    def create_dc(self):
        document_control = self.env['document.control']
        submittal_mapped_lines = self.sub_procurement_lines.mapped('submittal_type') + self.procurment_lines.mapped(
            'submittal_type')
        work_scope_mapped_lines = self.sub_procurement_lines.mapped('scope_of_work_id') + self.procurment_lines.mapped(
            'scope_of_work_id')
        division_mapped_lines = self.sub_procurement_lines.mapped('division') + self.procurment_lines.mapped('division')

        for type in set(submittal_mapped_lines):
            for work_scope in set(work_scope_mapped_lines):
                for division in set(division_mapped_lines):
                    dc_lines = []
                    submital_type = None
                    scope_of_work_id = None
                    division_id = None
                    submital_type = str(type)
                    scope_of_work_id = work_scope
                    division_id = division
                    for line in self.sub_procurement_lines:
                        print('000000000000000000')
                        if not line.is_submittaled:
                            print('000011111')
                            if line.submittal_type == str(
                                    type) and line.scope_of_work_id == work_scope and line.division == division and line.submittal_type and line.scope_of_work_id:
                                print('00000000333333')
                                dc_lines.append((0, 0, {
                                    'product_id': line.product.id,
                                    'code': 'e',
                                    'description': line.product.name,
                                    'categ_id': line.product.categ_id.id,
                                    'procurement_list_sample_line': line.id,
                                    'specification': line.vendor.id
                                }))
                                line.is_submittaled = True
                                line.code = 'p'

                    for line2 in self.procurment_lines:
                        print('1111111111111111')
                        if not line2.is_submittaled:
                            print('222222222222222')
                            if line2.submittal_type == str(
                                    type) and line2.scope_of_work_id == work_scope and line2.division == division and line2.submittal_type and line2.scope_of_work_id:
                                print('33333333333333')
                                dc_lines.append((0, 0, {
                                    'product_id': line2.product.id,
                                    'code': 'e',
                                    'description': line2.product.name,
                                    'categ_id': line2.product.categ_id.id,
                                    'procurement_list_sample_line': line2.id,
                                    'specification': line2.vendor.id
                                }))
                                line2.is_submittaled = True
                                line2.code = 'p'

                    if dc_lines:
                        created_record = document_control.sudo().create({
                            'projectID': self.project_no,
                            'project_id': self.name.id,
                            'client_id': self.partner_id.id,
                            'client_specialist_id': self.client_specialist_id.id,
                            'attention': 'Tender Department',
                            'consultant': self.consultant.id,
                            'prepared_by_id': self.env.user.id,
                            'description': '',
                            'remarks': '',
                            'submittal_type': submital_type,
                            'scope_of_work_id': scope_of_work_id.id,
                            'division': division_id.id,
                            'submission_date': date.today(),
                            'specifications': '',
                            'procurment_list_id': self.id,
                            'dc_line_ids': dc_lines,
                        })


class ProcurementListLines(models.Model):
    _inherit = 'procurment.list.lines'

    _order = "sequance"

    # add by Ahmed Mokhlef
    submittal_type = fields.Selection(string="DC Type",
                                      selection=[('dc', 'Document Control'), ('mt', 'Material'), ('dw', 'Drawing')],
                                      required=False, )
    scope_of_work_id = fields.Many2one(comodel_name="work.scope", string="Scope Of Work", required=False, )
    division = fields.Many2one(comodel_name="division.scope", string="Division", required=False,
                               tracking=True)

    is_submittaled = fields.Boolean(string="", )
    is_dc_updated = fields.Boolean(string="", )

    action_code = fields.Char(string="Action Code", required=False, compute='get_action_code', store=True)

    sequance = fields.Integer()

    @api.depends('code', 'product')
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

    def create_submittal(self):
        for line in self:
            dc_lines = []
            document_control = self.env['document.control']
            if line.product:
                if not line.is_submittaled:
                    dc_lines.append((0, 0, {
                        'product_id': line.product.id,
                        'code': 'e',
                        'description': line.product.name,
                        'categ_id': line.product.categ_id.id,
                        'procurement_list_sample_line': line.id,
                        'specification': line.vendor.id
                    }))

                    document_control.sudo().create({
                        'projectID': line.sub_procurement_id.project_no if line.sub_procurement_id else line.procurment_id.project_no,
                        'project_id': line.sub_procurement_id.name.id if line.sub_procurement_id else line.procurment_id.name.id,
                        'client_id': line.sub_procurement_id.partner_id.id if line.sub_procurement_id else line.procurment_id.partner_id.id,
                        'client_specialist_id': line.sub_procurement_id.client_specialist_id.id if line.sub_procurement_id else line.procurment_id.client_specialist_id.id,
                        'consultant': line.sub_procurement_id.consultant.id if line.sub_procurement_id else line.procurment_id.consultant.id,
                        'attention': 'Tender Department',
                        'prepared_by_id': self.env.user.id,
                        'description': '',
                        'remarks': '',
                        'submittal_type': line.submittal_type,
                        'scope_of_work_id': line.scope_of_work_id.id,
                        'division': line.division.id,
                        'submission_date': date.today(),
                        'specifications': line.vendor,
                        'procurment_list_id': line.sub_procurement_id.id if line.sub_procurement_id else line.procurment_id.id,
                        'dc_line_ids': dc_lines,
                    })
                    line.is_submittaled = True
                    line.code = 'p'
