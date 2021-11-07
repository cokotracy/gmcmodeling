# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api


class SelectProducts(models.TransientModel):

    _name = 'select.products'
    _description = 'Select Products'

    product_ids = fields.Many2many('product.product', string='Products')
    flag_type = fields.Char('Flag Type')

    def select_products(self):
        if self.flag_type == 'material':
            job_cost_id = self.env['job.costing'].browse(self._context.get('active_id', False))
            for product in self.product_ids:
                self.env['job.cost.line'].create({
                    'product_id': product.id,
                    'description': product.name,
                    'uom_id': product.uom_id.id,
                    'cost_price': product.standard_price,
                    'job_type': 'material',
                    'product_qty': 1.0,
                    'date': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'direct_id': job_cost_id.id
                })
        if self.flag_type == 'subcontractor':
            job_cost_id = self.env['job.costing'].browse(self._context.get('active_id', False))
            for product in self.product_ids:
                self.env['job.cost.line'].create({
                    'product_id': product.id,
                    'description': product.name,
                    'uom_id': product.uom_id.id,
                    'cost_price': product.standard_price,
                    'job_type': 'subcontractor',
                    'product_qty': 1.0,
                    'date': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'direct_id': job_cost_id.id
                })
        if self.flag_type == 'other':
            job_cost_id = self.env['job.costing'].browse(self._context.get('active_id', False))
            for product in self.product_ids:
                self.env['job.cost.line'].create({
                    'product_id': product.id,
                    'description': product.name,
                    'uom_id': product.uom_id.id,
                    'cost_price': product.standard_price,
                    'job_type': 'other',
                    'product_qty': 1.0,
                    'date': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'direct_id': job_cost_id.id
                })
        elif self.flag_type == 'labour':
            job_cost_id = self.env['job.costing'].browse(self._context.get('active_id', False))
            for product in self.product_ids:
                self.env['job.cost.line'].create({
                    'product_id': product.id,
                    'description': product.name,
                    'uom_id': product.uom_id.id,
                    'cost_price': product.standard_price,
                    'job_type': 'labour',
                    # 'invoice_hours': 0,
                    'date': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'direct_id': job_cost_id.id
                })
        elif self.flag_type == 'equipment':
            job_cost_id = self.env['job.costing'].browse(self._context.get('active_id', False))
            for product in self.product_ids:
                self.env['job.cost.line'].create({
                    'product_id': product.id,
                    'description': product.name,
                    'uom_id': product.uom_id.id,
                    'cost_price': product.standard_price,
                    'job_type': 'equipment',
                    # 'invoice_hours': 1.0,
                    'date': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'direct_id': job_cost_id.id
                })
        elif self.flag_type == 'overhead':
            job_cost_id = self.env['job.costing'].browse(self._context.get('active_id', False))
            for product in self.product_ids:
                self.env['job.cost.line'].create({
                    'product_id': product.id,
                    'description': product.name,
                    'uom_id': product.uom_id.id,
                    'cost_price': product.standard_price,
                    'job_type': 'overhead',
                    # 'invoice_hours': 1.0,
                    'date': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'direct_id': job_cost_id.id
                })
