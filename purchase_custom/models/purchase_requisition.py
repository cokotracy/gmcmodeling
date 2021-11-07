from odoo import api, fields, models



class purchase_requisition(models.Model):
    _inherit = 'purchase.requisition'

    kindpo_id = fields.Many2one(comodel_name="kind.of.purchase", string="Kind Of Purchase", required=False, )
    purchasee_type = fields.Selection(string="Purchase type", selection=[('international', 'International Purchase'), ('local', ' Local Purchase'), ], required=False, )
    purchasee_type_2 = fields.Selection(string="Purchase type", selection=[('international', 'مشتريات خارجيه'), ('local', 'مشتريات داخليه'), ], required=False, )