# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import html2plaintext


class Note(models.Model):
    _inherit = 'note.note'

    @api.onchange('task_id')
    def onchange_task(self):
        for rec in self:
            rec.project_id = rec.task_id.project_id.id

    project_id = fields.Many2one(
        'project.project',
        string='Construction Project',
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task / Job Order',
    )
    is_task = fields.Boolean(
        string='Is Job Order?',
    )
    is_project = fields.Boolean(
        string='Is Project?',
    )


class Attachment(models.Model):
    _inherit = "ir.attachment"

    attach_schedule = fields.Boolean(string='POQ')
    attach_document = fields.Boolean(string='DOC')
