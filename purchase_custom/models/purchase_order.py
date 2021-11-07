# -*- coding: utf-8 -*-

from odoo import models, fields, api

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    kindpo_id = fields.Many2one(comodel_name="kind.of.purchase",related='requisition_id.kindpo_id',readonly=False ,string="Kind Of Purchase", required=False, )
    purchasee_type = fields.Selection(string="Purchase type",related='requisition_id.purchasee_type',readonly=False, selection=[('international', 'International Purchase'),('local', ' Local Purchase'), ], required=False, store=True)
    purchasee_type_2 = fields.Selection(string="Purchase type",related='requisition_id.purchasee_type_2',readonly=False, selection=[('international', 'مشتريات خارجيه'), ('local', 'مشتريات داخليه'), ],required=False, store=True)

    @api.onchange('purchasee_type')
    def _onchange_purchasee_type(self):
        if self.purchasee_type:
            self.purchasee_type_2 = self.purchasee_type

    @api.onchange('purchasee_type_2')
    def _onchange_purchasee_type_2(self):
        if self.purchasee_type_2:
            self.purchasee_type = self.purchasee_type_2