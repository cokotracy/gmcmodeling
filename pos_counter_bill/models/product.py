# -*- coding: utf-8 -*-

from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = "product.template"

    bill_category = fields.Many2one('product.bill_category', 'Product Counter', help="Enter Counter/No where Product is availabal after bill.")


class ProductBillCategory(models.Model):
    _name = 'product.bill_category'
    _description = "Product Bill Category"

    name = fields.Char('Bill Category Name')
