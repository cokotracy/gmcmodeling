# -*- coding: utf-8 -*-
from odoo import http

# class WcDocumentControl(http.Controller):
#     @http.route('/wc_document_control/wc_document_control/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wc_document_control/wc_document_control/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wc_document_control.listing', {
#             'root': '/wc_document_control/wc_document_control',
#             'objects': http.request.env['wc_document_control.wc_document_control'].search([]),
#         })

#     @http.route('/wc_document_control/wc_document_control/objects/<model("wc_document_control.wc_document_control"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wc_document_control.object', {
#             'object': obj
#         })