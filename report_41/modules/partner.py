from odoo import api, fields, models


class Vendor(models.Model):
    _inherit = "res.partner"

    m_code = fields.Char('كود المأموريه المتخصصه')
    t_code = fields.Char('كود التعامل')
    file_no = fields.Char('رقم الملف')
    registeration_no = fields.Char('رقم التسجيل')
