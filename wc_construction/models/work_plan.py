# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class WorkPlanLines(models.Model):
    _name = 'work.plan.line'

    product_id = fields.Many2one(comodel_name="product.product",domain=[('is_tender_item','=',True)], string="tender Item", required=True, )
    work_plan_item_id = fields.Many2one(comodel_name="work.plan.items.line", string="Work Plan Item", required=False, )
    quantity = fields.Float(string="Quantity",  required=False, )
    tender_quantity = fields.Float(string="Tender Quantity",  required=False, )
    work_plan_id = fields.Many2one(comodel_name="work.plan", string="", required=False, )

    update_product = fields.Boolean(string="Update Products", )

    @api.onchange('product_id')
    def get_product_data(self):
        for rec in self:
            for line in rec.work_plan_id.quotation_id.order_line:
                if rec.product_id.id == line.product_id.id:
                    # rec.price_unit = line.price_unit
                    rec.tender_quantity = line.product_uom_qty
                    # rec.product_uom_id = line.product_uom_id.id

    @api.onchange('update_product', 'quantity','product_id')
    def get_products_from_contract_quotation(self):
        for rec in self:
            products = []
            for res in rec.work_plan_id.quotation_id.order_line:
                products.append(res.product_id.id)

            return {'domain': {'product_id': [('id', 'in', products)]}}

    @api.onchange('product_id','work_plan_item_id')
    def filter_work_plan_items(self):
        work_plan_items = self.env['work.plan.items'].search([('project_id','=',self.work_plan_id.project_id.id)])
        work_plan_items_line = []
        for rec in work_plan_items:
            for line in rec.work_plan_items_line_ids:
                work_plan_items_line.append(line.id)

        return {'domain':{'work_plan_item_id':[('id','in',work_plan_items_line)]}}


class WorkPlan(models.Model):
    _name = 'work.plan'

    contract_id = fields.Many2one(comodel_name="owner.contract",domain=[('type','=','subcontractor')] ,string="Contract", required=False, )

    quotation_id = fields.Many2one(comodel_name="sale.order", string="Quotation",compute='get_customer',store=True, required=False, )
    project_id = fields.Many2one(comodel_name="project.project", string="Project", required=True, )
    customer_id = fields.Many2one(comodel_name="res.partner", string="Vendor",compute='get_customer',store=True, required=False, )
    date = fields.Date(string="Date", required=False, default=fields.Date.context_today)
    work_plan_line_ids = fields.One2many(comodel_name="work.plan.line", inverse_name="work_plan_id", string="", required=False, )

    @api.depends('project_id')
    def get_customer(self):
        if self.project_id:
            self.quotation_id = self.project_id.so_id.id
            self.customer_id = self.project_id.partner_id.id
        else:
            self.quotation_id = False
            self.customer_id = False

    @api.onchange('work_plan_line_ids')
    def action_restriction_plan_line(self):
        for i in self.work_plan_line_ids:
            total_qty = i.quantity
            tender_quantity = i.tender_quantity
            for j in self.work_plan_line_ids:
                if i.id == j.id:
                    continue
                if i.product_id.id == j.product_id.id and i.work_plan_item_id.id == j.work_plan_item_id.id:
                    total_qty = total_qty + j.quantity
                if total_qty > tender_quantity:
                    raise ValidationError("There Is No Available Quantity")

    @api.onchange('contract_id')
    def get_contract_data(self):
        # lines = []
        self.project_id = self.contract_id.project_id.id
        # self.customer_id = self.contract_id.customer_id.id

        # for rec in self.contract_id.contract_line_ids:
        #     lines.append((0, 0, {
        #         'product_id': rec.product_id.id,
        #         'account_id': self._get_computed_account_to_lines(rec.product_id),
        #         'name': rec.product_id.name,
        #         'price_unit': rec.price_unit,
        #         'total_contract_qty': rec.quantity,
        #         'quantity': 0,
        #         'product_uom_id': rec.product_uom_id.id,
        #         'exclude_from_invoice_tab': False,
        #         'tax_ids': rec.tax_id.ids,
        #     }))
        # self._onchange_partner_id()
        # self.invoice_line_ids = lines
        #
        # for line in self.invoice_line_ids:
        #     line._onchange_price_subtotal()
        # self._onchange_invoice_line_ids()






