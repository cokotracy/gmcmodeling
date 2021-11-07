# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero

class ExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    state = fields.Selection(selection_add=[('manager_revision', 'Manager Revision'),('approve',) ], required=False, )
    is_expense_manager = fields.Boolean(string="",compute='check_expense_manager'  )
    manager_revision_id = fields.Many2one(comodel_name="res.users", string="Manager Revision", required=False, )

    @api.depends('is_expense_manager')
    def check_expense_manager(self):
        if self.state == 'manager_revision':
            if self.env.user.id == self.user_id.id:
                self.is_expense_manager = True
            else:
                self.is_expense_manager = False
        else:
            self.is_expense_manager = False

    def manager_revision_button(self):
        self.state = 'manager_revision'
        self.manager_revision_id = self.env.user.id

        revision_manager_group = self.env.ref("wc_expense.group_revision_expense_manager")
        revision_managers = []
        for user_group in self.env['res.groups'].search([('id', '=', revision_manager_group.id)]):
            for user1 in user_group.users:
                revision_managers.append(user1.partner_id.id)

        thread_pool = self.env['mail.thread']
        if False not in revision_managers:
            thread_pool.message_notify(
                partner_ids=revision_managers,
                subject="Expense Approve Notification",
                body='This Expense Need Your Approval: <a target=_BLANK href="/web?#id=' + str(
                    self.id) + '&view_type=form&model=hr.expense.sheet&action=" style="font-weight: bold">' + str(
                    self.name) + '</a>',
                email_from=self.env.user.company_id.catchall or self.env.user.company_id.email, )


class Expense(models.Model):
    _inherit = 'hr.expense'

    def _prepare_move_values(self):
        """
        This function prepares move values related to an expense
        """
        self.ensure_one()
        journal = self.sheet_id.bank_journal_id if self.payment_mode == 'company_account' else self.sheet_id.journal_id
        account_date = self.sheet_id.accounting_date or self.date
        move_values = {
            'journal_id': journal.id,
            'company_id': self.sheet_id.company_id.id,
            'date': account_date,
            'ref': self.sheet_id.name,
            # force the name to the default value, to avoid an eventual 'default_name' in the context
            # to set it to '' which cause no number to be given to the account.move when posted.
            'name': '/',
            'expense_sheet_id': self.sheet_id.id,
        }
        return move_values

