# -*- coding: utf-8 -*-

from odoo import models, fields, api,exceptions

class GuaranteeLiteerLine(models.Model):
    _name = 'guarantee.letter.line'

    attachment_id = fields.Binary(string="Attachment",  required=True, )
    note = fields.Text(string="Note", required=False, )
    guarantee_id = fields.Many2one(comodel_name="guarantee.letter", string="", required=False, )



class GuaranteeLiteer(models.Model):
    _name = 'guarantee.letter'

    name = fields.Char(string="Name",default='New' ,required=False, )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=False, )
    project_id = fields.Many2one(comodel_name="project.project", string="Project", required=True, )
    submission_date = fields.Date(string="Submission Date", required=False, )
    tender_qty = fields.Float(string="Tender Quantity",  required=False, )
    bid_bond_amount = fields.Float(string="Bid Bond Amount",  required=False, )
    state = fields.Selection(string="State", selection=[('draft', 'Draft'), ('confirmed', 'Confirmed'), ], default='draft' , required=False, )

    type_id = fields.Many2many(comodel_name="guarantee.types", string="Guarantee Types", required=False, )

    guarantee_line_ids = fields.One2many(comodel_name="guarantee.letter.line", inverse_name="guarantee_id", string="", required=False, )

    @api.model
    def create(self, vals):
        res = super(GuaranteeLiteer, self).create(vals)

        res.name = self.env['ir.sequence'].next_by_code('guarantee.letter.code')


        return res

    def confirm_guarantee_letter(self):
        for rec in self:
            if not rec.guarantee_line_ids:
                raise exceptions.ValidationError('You Must Sett Attachment Before Confirmation ')
            users = []
            for user in self.env.ref('project.group_project_user').users:
                users.append(user.partner_id.id)
            thread_pool = self.env['mail.thread']
            if False not in users:
                thread_pool.message_notify(
                    partner_ids=users,
                    subject="Guarantee Letter Notification",
                    body='This Guarantee Letter Is Confirmed: <a target=_BLANK href="/web?#id=' + str(
                        rec.id) + '&view_type=form&model=guarantee.letter&action=" style="font-weight: bold">' + str(
                        rec.name) + '</a>',
                    # email_from=self.env.user.company_id.catchall or self.env.user.company_id.email, )
                    email_from=self.env.user.company_id.email, )
            self.state = 'confirmed'


class GuaranteeTypes(models.Model):
    _name = 'guarantee.types'
    _rec_name = 'name'
    _description = 'Guarantee Types'

    name = fields.Char(string="Name", required=False, )
