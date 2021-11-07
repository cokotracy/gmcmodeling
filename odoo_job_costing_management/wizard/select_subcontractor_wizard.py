from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api


class SubSubcontractor(models.TransientModel):
    _name = 'select.subcontractor'
    _description = 'Select Subcontractor'

    sub_contractors = fields.Many2many('res.partner', string='Subcontractor')

    def select_contractors(self):
        job_cost_id = self.env['job.costing'].browse(self._context.get('active_id', False))
        for sub_contractor in self.sub_contractors:
            job_cost_id.write({
                'subcontractor_line_ids':[(1, sub_contractor.id,{
                    'name': sub_contractor.name,
                    'phone': sub_contractor.phone,
                    'email': sub_contractor.email,
                    'company_id': sub_contractor.company_id.id,
                    'job_id': job_cost_id.id

                })]
            })


class Labours(models.TransientModel):
    _name = 'select.labour'
    _description = 'Select Labour'

    labour_ids = fields.Many2many('hr.employee', string='Labour')

    def select_labours(self):
        job_cost_id = self.env['job.costing'].browse(self._context.get('active_id', False))
        for labour in self.labour_ids:
            job_cost_id.write({
                'job_labour_line_ids': [(1, labour.id, {'name': labour.name,'job_cost_id_employee': job_cost_id.id})],
            })


class SelectEquipment(models.TransientModel):
    _name = 'select.equipment'
    _description = 'Select Equipment'

    equipment_line_ids = fields.Many2many('maintenance.equipment', string='Equipment')

    def select_equipment(self):
        job_cost_id = self.env['job.costing'].browse(self._context.get('active_id', False))
        for equipment in self.equipment_line_ids:
            job_cost_id.write({
                'equipment_line_ids' : [(1, equipment.id, {
                    'name': equipment.name,
                    'employee_id': equipment.employee_id.id,
                    'department_id': equipment.department_id.id,
                    'assign_date': equipment.assign_date,
                    'category_id': equipment.category_id.id,
                    'company_id': equipment.company_id.id,
                    'job_id': job_cost_id.id
                })]
            })

