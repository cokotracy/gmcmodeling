# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError
from odoo.fields import Date, Datetime
from datetime import date, datetime, time, timedelta
import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ProjectsWizarddReport(models.TransientModel):
    _name = "projects.wizard.report"

    def print_report(self):
        data = {}
        projects = []
        for rec in self.env['project.project'].search([]).sorted(lambda r: r.state):
            projects.append({
                'project_no': rec.project_no,
                'project_name': rec.name,
                'partner_name': rec.partner_id.name,
                'request_date': rec.project_start_date,
                'due_date': rec.project_end_date,
                'state': str(dict(rec._fields['state'].selection).get(rec.state)),
            })
        data['projects'] = projects
        return self.env.ref('wc_construction.print_report_id_projects').report_action(self, data=data)


class ProjectReport(models.AbstractModel):
    _name = 'report.wc_construction.print_report_template_projects'

    @api.model
    def _get_report_values(self, docids, data=None):
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('wc_construction.print_report_template_projects')
        projects = data.get('projects')

        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'projects': projects,
        }
