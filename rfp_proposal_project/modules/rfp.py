from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class RFP(models.Model):
    _name = 'rfp.rfp'
    _description = 'RFP'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']



    state = fields.Selection([('draft', 'Draft'),('confirmed','Confirmed'),('approved','Approved'),('rejected','Rejected')], default='draft', string="State", index=True)


    name = fields.Char()
    customer_id = fields.Many2one('res.partner','Customer')

    type_work = fields.Char('Type of Work')
    place_work = fields.Char('Place of Work')
    customer_refrence = fields.Char('Customer Reference')

    date = fields.Date('RFP Date')
    date_respond = fields.Date('Respond Date')

    analytic_account_id = fields.Many2one('account.analytic.account' , 'Analyti account')
    is_analytic = fields.Boolean(compute="_get_is_analytic")

    description_ids = fields.One2many('rfp.description' , 'rfp_id')


    def action_confirm(self):
    	# set rfp to confirmed
    	self.state = 'confirmed'

    def action_approve(self):
    	# set rfp to approved
    	self.state = 'approved'

    def action_reject(self):
    	# set rfp to rejected
    	self.state = 'rejected'

    def action_set_to_draft(self):
    	# set rfp to approved
    	self.state = 'draft'


    def action_create_analytic_account(self):

    	if self.name and self.customer_id :
    		analytic = self.env['account.analytic.account'].create({
    			'name' : self.name,
    			'partner_id' : self.customer_id.id,
    			})
    		self.analytic_account_id = analytic.id
    		self.write({
    			'analytic_account_id' : analytic.id, 
    			})
    		return self
    			
    	else:
    		raise UserError('Please set data in RFP Number and Customer first')


    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('rfp.rfp')
        rec = super(RFP, self).create(values)

        return rec

    @api.depends('analytic_account_id')
    def _get_is_analytic(self):
        if self.analytic_account_id :
            self.is_analytic = True
        else:
            self.is_analytic = False



class RFPDescription(models.Model):
    _name = 'rfp.description'
    _description = 'RFP'


    description = fields.Char('Description')

    rfp_id = fields.Many2one('rfp.rfp')