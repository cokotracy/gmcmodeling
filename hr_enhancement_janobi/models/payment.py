from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date


class Payment(models.Model):
    _inherit = 'account.payment'

    is_loan_payment = fields.Boolean()
    employee_id = fields.Many2one('hr.employee')

    def action_post(self):
        if self.is_loan_payment and self.employee_id:
            self.env['hr.employee.loan'].create({
            'currency_id':self.currency_id.id,
            'employee_id':self.employee_id.id,
            'date':self.date,
            'desc':self.ref,
            'amount':self.amount,
            'install_count':1,
            'state':'draft',
            })
        return super(Payment, self).action_post()
