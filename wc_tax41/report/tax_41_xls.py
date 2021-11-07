 # -*- coding: utf-8 -*-
from odoo.http import request
from odoo import models, api,fields
from datetime import date,datetime
from odoo.exceptions import UserError, ValidationError


from datetime import datetime, timedelta



class AttendanceReportXls(models.AbstractModel):
    _name = 'report.wc_tax41.tax_41_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        name =  data['form']

        worksheet = workbook.add_worksheet("Tax 41")
        worksheet.right_to_left()
        f1 = workbook.add_format({'bold': True, 'font_color': '#000000', 'border': True, 'align': 'vcenter'})
        f2 = workbook.add_format({'bold': True, 'font_color': '#000000', 'border': False, 'align': 'vcenter'})

        cell_text_format = workbook.add_format({'align': 'center',
                                                'bold': True,
                                                'size': 12, })
        cell_text_format_values = workbook.add_format({'align': 'center',
                                                'bold': False,
                                                'size': 10, })

        worksheet.set_column('A:A', 3)
        worksheet.set_column('B:B', 5)
        worksheet.set_column('C:C', 8)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 13)
        worksheet.set_column('H:H', 10)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 8)
        worksheet.set_column('K:K', 15)
        worksheet.set_column('L:L', 20)
        worksheet.set_column('M:M', 20)
        worksheet.set_column('N:N', 20)
        worksheet.set_column('O:O', 15)
        worksheet.set_column('O:O', 15)
        worksheet.set_column('P:P', 10)

        row = 0
        col = 0
        worksheet.write(row + 2, col,
                        'نموزج 41 من  ' + str(name['from_date']) + ' إلى ' + str(
                            name['to_date']), f2)


        worksheet.write(row + 5, col + 1, 'الفترة', cell_text_format)
        worksheet.write(row + 5, col + 2, 'السنة', cell_text_format)
        worksheet.write(row + 5, col + 3, 'رقم التسجيل', cell_text_format)
        worksheet.write(row + 5, col + 4, 'رقم الملف', cell_text_format)
        worksheet.write(row + 5, col + 5, 'كود المأمورية المختصة', cell_text_format)
        worksheet.write(row + 5, col + 6, 'تاريخ التعامل', cell_text_format)
        worksheet.write(row + 5, col + 7, 'طبيعة التعامل', cell_text_format)
        worksheet.write(row + 5, col + 8, 'القيمة الإجمالية للتعامل', cell_text_format)
        worksheet.write(row + 5, col + 9, 'نوع الخصم', cell_text_format)
        worksheet.write(row + 5, col + 10, 'القيمة الصافية للتعامل', cell_text_format)
        worksheet.write(row + 5, col + 11, 'نسبة الخصم على الضريبة', cell_text_format)
        worksheet.write(row + 5, col + 12, 'المحصل لحساب الضريبة', cell_text_format)
        worksheet.write(row + 5, col + 13, 'أسم الممول', cell_text_format)
        worksheet.write(row + 5, col + 14, 'عنوان الممول', cell_text_format)
        worksheet.write(row + 5, col + 15, 'الرقم القومي', cell_text_format)
        worksheet.write(row + 5, col + 16, 'العملة', cell_text_format)


        row = 6
        seq = 0
        move_lines = self.env['account.move.line'].search([('date', '>=', name['from_date']),('date', '<=', name['to_date']),('move_id.type', 'in', ['in_invoice', 'in_refund'])],order='date ASC')

        account_tax = self.env['account.tax'].search([('discount_type', '!=',False)])
        for tax_type in account_tax:
            for ml in move_lines:
                print (ml.date)

                if tax_type.id in ml.tax_ids.ids:
                    row += 1
                    seq += 1
                    invoice_date = datetime.strptime(str(ml.move_id.invoice_date), '%Y-%m-%d').date()
                    duration = ''
                    if invoice_date.month in [1,2,3]:
                        duration = '1'
                    elif invoice_date.month in [2,3,4]:
                        duration = '2'
                    elif invoice_date.month in [5,6,7]:
                        duration = '3'
                    else:
                        duration = '4'
                    worksheet.write(row, col + 1, str(duration), cell_text_format_values)
                    worksheet.write(row, col + 2, str(invoice_date.year), cell_text_format_values)
                    worksheet.write(row, col + 3, str(ml.move_id.partner_id.register_no or ' '), cell_text_format_values)
                    worksheet.write(row, col + 4, str(ml.move_id.partner_id.file_no or ' '), cell_text_format_values)
                    worksheet.write(row, col + 5, str(ml.move_id.partner_id.mission_code or ' '), cell_text_format_values)
                    worksheet.write(row, col + 6, str(invoice_date or ' '), cell_text_format_values)
                    worksheet.write(row, col + 7, str(ml.move_id.partner_id.dealing_nature or ' '), cell_text_format_values)
                    worksheet.write(row, col + 8, str(ml.price_subtotal), cell_text_format_values)
                    worksheet.write(row, col + 9, str(tax_type.discount_type if tax_type else ' '), cell_text_format_values)
                    worksheet.write(row, col + 10, str(ml.price_subtotal), cell_text_format_values)
                    worksheet.write(row, col + 11, str(-(tax_type.amount) if tax_type.amount < 0 else tax_type.amount or '') + (' %'),
                                    cell_text_format_values)
                    worksheet.write(row, col + 12, str(-(ml.price_subtotal * tax_type.amount / 100) if tax_type.amount < 0 else (ml.price_subtotal * tax_type.amount / 100) or ' '), cell_text_format_values)
                    worksheet.write(row, col + 13, str(ml.move_id.partner_id.name), cell_text_format_values)
                    worksheet.write(row, col + 14, str(ml.move_id.partner_id.street or ''), cell_text_format_values)
                    worksheet.write(row, col + 15, str(ml.move_id.partner_id.national_ID or ''), cell_text_format_values)
                    worksheet.write(row, col + 16, str('1'), cell_text_format_values)
