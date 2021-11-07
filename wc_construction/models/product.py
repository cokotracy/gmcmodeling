# -*- coding: utf-8 -*-

from odoo import models, fields


class Product(models.Model):
    _inherit = 'product.product'

    is_tender_item = fields.Boolean(string="Is Tender Item")
    is_deduction = fields.Boolean(string='Is Deduction')


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_tender_item = fields.Boolean(string="Is Tender Item")
    is_deduction = fields.Boolean(string='Is Deduction')
