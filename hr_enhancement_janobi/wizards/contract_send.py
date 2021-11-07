# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons.mail.wizard.mail_compose_message import _reopen


class ContractSend(models.TransientModel):
    _name = 'hr.applicant.contract.send'
    _inherits = {'mail.compose.message': 'composer_id'}
    _description = 'Contract Send'

    applicant_id = fields.Many2one(comodel_name='hr.applicant', string='Applicant')
    composer_id = fields.Many2one('mail.compose.message', string='Composer', required=True, ondelete='cascade')
    template_id = fields.Many2one('mail.template', 'Use template', index=True,
                                  domain="[('model', '=', 'hr.applicant')]")

    @api.model
    def default_get(self, fields):
        res = super(ContractSend, self).default_get(fields)
        res_id = self._context.get('active_id')

        applicant = self.env['hr.applicant'].browse(res_id)

        composer = self.env['mail.compose.message'].create({'composition_mode': 'comment'})
        self.onchange_template_id()
        res.update({
            'applicant_id': applicant.id,
            'composer_id': composer.id,
        })
        return res

    @api.onchange('template_id')
    def onchange_template_id(self):
        if self.composer_id:
            self.composer_id.template_id = self.template_id.id
            self.composer_id.onchange_template_id_wrapper()

    def _send_email(self):
        self.composer_id.send_mail()

    def send_action(self):
        self.ensure_one()
        self._send_email()
        return {'type': 'ir.actions.act_window_close'}

    def save_as_template(self):
        self.ensure_one()
        self.composer_id.save_as_template()
        action = _reopen(self, self.id, self.model, context=self._context)
        action.update({'name': _('Send Contract')})
        return action


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    country_id = fields.Many2one(comodel_name='res.country', string='Country')
    passport_id = fields.Char(string='Passport Number')
    contract_type = fields.Selection(string='Contract Type', selection=[('1', '1 Year'),
                                                                        ('2', '2 Years'),
                                                                        ('other', 'Other')])
    meal_allowance = fields.Float(string='Meal Allowance')
    other_allowance = fields.Float(string='Other Allowances')

    def open_contract_send_wizard(self):
        self.ensure_one()
        template = self.env.ref('hr_enhancement_janobi.email_template_contract', raise_if_not_found=False)
        compose_form = self.env.ref('hr_enhancement_janobi.contract_send_wizard_form', raise_if_not_found=False)
        ctx = dict(
            default_model='hr.applicant',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            force_email=True
        )
        return {
            'name': _('Send Contract'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.applicant.contract.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
