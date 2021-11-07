# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, safe_eval

class WizardDC(models.TransientModel):
    _name = 'wizard.dc'

    projectID = fields.Char(string="Project ID", required=False, )
    project_id = fields.Many2one(comodel_name="project.project", string="Project Name", required=False, )
    transaction_id = fields.Char(string="Transaction ID", required=False, )
    revision_no = fields.Char(string="Revision No", required=False, )
    submission_date_from = fields.Date(string="From Submission Date", required=False,)
    submission_date_to = fields.Date(string="To Submission Date", required=False,)
    ref = fields.Char(string="Reference", required=False, )
    submittal_type = fields.Selection(string="Submittal Type", selection=[('dc', 'Document Control'), ('mt', 'Material'),('dw','Drawing') ], required=False, )
    scope_of_work_id = fields.Many2one(comodel_name="work.scope", string="Scope Of Work", required=False, )

    def print_dc_xls(self):

        return self.env.ref('wc_document_control.dc_xlsx').report_action(self)
