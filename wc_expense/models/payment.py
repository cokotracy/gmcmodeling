# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    user_confirmed = fields.Many2one(comodel_name="res.users", string="User Confirmed", required=False, )

    def post(self):
        res = super(AccountPayment, self).post()
        self.user_confirmed = self.env.user.id
        return res
