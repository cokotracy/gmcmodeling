# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    project_id = fields.Many2one(comodel_name="project.project", string="Project", required=False, )

class SalesOrderLine(models.Model):
    _inherit = 'sale.order.line'

    code = fields.Char(string="Code", required=False, )




