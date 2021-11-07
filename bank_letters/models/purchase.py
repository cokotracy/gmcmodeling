from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, UserError
from datetime import date

class purchase(models.Model):
    _inherit = "purchase.order"
    letter_of_credit = fields.Many2one('account.letter','Letter of credit',domain=[('state','=','validate')],)
    