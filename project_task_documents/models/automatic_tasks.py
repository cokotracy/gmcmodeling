from odoo import fields, models, api, _


class AutomaticTasks(models.Model):
    _name = 'automatic.tasks'

    name = fields.Char(string='Task Name', required=True)
    stage_id = fields.Many2one(comodel_name='project.task.type', required=True)
    sequence = fields.Integer(string='Sequence', required=True)
    is_job_document = fields.Boolean()
    is_job_schedule = fields.Boolean()
