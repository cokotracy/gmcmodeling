# -*- coding: utf-8 -*-
from odoo import http

# class WcExpense(http.Controller):
#     @http.route('/wc_expense/wc_expense/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wc_expense/wc_expense/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wc_expense.listing', {
#             'root': '/wc_expense/wc_expense',
#             'objects': http.request.env['wc_expense.wc_expense'].search([]),
#         })

#     @http.route('/wc_expense/wc_expense/objects/<model("wc_expense.wc_expense"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wc_expense.object', {
#             'object': obj
#         })