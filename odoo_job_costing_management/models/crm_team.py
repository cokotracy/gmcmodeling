from odoo import fields, models, api, _


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    is_tender = fields.Boolean(compute='get_users', readonly=False)
    has_team_tender = fields.Boolean(string='Team Tender')

    @api.depends('is_tender')
    def get_users(self):
        for rec in self:
            users_group = self.env.ref('odoo_job_costing_management.group_project_tender_user').id
            users = self.env['res.users'].search([('groups_id', 'in', [users_group])])
            if rec.has_team_tender:
                rec.member_ids = [(6, 0, users.ids)]
                rec.is_tender = True
            else:
                rec.is_tender = False
                rec.member_ids = False
