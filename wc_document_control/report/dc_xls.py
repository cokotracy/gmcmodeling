 # -*- coding: utf-8 -*-
from odoo.http import request
from odoo import models, api,fields
from datetime import date,datetime
from odoo.exceptions import UserError, ValidationError


from datetime import datetime, timedelta



class DCReportXls(models.AbstractModel):
    _name = 'report.wc_document_control.dc_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

        worksheet = workbook.add_worksheet("Document Control Report")
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
        worksheet.write(row + 2, col,str(dict(lines._fields['submittal_type'].selection).get(lines.submittal_type)) + ' Submittal Form', f2)

        worksheet.write(row + 5, col + 1, 'Transaction ID', cell_text_format)
        worksheet.write(row + 5, col + 2, 'Revision No', cell_text_format)
        worksheet.write(row + 5, col + 3, 'Project ID', cell_text_format)
        worksheet.write(row + 5, col + 4, 'Project Name', cell_text_format)
        worksheet.write(row + 5, col + 5, 'Scope Of Work', cell_text_format)
        worksheet.write(row + 5, col + 6, 'Submittal Type', cell_text_format)
        worksheet.write(row + 5, col + 7, 'Description', cell_text_format)
        worksheet.write(row + 5, col + 8, 'Submission Date', cell_text_format)
        worksheet.write(row + 5, col + 9, 'Status', cell_text_format)
        worksheet.write(row + 5, col + 10, 'Return Date', cell_text_format)
        worksheet.write(row + 5, col + 11, 'Action Code', cell_text_format)
        row = 6
        seq = 0
        domain = []
        if lines.projectID:
            domain.append(('projectID', '=', lines.projectID), )
        if lines.project_id:
            domain.append(('project_id', '=',lines.project_id.id), )
        if lines.transaction_id:
            domain.append(('transaction_id', '=',lines.transaction_id), )
        if lines.revision_no:
            domain.append(('revision_no', '=',lines.revision_no), )
        if lines.submission_date_from and lines.submission_date_to:
            domain.append(('submission_date', '>=', lines.submission_date_from), )
            domain.append(('submission_date', '<=', lines.submission_date_to), )
        if lines.ref:
            domain.append(('ref', '=', lines.ref), )
        if lines.submittal_type:
            domain.append(('submittal_type', '=', lines.submittal_type), )
        if lines.scope_of_work_id:
            domain.append(('scope_of_work_id', '=', lines.scope_of_work_id.id), )
        submittal_items = self.env['document.control.line'].search(domain)
        for sub_item in submittal_items:

                    row += 1
                    seq += 1

                    worksheet.write(row, col + 1, str(sub_item.transaction_id or ' '), cell_text_format_values)
                    worksheet.write(row, col + 2, str(sub_item.revision_no or ' '), cell_text_format_values)
                    worksheet.write(row, col + 3, str(sub_item.projectID or ' '), cell_text_format_values)
                    worksheet.write(row, col + 4, str(sub_item.project_id.name or ' '), cell_text_format_values)
                    worksheet.write(row, col + 5, str(sub_item.scope_of_work_id.name or ' '), cell_text_format_values)
                    worksheet.write(row, col + 6, str(dict(sub_item._fields['submittal_type'].selection).get(sub_item.submittal_type)) or ' ', cell_text_format_values)
                    worksheet.write(row, col + 7, str(sub_item.description or ' '), cell_text_format_values)
                    worksheet.write(row, col + 8, str(sub_item.submission_date or ' '), cell_text_format_values)
                    worksheet.write(row, col + 9, str(dict(sub_item._fields['code'].selection).get(sub_item.code)) or ' ', cell_text_format_values)
                    worksheet.write(row, col + 10, str(sub_item.return_date or ' '))
                    worksheet.write(row, col + 11, str(sub_item.action_code or ' '),cell_text_format_values)
