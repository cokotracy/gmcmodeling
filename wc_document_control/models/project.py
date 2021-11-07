# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date


class Project(models.Model):
    _inherit = 'project.project'

    client_specialist_id = fields.Many2one(comodel_name="res.partner", string="Client Specialist", required=False, )
    consultant_id = fields.Many2one(comodel_name="consultant.consultant", string="Consultant",
                                    help="The Project Consultant Office")
    client_manager = fields.Char(string="Client Manager", required=False, )