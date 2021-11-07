# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import time

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    bonus_ids = fields.One2many('employee.bonus', 'employee_id', string='Bonuses')
    
    
    def action_show_custom_employeebonus(self):
        self.ensure_one()
        return {
            'name': _('Employee Bonuses'),
            'view_mode': 'tree,form',
            'res_model': 'employee.bonus',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.bonus_ids.ids)],
            'target': 'current',
        }
    
#     def get_bonus_amounts(self, emp_id, date_from, date_to=None):
#         if date_to is None:
#             date_to = datetime.now().strftime('%Y-%m-%d')
#         self._cr.execute("SELECT sum(o.bonus_amount) from employee_bonus as o where \
#                             o.inculde_in_payroll IS TRUE and o.employee_id=%s \
#                             and o.state='approved_hr_manager' AND  o.payroll_date >= %s AND o.payroll_date <= %s ",
#                             (emp_id, date_from, date_to))
#         res = self._cr.fetchone()
#         return res and res[0] or 0.0


