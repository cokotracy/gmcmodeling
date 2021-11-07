# -*- coding: utf-8 -*-
""" This Module For Sale Order """
from odoo import models, fields, api


class SaleOrder(models.Model):
    """ sale.order Model """
    _inherit = 'sale.order'

    job_type_id = fields.Many2one(comodel_name='job.type')
    project_id = fields.Many2one(comodel_name='project.project', string='Project Name')
    project_no = fields.Char(related='project_id.project_no', readonly=True)
    project_start_date = fields.Date(
        related='project_id.project_start_date', readonly=True
    )
    project_end_date = fields.Date(
        related='project_id.project_end_date', readonly=True
    )
    project_period = fields.Char(
        related='project_id.project_period', readonly=True
    )


    def action_job_estimate(self):
        """
        get all Job Estimation related to quotation
        :return: Job Estimation view action
        """
        action = self.env.ref('job_cost_estimate_customer.action_estimate_job').read()[0]
        action['domain'] = [('quotation_id', '=', self.id)]
        return action


    def _prepare_invoice(self):
        """
        Override to add sale order additional fields to related invoice
        """
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'job_type_id': self.job_type_id.id,
            'project_name_id': self.project_id.id,
        })
        return invoice_vals

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if res.order_line:
            for line in res.order_line:
                if line.product_id.type == 'service' and line.recently_done_update:
                    line.write({
                        'qty_delivered': line.qty_delivered + line.recently_done,
                        'recently_done_update': False
                    })
        return res


    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if vals.get('order_line'):
            for line in self.order_line:
                if line.product_id.type == 'service' and line.recently_done_update:
                    line.write({
                        'qty_delivered': line.qty_delivered + line.recently_done,
                        'recently_done_update': False
                    })
        return res


class SaleOrderLine(models.Model):
    """ sale.order Model """
    _inherit = 'sale.order.line'

    recently_done = fields.Float()
    recently_done_update = fields.Boolean()

    @api.onchange('recently_done')
    def recently_done_qty_on_change(self):
        if self.recently_done > 0:
            self.recently_done_update = True

