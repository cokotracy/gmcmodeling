from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = 'res.partner'

    customer_type = fields.Selection(selection=[('cash', 'Cash'),
                                                ('credit', 'Credit'),
                                                ('subcontracting', 'Subcontracting')], string='Customer Type')
