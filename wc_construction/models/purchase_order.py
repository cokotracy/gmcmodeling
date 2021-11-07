# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[('dep_approved', 'Department Approved'),
                                            ('gm_approved', 'GM Approved'),
                                            ('sent',), ], required=False)

    is_need_confirm = fields.Boolean(string="", compute='check_order_lines_control_cost')

    @api.depends('is_need_confirm')
    def check_order_lines_control_cost(self):
        for rec in self:
            rec.is_need_confirm = False
            if not self.validate_done:
                for line in rec.order_line:
                    if line.product_qty > line.validate_qty:  # or rec.price_unit > rec.validate_price:
                        if self.env.user.has_group('procurment_list_project.group_control_po_validate'):
                            rec.is_need_confirm = True
                        elif self.env.user.has_group(
                                'procurment_list_project.group_control_po_validate_type_c') and rec.origin == "Procurement-C":
                            rec.is_need_confirm = True
                        elif self.env.user.has_group(
                                'procurment_list_project.group_control_po_validate_type_m') and rec.origin == "Procurement-M":
                            rec.is_need_confirm = True
                        elif self.env.user.has_group(
                                'procurment_list_project.group_control_po_validate_type_e') and rec.origin == "Procurement-E":
                            rec.is_need_confirm = True

    def gm_approve(self):
        self.state = 'gm_approved'

    def action_dep_approve(self):
        self.state = 'dep_approved'

    def button_confirm(self):
        for order in self:
            if self.is_need_confirm:
                raise UserError('Order Lines Need Validate From Control Cost Responsible')
            if order.state not in ['draft', 'sent', 'gm_approved']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.company.currency_id._convert(
                        order.company_id.po_double_validation_amount, order.currency_id, order.company_id,
                        order.date_order or fields.Date.today())) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True
