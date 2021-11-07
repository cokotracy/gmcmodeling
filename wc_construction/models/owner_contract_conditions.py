# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class OwnerContractConditions(models.Model):
    _inherit = 'owner.contract'

    conditions = fields.Html(string="Contract Important Terms", required=False)
    project_location_id = fields.Char(readonly=False)
