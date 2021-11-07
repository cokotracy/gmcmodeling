from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class Proposal(models.Model):
    _name = 'proposal.proposal'
    _description = 'PROPOSAL'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']



    state = fields.Selection([('draft', 'Draft'),('confirmed','Confirmed'),('approved','Approved'),('f_approved','Final Approve'),('rejected','Rejected')], default='draft', string="State", index=True)


    name = fields.Char()
    customer_id = fields.Many2one('res.partner','Customer',required=True)

    rfp_id = fields.Many2one('rfp.rfp','Auto Complete',domain=[('state','=','approved')])

    type_work = fields.Char('Type of Work')
    place_work = fields.Char('Place of Work')
    customer_refrence = fields.Char('Customer Reference')

    date = fields.Date('Proposal Date')
    date_respond = fields.Date('Respond Date')

    analytic_account_id = fields.Many2one('account.analytic.account' , 'Analyti account')
    is_analytic = fields.Boolean(compute="_get_is_analytic")

    # document
    doc1 = fields.Binary('Document 1')
    doc2 = fields.Binary('Document 2')

    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.user.company_id,
        string='Company',
    )
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Pricelist',
        help="Pricelist for current sales estimate."
    )

    estimate_ids = fields.One2many(
        'sale.estimate.line.job.proposal',
        'proposal_id',
        'Estimate Lines',
        copy=False,
        domain=[('job_type','=','material')],
    )
    labour_estimate_line_ids = fields.One2many(
        'sale.estimate.line.job.proposal',
        'proposal_id',
        copy=False,
        domain=[('job_type','=','labour')],
    )

    overhead_estimate_line_ids = fields.One2many(
        'sale.estimate.line.job.proposal',
        'proposal_id',
        copy=False,
        domain=[('job_type','=','overhead')],
    )

    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        if self.customer_id:
            domain = {'domain': {'rfp_id': [('customer_id','=',self.customer_id.id),('state','=','approved')]}}
            return domain
        else :
            domain = {'domain': {'rfp_id': [('state','=','approved')]}}
            return domain

    @api.onchange('rfp_id')
    def _onchange_rfp_id(self):
        if self.rfp_id:
            self.date = self.rfp_id.date
            self.customer_refrence = self.rfp_id.customer_refrence
            self.type_work = self.rfp_id.type_work
            self.place_work = self.rfp_id.place_work
            self.customer_id = self.rfp_id.customer_id.id


    def action_confirm(self):
    	# set rfp to confirmed
    	self.state = 'confirmed'

    def action_approve(self):
    	# set rfp to approved
    	self.state = 'approved'

    def action_final_approve(self):
        # set rfp to approved
        if not self.doc1 or not self.doc2:
            raise UserError("You have to upload domcument in document tap")
        else:
            self.state = 'f_approved'

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
        values['name'] = self.env['ir.sequence'].next_by_code('proposal.proposal')
        rec = super(Proposal, self).create(values)

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