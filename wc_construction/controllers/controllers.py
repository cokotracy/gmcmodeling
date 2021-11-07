# -*- coding: utf-8 -*-
from odoo import http

# class WcConstruction(http.Controller):
#     @http.route('/wc_construction/wc_construction/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wc_construction/wc_construction/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wc_construction.listing', {
#             'root': '/wc_construction/wc_construction',
#             'objects': http.request.env['wc_construction.wc_construction'].search([]),
#         })

#     @http.route('/wc_construction/wc_construction/objects/<model("wc_construction.wc_construction"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wc_construction.object', {
#             'object': obj
#         })