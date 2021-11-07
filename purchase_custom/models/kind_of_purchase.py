from odoo import api, fields, models


class kind_of_purchase(models.Model):
    _name = 'kind.of.purchase'
    _rec_name = 'name'
    _description = 'Kind Of Purchase'


    name = fields.Char(string="Kind Of purchase", required=False, )
    user_id = fields.Many2one(comodel_name="res.users", string="Responsible", required=False, )
    financial_approval= fields.Boolean(string="Financial approval",  )
