# -*- coding: utf-8 -*-
from odoo import http

# class WcTax41(http.Controller):
#     @http.route('/wc_tax41/wc_tax41/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wc_tax41/wc_tax41/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wc_tax41.listing', {
#             'root': '/wc_tax41/wc_tax41',
#             'objects': http.request.env['wc_tax41.wc_tax41'].search([]),
#         })

#     @http.route('/wc_tax41/wc_tax41/objects/<model("wc_tax41.wc_tax41"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wc_tax41.object', {
#             'object': obj
#         })