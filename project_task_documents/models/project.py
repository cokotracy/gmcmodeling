# -*- coding: utf-8 -*-
# Copyright 2019 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, tools, SUPERUSER_ID, _

import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of attached documents")
    is_job_document = fields.Boolean()
    is_job_schedule = fields.Boolean()

    def _compute_attached_docs_count(self):
        attachment_obj = self.env['ir.attachment']
        domain = []
        for task in self:
            task.doc_count = attachment_obj.search_count([
                '&', ('res_model', '=', 'project.task'), ('res_id', '=', task.id)
            ])
            if task.project_id:
                if task.is_job_document:
                    domain = [('res_model', '=', 'project.project'),
                              ('res_id', '=', task.project_id.id),
                              ('attach_document', '=', True)]
                elif task.is_job_schedule:
                    domain = [('res_model', '=', 'project.project'),
                              ('res_id', '=', task.project_id.id),
                              ('attach_schedule', '=', True)]
                if domain:
                    task.doc_count = attachment_obj.search_count(domain)

    def attached_docs_view_action(self):
        self.ensure_one()
        if self.is_job_document:
            domain = [('res_model', '=', 'project.project'),
                      ('res_id', '=', self.project_id.id), ('attach_document', '=', True)]
        elif self.is_job_schedule:
            domain = [('res_model', '=', 'project.project'),
                      ('res_id', '=', self.project_id.id), ('attach_schedule', '=', True)]
        else:
            domain = ['&', ('res_model', '=', 'project.task'), ('res_id', 'in', self.ids)]

        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached to the tasks of your project.</p>
                    '''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }
