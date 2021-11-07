# -*- coding: utf-8 -*-
# from odoo import http


# class NumberOfDaysInPayslip(http.Controller):
#     @http.route('/number_of_days_in_payslip/number_of_days_in_payslip/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/number_of_days_in_payslip/number_of_days_in_payslip/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('number_of_days_in_payslip.listing', {
#             'root': '/number_of_days_in_payslip/number_of_days_in_payslip',
#             'objects': http.request.env['number_of_days_in_payslip.number_of_days_in_payslip'].search([]),
#         })

#     @http.route('/number_of_days_in_payslip/number_of_days_in_payslip/objects/<model("number_of_days_in_payslip.number_of_days_in_payslip"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('number_of_days_in_payslip.object', {
#             'object': obj
#         })
