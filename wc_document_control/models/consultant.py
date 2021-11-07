# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime,date
class Consultant(models.Model):
    _name = 'consultant.consultant'
    _rec_name = 'name'
    _description = ''

    def get_default_company(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", default=get_default_company,
                                 required=False, )

    name = fields.Char(string="Name", required=False, )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Attention", required=False, )
    logo1 = fields.Image(string="Logo1",max_width=1920, max_height=1920,)
    image_128_logo1 = fields.Image("logo1 128",related="logo1", max_width=128, max_height=128, store=True)
    logo2 = fields.Image(string="Logo2",max_width=1920, max_height=1920,)
    image_128_logo2 = fields.Image("logo2 128" ,related="logo2", max_width=128, max_height=128, store=True)


class Partner(models.Model):
    _inherit = 'res.partner'

    logo2 = fields.Binary(string="Logo2",  )


