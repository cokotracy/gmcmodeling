# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero


class Expense(models.Model):
    _inherit = 'hr.expense'

    def action_move_create(self):
        '''
        main function that is called when trying to create the accounting entries related to an expense
        '''
        move_line_values_by_expense = self._get_account_move_line_values()
        move_group_by_sheet = []

        move_grouped_by_sheet = {}
        for expense in self:
            # create the move that will contain the accounting entries
            move_vals = expense._prepare_move_values()
            move_vals['date'] = expense.date
            move = self.env['account.move'].with_context(default_journal_id=move_vals['journal_id']).create(move_vals)
            move_grouped_by_sheet[expense.sheet_id.id] = move


            # get the account move of the related sheet
            # get move line values
            move_line_values = move_line_values_by_expense.get(expense.id)

            move.write({'line_ids': [(0, 0, line) for line in move_line_values]})
            expense.sheet_id.write({'account_move_id': move.id})

            if expense.payment_mode == 'company_account':
                expense.sheet_id.paid_expense_sheets()

            # post the moves
            # for move in move_grouped_by_sheet.values():
            move._post()
            move_group_by_sheet.append(move_grouped_by_sheet)

        return move_group_by_sheet


class ExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    expense_type = fields.Selection([('expense', 'Expense'), ('project', 'Project')],string='Expense type')


class Expense(models.Model):
    _inherit = 'hr.expense'

    expense_type = fields.Selection([('expense', 'Expense'), ('project', 'Project')],string='Expense type',related='sheet_id.expense_type')

    project_id = fields.Many2one('project.project','Project')

    tasks_ids = fields.Many2many('project.task',string='Tasks')

    @api.onchange('project_id')
    def project_onchange(self):
        if self.project_id:
            self.analytic_account_id = self.project_id.analytic_account_id.id
            task_data = self.env['project.task'].search([('project_id', '=',self.project_id.id)])
            ids=[]
            for task in task_data :
                # ids.append(task.id)
                # raise Warning(task.id)
                self.update({'tasks_ids': [(4,task.id )]})
