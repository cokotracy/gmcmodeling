# -*- coding: utf-8 -*-

from odoo import models, fields, api

class JobCostLine(models.Model): 
    _inherit = 'job.cost.line'

    customer_invoice_line_ids = fields.One2many(
        'account.move.line',
        'customer_job_cost_line_id',
        string='Customer Invoice Line'
    )
    actual_invoice_subtotal = fields.Float(
        string='Actual Invoice Subtotal',
        compute='_compute_actual_subtotal',
        store=True
    )
    
    @api.depends('customer_invoice_line_ids',
                 'customer_invoice_line_ids.quantity',
                 'customer_invoice_line_ids.price_unit', 
                 'customer_invoice_line_ids.move_id.state')
    def _compute_actual_subtotal(self):
        actual_invoice_subtotal = 0.0
        for rec in self:
            for line in rec.customer_invoice_line_ids:
                if line.invoice_id.state in ['open', 'paid']:
                    if line.currency_id != rec.currency_id:
                        from_currency = line.currency_id
                        to_currency = rec.currency_id
                        compute_currency = from_currency.compute((line.quantity * line.price_unit), to_currency)
                        actual_invoice_subtotal += compute_currency
                    else:
                        actual_invoice_subtotal += line.quantity * line.price_unit
            rec.actual_invoice_subtotal = actual_invoice_subtotal


    
   