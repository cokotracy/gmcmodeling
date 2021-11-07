from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp
from datetime import datetime


class Project(models.Model):
    _inherit = 'project.project'

    name = fields.Char(default="new")

    project_no = fields.Char('Project No.')
    project_beginning = fields.Date('Project Beginning')
    project_end_date = fields.Date('Project End Date')
    project_period = fields.Char('Project Period', compute="_get_project_period")
    proposal_id = fields.Many2one('proposal.proposal', 'Auto Complete', domain=[('state', '=', 'f_approved')],
                                  required=True)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            domain = {'domain': {'proposal_id': [('customer_id', '=', self.partner_id.id), ('state', '=', 'approved')]}}
            return domain
        else:
            domain = {'domain': {'proposal_id': [('state', '=', 'approved')]}}
            return domain

    @api.onchange('proposal_id')
    def _onchange_proposal_id(self):
        if self.proposal_id:
            self.analytic_account_id = self.proposal_id.analytic_account_id.id
            self.partner_id = self.proposal_id.customer_id.id

    @api.depends('project_beginning', 'project_end_date')
    def _get_project_period(self):
        if self.project_end_date and self.project_beginning:
            d1 = datetime.strptime(str(self.project_beginning), "%Y-%m-%d")
            d2 = datetime.strptime(str(self.project_end_date), "%Y-%m-%d")
            self.project_period = str(abs((d2 - d1).days)) + ' Days'
        else:
            self.project_period = ''

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('project.project')
        rec = super(Project, self).create(values)

        self.env['account.analytic.account'].create({
            'name': rec.name,
            'partner_id': rec.partner_id.id,
        })

        return rec
