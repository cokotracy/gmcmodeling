# Copyright 2018 Giacomo Grasso <giacomo.grasso.82@gmail.com>
# Odoo Proprietary License v1.0 see LICENSE file

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_invoiced = fields.Float(compute='_get_so_open_amount', string='Invoiced', store=True,
                                   copy=False)
    amount_to_invoice = fields.Float(compute='_get_so_open_amount', string='To Invoice', store=True,
                                     copy=False)

    @api.depends('order_line.amount_invoiced')
    def _get_so_open_amount(self):
        """
        Compute the total amount invoiced and the remaining amount to be
        invoiced of the entire sale order
        """
        for order in self:
            invoiced, to_invoice = 0.0, 0.0

            for line in order.order_line:
                invoiced += line.amount_invoiced
                to_invoice += line.amount_to_invoice

            order.amount_invoiced = invoiced
            order.amount_to_invoice = to_invoice


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    amount_invoiced = fields.Float(compute='_get_po_invoice_amount', string='Amount Inv.', store=True,
                                   readonly=True, digits=dp.get_precision('Product Price'))
    amount_to_invoice = fields.Float(compute='_get_po_invoice_amount', string='Amount to Inv.', store=True,
                                     readonly=True, digits=dp.get_precision('Product Price'))

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.price_subtotal', 'price_subtotal',)
    def _get_po_invoice_amount(self):
        """
        Compute the total amount invoiced and the remaining amount to be
        invoiced. If case of a refund, these amounts are decreased.
        """
        for order_line in self:
            invoiced = 0.0
            for line in order_line.invoice_lines:
                if line.move_id.state != 'cancel':
                    tax_list = line.invoice_line_tax_ids.compute_all(
                        line.price_subtotal,
                        line.move_id.currency_id,
                        1,
                        line.product_id,
                        line.move_id.partner_id)['taxes']
                    taxes = 0.0
                    for tax in tax_list:
                        taxes += tax['amount']
                    if line.move_id.type == 'out_invoice':
                        invoiced += line.price_subtotal + taxes
                    elif line.move_id.type == 'out_refund':
                        invoiced -= line.price_subtotal + taxes

            order_line.amount_invoiced = invoiced
            order_line.amount_to_invoice = order_line.price_total - invoiced
