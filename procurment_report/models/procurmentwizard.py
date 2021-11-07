# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _ , api
import datetime
from datetime import timedelta, date

class Procurmentt(models.Model):
    _name = 'code.code'
    name = fields.Char(string="Name")



class Procurmenttwizard(models.TransientModel):
    _name = 'procurment.print'
    project_no = fields.Char(string="Project Number")
    product = fields.Many2one("product.product", string="Product Name")
    submittal_type= fields.Selection(string="Dc Type", selection=[('dc', 'Document Control'), ('mt', 'Material'),('dw','Drawing') ], required=False )
    scope_of_work_id = fields.Many2one("work.scope", string="Scope Of Work", required=False)
    division = fields.Many2one("division.scope", string="Division", required=False)
    job_type_id =  fields.Many2one("job.type", string="Job Type", required=False)
    action_code = fields.Char(string="Action Code", required=False)
    work_item_code = fields.Char(string="Item Code")
    name = fields.Char(string="Work Item")


    def print_dc_xls(self):

        return self.env.ref('procurment_report.dc_xlsx_procurment').report_action(self)

class ProcurmentReportXls(models.AbstractModel):
    _name = 'report.procurment_report.dc_xlsx_procurment'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):


        worksheet = workbook.add_worksheet("Procurment List Report")
        f1 = workbook.add_format({'bold': True, 'font_color': '#000000', 'border': True, 'align': 'vcenter'})
        f2 = workbook.add_format({'bold': True, 'font_color': '#000000', 'border': False, 'align': 'vcenter'})

        cell_text_format = workbook.add_format({'align': 'center',
                                                'bold': True,
                                                'size': 12, })
        cell_text_format_values = workbook.add_format({'align': 'center',
                                                'bold': False,
                                                'size': 10, })

        worksheet.set_column('A:A', 1)
        worksheet.set_column('B:B', 23)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 18)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 18)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 15)
        worksheet.set_column('L:L', 15)

        row = 0
        col = 0


        worksheet.write(row + 5, col + 1, 'Project ID', cell_text_format)
        worksheet.write(row + 5, col + 2, 'Item Code', cell_text_format)
        worksheet.write(row + 5, col + 3, 'Work Item', cell_text_format)
        worksheet.write(row + 5, col + 4, 'Product', cell_text_format)
        worksheet.write(row + 5, col + 5, 'DC Type', cell_text_format)
        worksheet.write(row + 5, col + 6, 'Scope Of Work', cell_text_format)
        worksheet.write(row + 5, col + 7, 'Division', cell_text_format)
        worksheet.write(row + 5, col + 8, 'Job Type', cell_text_format)
        worksheet.write(row + 5, col + 9, 'Action Code', cell_text_format)

        row = 6
        seq = 0
        where_search = []
        project_id = self.env['project.project'].search([('project_no', '=', lines.project_no)])
        if lines.project_no:
            where_search.append(('project_id', '=', project_id.id))
        if lines.work_item_code:
            where_search.append(('work_item_code', '=', lines.work_item_code))
        if lines.name:
            where_search.append(('name', '=', lines.name))
        if lines.product:
            where_search.append(('product', '=', lines.product.id))
        if lines.submittal_type:
            where_search.append(('submittal_type', '=', lines.submittal_type))
        if lines.scope_of_work_id:
            where_search.append(('scope_of_work_id', '=', lines.scope_of_work_id.id))
        if lines.division:
            where_search.append(('division', '=', lines.division.id))
        if lines.job_type_id:
            where_search.append(('job_type_id', '=', lines.job_type_id.id))
        if lines.action_code:
            where_search.append(('action_code', '=', lines.action_code))
        procurment_list_line = self.env['procurment.list.lines'].search(where_search)
        for rec in procurment_list_line:
            row += 1
            seq += 1
            worksheet.write(row, col + 1, str(rec.project_id.project_no or ' '), cell_text_format_values)
            worksheet.write(row, col + 2, str(rec.work_item_code or ' '), cell_text_format_values)
            worksheet.write(row, col + 3, str(rec.name or ' '), cell_text_format_values)
            worksheet.write(row, col + 4, str(rec.product.name or ' '), cell_text_format_values)
            worksheet.write(row, col + 5, str(rec.submittal_type or ' '), cell_text_format_values)
            worksheet.write(row, col + 6, str(rec.scope_of_work_id.name or ' '), cell_text_format_values)
            worksheet.write(row, col + 7, str(rec.division.name or ' '), cell_text_format_values)
            worksheet.write(row, col + 8, str(rec.job_type_id.name or ' '), cell_text_format_values)
            worksheet.write(row, col + 9, str(rec.action_code or ' '), cell_text_format_values)
