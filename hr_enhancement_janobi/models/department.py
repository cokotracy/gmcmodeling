from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError



class HrDepartment(models.Model):
    _inherit = 'hr.department'


    disclaimer = fields.Boolean()


    @api.model
    def create(self, vals):
        res = super(HrDepartment, self).create(vals)
        if res.disclaimer and res.manager_id:
            approve_type = self.env['approval.category'].search([('is_disclaimer','=',True)])
            if not approve_type :
                raise UserError(_("Can not find Approval Type with Disclaimer"))
            else :
                managers_ids = []
                for id in approve_type.user_ids:
                    managers_ids.append(id.id)
                if res.manager_id.id not in managers_ids:
                    if res.manager_id.user_id:
                        for approve in approve_type:
                            approve.update({'user_ids': [(4, res.manager_id.user_id.id)]})
                    else:
                        raise UserError(_("There is no related user to the manager"))

        return res

    def write(self, vals):
        res = super(HrDepartment, self).write(vals)

        if self.disclaimer and self.manager_id:
            approve_type = self.env['approval.category'].search([('is_disclaimer','=',True)])
            if not approve_type :
                raise UserError(_("Can not find Approval Type with Disclaimer"))
            else :
                managers_ids = []
                for id in approve_type.user_ids:
                    managers_ids.append(id.id)
                if self.manager_id.id not in managers_ids:
                    if self.manager_id.user_id:
                        for approve in approve_type:
                            approve.update({'user_ids': [(4, self.manager_id.user_id.id)]})
                    else:
                        raise UserError(_("There is no related user to the manager"))

        return res




