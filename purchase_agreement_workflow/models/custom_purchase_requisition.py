# -*- coding: utf-8 -*-
# Add By Omnya 13/04/2020
from odoo import models, fields, _,api
from odoo.exceptions import UserError, ValidationError

PURCHASE_REQUISITION_STATES = [
    ('draft', 'Draft'),
    ('dep_manager', 'Dep Manager Approval'),
    ('approved', 'Approved'),
    ('in_progress', 'Confirmed'),
    ('open', 'Bid Selection'),
    ('done', 'Closed'),
    ('cancel', 'Cancelled')
]


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    employee_check = fields.Boolean(compute="get_related_employee", default=False)

    @api.depends('employee_check')
    def get_related_employee(self):
        for item in self:
            employee_id = self.env['hr.employee'].search([('user_id', '=', item.create_uid.id)])
            current_user_id = self.env.uid
            employee_manager = self.env['hr.employee'].search([('user_id', '=', current_user_id)])

            if employee_id.department_id.manager_id.id == employee_manager.id:
                item.employee_check = True
            else:
                item.employee_check = False


    state = fields.Selection(PURCHASE_REQUISITION_STATES, string='Status', tracking=True, required=True,
                             copy=False, default='draft')
    state_blanket_order = fields.Selection(PURCHASE_REQUISITION_STATES, compute='_set_state')
    def action_in_progress(self):
        res=super(PurchaseRequisition, self).action_in_progress()

        employee_id = self.env['hr.employee'].search([('user_id', '=', self.create_uid.id)])
        manager_id = employee_id.department_id.manager_id
        user_id = self.kindpo_id.user_id.id
        activity_ins = self.env['mail.activity'].sudo()
        activity_ins.create(
            {'res_id': self.id,
             'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.requisition')],
                                                         limit=1).id,
             'res_model': 'purchase.requisition',
             'activity_type_id': 3,
             'summary': 'Purchase Agreement is Approved',
             'note': _(
                 'THE purchase agreement record with the ID %s is approved by Your Manager %s') % (
                         self.id, manager_id.name),
             'date_deadline': fields.Date.today(),
             'activity_category': 'default',
             'previous_activity_type_id': False,
             'recommended_activity_type_id': False,
             'user_id': user_id
             })

        self.write({'state': 'approved'})
        return res
    def approve_dep_manager(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.create_uid.id)])
        print(self.create_uid.id)

        user_id = employee_id.department_id.manager_id.user_id.id
        activity_ins = self.env['mail.activity'].sudo()
        activity_ins.create(
            {'res_id': self.id,
             'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.requisition')],
                                                         limit=1).id,
             'res_model': 'purchase.requisition',
             'activity_type_id': 3,
             'summary': 'Purchase Agreement is  Needed To Approve',
             'note': _(
                 'please we need Your Approve on this purchase agreement'),
             'date_deadline': fields.Date.today(),
             'activity_category': 'default',
             'previous_activity_type_id': False,
             'recommended_activity_type_id': False,
             'user_id': user_id
             })
        self.write({'state': 'dep_manager'})
    def action_cancel(self):
        res = super(PurchaseRequisition, self).action_cancel()
        current_user_id = self.env.uid
        employee_manager = self.env['hr.employee'].search([('user_id', '=', current_user_id)])

        activity_ins = self.env['mail.activity'].sudo()
        activity_ins.create(
            {'res_id': self.id,
             'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.requisition')],
                                                         limit=1).id,
             'res_model': 'purchase.requisition',
             'activity_type_id': 3,
             'summary': 'Purchase Agreement is Canceled',
             'note': _(
                 'THE purchase agreement record with the ID %s is canceled by Your Manager %s Back to Him Please') % (
                     self.id,employee_manager.name),
             'date_deadline': fields.Date.today(),
             'activity_category': 'default',
             'previous_activity_type_id': False,
             'recommended_activity_type_id': False,
             'user_id': self.create_uid.id
             })
        return res

    def action_reject(self):

        current_user_id = self.env.uid
        employee_manager = self.env['hr.employee'].search([('user_id', '=', current_user_id)])

        activity_ins = self.env['mail.activity'].sudo()
        activity_ins.create(
            {'res_id': self.id,
             'res_model_id': self.env['ir.model'].search([('model', '=', 'purchase.requisition')],limit=1).id,
             'res_model': 'purchase.requisition',
             'activity_type_id': 3,
             'summary': 'Purchase Agreement is Rejected',
             'note': _(
                 'THE purchase agreement record with the ID %s is Rejected by Your Manager %s Back to Him Please') % ( self.id, employee_manager.name),
             'date_deadline': fields.Date.today(),
             'activity_category': 'default',
             'previous_activity_type_id': False,
             'recommended_activity_type_id': False,
             'user_id': self.create_uid.id
             })
        self.write({'state': 'draft'})



