from odoo import api, fields, models,_
from odoo.exceptions import ValidationError,UserError
from datetime import date


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    user_ids = fields.Many2many('res.users', string="Approvers")
    is_disclaimer = fields.Boolean()

    @api.constrains('is_disclaimer')
    def _constrains_is_disclaimer(self):
        for rec in self:
            appr_cat = self.search([('is_disclaimer', '=', True),
                                   ('id', '!=', rec.id)])
            if appr_cat and rec.is_disclaimer:
                raise UserError(
                    _('Is Disclaimer Already Marked in %s.' % appr_cat.name)
                )

    @api.model
    def create(self, vals):
        res = super(ApprovalCategory, self).create(vals)
        departments = self.env['hr.department'].search([('disclaimer','=',True)])
        ids =[]
        for department in departments :
            ids.append(department.id)
            res.update({'user_ids': [(4, department.id)]})
        return res

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    is_disclaimer = fields.Boolean(related='category_id.is_disclaimer', stored=True)
    employee_id = fields.Many2one('hr.employee')
    loans = fields.Boolean()
    custody = fields.Boolean()
    equal_amount = fields.Boolean()
    maintenance = fields.Boolean()
    engineering = fields.Boolean()

    def action_confirm(self):
        res = super(ApprovalRequest, self).action_confirm()
        if self.employee_id:
            ids = []
            for line in self.approver_ids:
                vals = {
                    'status' :line.status,
                    'user_id': line.user_id.id
                }
                rec = self.env['approval.approver.employee'].create(vals)
                ids.append(rec.id)
            self.employee_id.update({
                'approver_lines':[(6, 0, ids)]
            })
        return res

    def action_approve(self, approver=None):
        res = super(ApprovalRequest, self).action_approve(approver=None)
        object = self.env['approval.approver.employee'].search([('employee_id','=',self.employee_id.id),('user_id','=',self.env.user.id)])
        if object:
            object.update(
                {
                    'status':'approved',
                    'date': fields.Date.today()
                }
            )
        return res

    def action_refuse(self, approver=None):
        res = super(ApprovalRequest,self).action_refuse(approver=None)
        object = self.env['approval.approver.employee'].search([('employee_id','=',self.employee_id.id),('user_id','=',self.env.user.id)])
        if object:
            object.update(
                {
                    'status':'refused',
                    'date': fields.Date.today()
                }
            )
        return res

    def action_withdraw(self, approver=None):
        res = super(ApprovalRequest,self).action_withdraw(approver=None)
        object = self.env['approval.approver.employee'].search([('employee_id','=',self.employee_id.id),('user_id','=',self.env.user.id)])
        if object:
            object.update(
                {
                    'status':'pending',
                    'date': fields.Date.today()
                }
            )
        return res

    def action_cancel(self, approver=None):
        res = super(ApprovalRequest,self).action_cancel()
        object = self.env['approval.approver.employee'].search([('employee_id','=',self.employee_id.id),('user_id','=',self.env.user.id)])
        if object:
            object.update(
                {
                    'status':'cancel',
                    'date': fields.Date.today()
                }
            )
        return res

    def action_draft(self):
        res = super(ApprovalRequest,self).action_draft()
        object = self.env['approval.approver.employee'].search([('employee_id','=',self.employee_id.id),('user_id','=',self.env.user.id)])
        if object:
            object.unlink()
        return res


    @api.depends('approver_ids.status')
    def _compute_request_status(self):
        for request in self:
            status_lst = request.mapped('approver_ids.status')
            minimal_approver = request.approval_minimum if len(status_lst) >= request.approval_minimum else len(status_lst)
            if status_lst:
                if status_lst.count('cancel'):
                    status = 'cancel'
                elif status_lst.count('refused'):
                    status = 'refused'
                elif status_lst.count('new'):
                    status = 'new'
                elif status_lst.count('approved') >= minimal_approver:
                    status = 'approved'
                else:
                    status = 'pending'
            else:
                status = 'new'
            request.request_status = status
