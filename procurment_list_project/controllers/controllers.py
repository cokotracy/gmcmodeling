# -*- coding: utf-8 -*-
from odoo import http

# class MyExtraAddons(http.Controller):
#     @http.route('/my_extra_addons/my_extra_addons/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/my_extra_addons/my_extra_addons/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('my_extra_addons.listing', {
#             'root': '/my_extra_addons/my_extra_addons',
#             'objects': http.request.env['my_extra_addons.my_extra_addons'].search([]),
#         })

#     @http.route('/my_extra_addons/my_extra_addons/objects/<model("my_extra_addons.my_extra_addons"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('my_extra_addons.object', {
#             'object': obj
#         })