from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class SalesOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[
        ('sm_approval', 'SM approval'),
        ('ap_approval', 'AP approval'),
        ('sale', 'Sales Order')])

    hide = fields.Boolean(compute='compute_type')

    type = fields.Char(compute='compute_type')

    def send_to_sm_state(self):
        for user in self.env['res.users'].search([]):
            if user.has_group('sales_enhancement.group_sale_approval1'):
                sale_manager_user = user
                mail_content = "Dear Mr." + sale_manager_user.name + "\n" + "Quotation order Number : " + self.name \
                               + ". has been confirmed and wait your approval."
                main_content = {
                    'subject': _('Purchase Requisition Approval'),
                    'author_id': self.env.user.company_id.id,
                    'body_html': mail_content,
                    'email_to': sale_manager_user.partner_id.email,
                }
                self.env['mail.mail'].sudo().create(main_content).send()
        self.write({'state': 'sm_approval'})

    def send_to_ap_state(self):
        for user in self.env['res.users'].search([]):
            if user.has_group('sales_enhancement.group_sale_approval2'):
                accountant_user = user
                mail_content = "Dear Mr." + accountant_user.name + "\n" + "Quotation order Number : " + self.name \
                               + ". has been confirmed and wait your approval."
                main_content = {
                    'subject': _('Purchase Requisition Approval'),
                    'author_id': self.env.user.company_id.id,
                    'body_html': mail_content,
                    'email_to': accountant_user.partner_id.email,
                }
                self.env['mail.mail'].sudo().create(main_content).send()
        self.write({'state': 'ap_approval'})

    @api.onchange('partner_id')
    def compute_type(self):
        for rec in self:
            if rec.partner_id.customer_type == 'cash':
                rec.type = 'cash'
                rec.hide = False
            elif rec.partner_id.customer_type == 'credit':
                rec.type = 'credit'
                if rec.state == 'draft':
                    rec.hide = True
            elif rec.partner_id.customer_type == 'subcontracting':
                rec.type = 'subcontracting'
                if rec.state == 'draft':
                    rec.hide = True


    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        if self.env.user.has_group('sales_enhancement.group_sale_approval1') or \
                self.env.user.has_group('sales_enhancement.group_sale_approval2'):
            self.write({
                'state': 'sale',
                'confirmation_date': fields.Datetime.now()
            })
        else:
            raise ValidationError(
                _('Not Allowed , You are not Manager to approve on this Quotation order'))
        self._action_confirm()

        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()
        return True
