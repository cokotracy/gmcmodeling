# -*- coding: utf-8 -*-

from odoo import models, fields, api

class WorkPlanItemsLines(models.Model):
    _name = 'work.plan.items.line'

    name = fields.Char(string="Name", required=True, )
    work_plan_items_id = fields.Many2one(comodel_name="work.plan.items", string="", required=False, )


class WorkPlanItems(models.Model):
    _name = 'work.plan.items'

    project_id = fields.Many2one(comodel_name="project.project", string="Project", required=True, )
    work_plan_items_line_ids = fields.One2many(comodel_name="work.plan.items.line", inverse_name="work_plan_items_id", string="", required=False, )






