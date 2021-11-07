# -*- coding: utf-8 -*-
from openerp import models, fields, _ ,api
from openerp.exceptions import Warning
from datetime import date

## Ahmed Salama Code Start ---->




class AccountLetter(models.Model):
    _name = "account.letter"
    _rec_name = 'name'
    _description = "Account Letters [LC/LG]"
    
    
    name = fields.Char('Name', size=128, required=True)
    number = fields.Char('Number', required=True)
    lc_value = fields.Float('Value', required=True)
    lc_margin = fields.Float('Margin', required=False)
    lc_margin_percent = fields.Float('Margin', required=False)
    journal_id = fields.Many2one('account.journal', 'Bank', required=True,
                                 domain=[('type','=','bank')]
                                 ,states = {'draft': [('readonly', False)]})
    lc_date_start = fields.Date('Start Date', required=True)
    lc_date_end = fields.Date('End Date', required=True)
    lc_bank_expense_value = fields.Float('Bank Expense Value', required=True)
    lc_managerial_expense = fields.Float('Managerial Expense Value', required=True)
    lc_manag_exp_account_id = fields.Many2one(string='Managerial Expense Account',
                                              comodel_name='account.account',
                                              required=True,compute='_get_default_account')
    currency_id = fields.Many2one('res.currency', string='Currency',)
    
    state = fields.Selection(
        [('draft', 'Draft'), ('validate', 'Validated'),('release', 'Releaseed'),('renewal', 'LG Renewal'),('liquidating', 'Liquidating'),('done', 'Done'),('draw', 'Withdrawed'),('cancel', 'Cancel')],
        'State', readonly=True, select=True,
        default='draft', tracking=True)
    
    _sql_constraints = [
        ('lc_unique_number', 'unique(number)','Choose another value - it has to be unique!')
    ]
    lc_commission_account_id = fields.Many2one(
        'account.account',
        'Bank Expense Account',
        compute = '_get_default_account',
        required=True,
        domain=[('user_type_id', '=', 'Expenses')], )
    
    lc_margin_account_id = fields.Many2one(
        'account.account',
        'Irrevocable liability',
        compute='_get_default_account',
        required=True,
        domain=[('user_type_id', 'in', ('Fixed Assets', 'Current Assets'))],
    
    
    )
    lc_loan_account_id = fields.Many2one(
        'account.account',
        'Loans Account',
        required=True,
        compute='_get_default_account'
    )
    lg_liquidating_account_id = fields.Many2one(
        'account.account',
        'Liquidating Account',
        required=True,
        compute='_get_default_account'
    )
    
    lc_liability_account_id = fields.Many2one(
        'account.account',
        'Irrevocable liability',
        required=False,
        domain=[('user_type_id', 'in', ('Current Liabilities', 'Non-current Liabilities', 'Payable'))],
    )
    lg_renewal_account_id = fields.Many2one(
        'account.account',
        'Renewal Account',
        required=True,
        compute='_get_default_account'
    )
    
    lc_journal_id = fields.Many2one(
        'account.journal',
        'Default journal',
        required=False, )
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account',
                                          string="Analytic Account",required=True)
    # @api.onchange('type')
    # def get_partner_domain(self):
    #     partner_obj = self.env['res.partner']
    #     partners = []
    #     if self.type:
    #         if self.type == 'credit':
    #             partners = partner_obj.search([('supplier','=',True)])
    #         elif self.type == 'guarantee':
    #             partners = partner_obj.search([('customer', '=', True)])
    #     domain = {'partner_id': [('id', 'in', [p.id for p in partners])]}
    #     return {'domain':domain}
    
    # ,domain=get_partner_domain

    partner_id = fields.Many2one(comodel_name='res.partner',
                                 string="Partner",required=True)
    type_id = fields.Many2one(comodel_name='account.letter.type',string="Type")
    type = fields.Selection(selection=[('credit','credit'),('guarantee','Guarantee')],string="Letter Type",required=True)
    is_draw = fields.Boolean(default=False)
    move_ids = fields.One2many('account.move', 'letter_id', readonly=True, copy=False, ondelete='restrict')
    renewal_ids = fields.One2many('account.letter.renewal', 'letter_id', readonly=True, copy=False, ondelete='restrict')
    release_ids = fields.One2many('account.letter.release', 'letter_id', readonly=True, copy=False, ondelete='restrict')
    # form_for_str = fields.Selection(string="Form 4?",selection=[('t','True'),('f','False')],defulat='t')
    form_for = fields.Boolean(string="Form 4?")


    def confirm_validate(self):
        payment_date=date.today()
        lc_margin_account_id = self.lc_margin_account_id.id
        lc_commission_account_id = self.lc_commission_account_id.id
        journal_id = self.journal_id
        
        name = journal_id.sequence_id.next_by_id()
        pre = 'LC Payment number ' if self.type == 'credit' else 'LG Payment number '
        ref = pre + self.number + ' / ' + self.name
        bank_related_account_id = self.journal_id.default_credit_account_id

        if self.type == 'credit':
            manag_exp_id = self.lc_manag_exp_account_id.id
            ## create entry with all needed lines
            move = self.create_cl_validation_entry(journal_id, payment_date, lc_commission_account_id,
                                                   manag_exp_id, lc_margin_account_id,
                                                   bank_related_account_id, name, ref)
            if move:
                self.state = 'validate'
                return move
            else:
                raise Warning("Something went wrong.\n The Entry doesn't created\n please review your administer.")
        if self.type == 'guarantee':
            ## create entry with all needed lines
            move = self.create_gl_validation_entry(journal_id, payment_date,
                                                   lc_commission_account_id,
                                                    lc_margin_account_id,
                                                   bank_related_account_id, name, ref)
            if move:
                self.state = 'validate'
                return move
            else:
                raise Warning("Something went wrong.\n The Entry doesn't created\n please review your administer.")
        
    def create_journal_entry(self, journal, payment_date, debit_account_id,
                             credit_account_id, name, ref, payment_value,entry_from):
        company_currency = self.env.user.company_id.currency_id
        if company_currency != self.currency_id:
            payment_value = self.currency_id.compute(payment_value, company_currency)
        debit_line_vals = {
            'name': name,
            'account_id': debit_account_id,
            'debit': payment_value,
            'ref': ref,
            'currency_id': self.currency_id and self.currency_id.id or False,
            'analytic_account_id': False
        }
        credit_analytic_account_id = False
        if entry_from == 'renewal' and self.analytic_account_id:
            credit_analytic_account_id = self.analytic_account_id.id
        credit_line_vals = {
            'name': name,
            'account_id': credit_account_id,
            'credit': payment_value,
            'ref': ref,
            'currency_id': self.currency_id and self.currency_id.id or False,
            'analytic_account_id': credit_analytic_account_id

        }
        
        move_vals = {
            'name': name,
            'journal_id': journal,
            'date': payment_date,
            'ref':  ref,
            'state':  'posted',
            'letter_id': self.id,
            'line_ids': [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
        }
        move = self.env['account.move'].create(move_vals)
        return move
    
    def create_cl_validation_entry(self,journal_id, payment_date, bank_expense_id,manag_exp_id,
                                   lc_account_id,bank_related_account_id, name, ref):
        company_currency = self.env.user.company_id.currency_id
        bank_exp_payment_value = self.lc_bank_expense_value
        manag_exp_payment_value = self.lc_managerial_expense
        lc_account_payment_value = self.lc_margin
        if company_currency != self.currency_id:
            bank_exp_payment_value = self.currency_id.compute(bank_exp_payment_value, company_currency)
            manag_exp_payment_value = self.currency_id.compute(manag_exp_payment_value, company_currency)
            lc_account_payment_value = self.currency_id.compute(lc_account_payment_value, company_currency)
        ##Bank Expense Account
        bank_exp_debit_line_vals = {
            'name': name,
            'account_id': bank_expense_id,
            'debit': bank_exp_payment_value,
            'ref': ref,
            'currency_id': self.currency_id and self.currency_id.id or False,
        }
        ##Managerial Expense Account
        manag_exp_debit_line_vals = {
            'name': name,
            'account_id': manag_exp_id,
            'debit': manag_exp_payment_value,
            'ref': ref,
            'currency_id': self.currency_id and self.currency_id.id or False,
        }
        ## LC Account
        lc_account_debit_line_vals = {
            'name': name,
            'account_id': lc_account_id,
            'debit': lc_account_payment_value,
            'ref': ref,
            'currency_id': self.currency_id and self.currency_id.id or False,
        }
        ## Bank Related Account
        if self.form_for:
            credit = sum([bank_exp_payment_value,manag_exp_payment_value])
        else:
            credit = sum([bank_exp_payment_value, manag_exp_payment_value, lc_account_payment_value])

        credit_line_vals = {
            'name': name,
            'account_id': bank_related_account_id.id,
            'credit': credit,
            'ref': ref,
            'currency_id': self.currency_id and self.currency_id.id or False,
            'analytic_account_id': self.analytic_account_id and self.analytic_account_id.id or False
        }
        ## Created Moves:
        if self.form_for:
            line_ids = [(0, 0, bank_exp_debit_line_vals), (0, 0, manag_exp_debit_line_vals)
                ,(0, 0, credit_line_vals)]
        else:
            line_ids = [(0, 0, bank_exp_debit_line_vals),(0, 0, manag_exp_debit_line_vals)
                    ,(0, 0, lc_account_debit_line_vals), (0, 0, credit_line_vals)]
        move_vals = {
            'name': name,
            'journal_id': journal_id.id,
            'date': payment_date,
            'ref':  ref,
            'state':  'posted',
            'letter_id': self.id,
            'line_ids': line_ids,
        }
        move = self.env['account.move'].create(move_vals)
        return move
    
    def create_gl_validation_entry(self,journal_id, payment_date, bank_expense_id,lg_account_id,
                                   bank_related_account_id, name, ref):
        company_currency = self.env.user.company_id.currency_id
        bank_exp_payment_value = self.lc_bank_expense_value
        lg_account_payment_value = self.lc_margin
        if company_currency != self.currency_id:
            bank_exp_payment_value = self.currency_id.compute(bank_exp_payment_value, company_currency)
            lg_account_payment_value = self.currency_id.compute(lg_account_payment_value, company_currency)
        ##Bank Expense Account
        bank_exp_debit_line_vals = {
            'name': name,
            'account_id': bank_expense_id,
            'debit': bank_exp_payment_value,
            'ref': ref,
            'currency_id': self.currency_id and self.currency_id.id or False,
            'analytic_account_id': self.analytic_account_id and self.analytic_account_id.id or False,
    
        }
        ## Bank Related Account with bank Expense value
        bank_exp_credit_line_vals = {
            'name': name,
            'account_id': bank_related_account_id.id,
            'credit': bank_exp_payment_value,
            'ref': ref,
            'currency_id': self.currency_id and self.currency_id.id or False,
        }
       
        ## LG Account
        lg_account_debit_line_vals = {
            'name': name,
            'account_id': lg_account_id,
            'debit': lg_account_payment_value,
            'ref': ref,
            'currency_id': self.currency_id and self.currency_id.id or False,
        }
        ## Bank Related Account Debit
        ## 'analytic_account_id': [(6, 0, [self.analytic_account_id.id])]
        lg_account_credit_line_vals = {
            'name': name,
            'account_id': bank_related_account_id.id,
            'credit': lg_account_payment_value,
            'ref': ref,
            'currency_id': self.currency_id and self.currency_id.id or False,
        }
        ## Created Moves:
        line_ids = [(0, 0, bank_exp_debit_line_vals),(0, 0, bank_exp_credit_line_vals)
                    ,(0, 0, lg_account_debit_line_vals), (0, 0, lg_account_credit_line_vals)]
        move_vals = {
            'name': name,
            'journal_id': journal_id.id,
            'date': payment_date,
            'ref':  ref,
            'state':  'posted',
            'letter_id': self.id,
            'line_ids': line_ids,
        }
        move = self.env['account.move'].create(move_vals)
        return move
    
    
    def confirm_cancel(self):
        self.state = 'cancel'
    
    
    def confirm_done(self):
        self.state = 'done'
    
    
    # def action_draw_lg(self):
    #     action = self.env.ref('bank_letters.action_wizard_lg_draw')
    #     result = action.read()[0]
    #     res = self.env.ref('bank_letters.wizard_lg_draw_view', False)
    #     result['views'] = [(res and res.id or False, 'form')]
    #     result['target'] = 'new'
    #     return result
    
    
    def button_journal_entries(self):
        return {
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('letter_id', 'in', self.ids)],
        }
    
    
    def action_renewal_lg(self):
        action = self.env.ref('bank_letters.action_wizard_lg_renewal')
        result = action.read()[0]
        res = self.env.ref('bank_letters.wizard_lg_renewal_view', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        return result
    
    
    def create(self, vals):
        if vals.get('lc_value') and vals.get('lc_margin_percent'):
            vals['lc_margin'] = vals.get('lc_value') * vals.get('lc_margin_percent') / 100
        letter = super(AccountLetter, self).create(vals)
        return letter
    
    
    def write(self, vals):
        if vals.get('lc_value') or vals.get('lc_margin_percent'):
            margin = vals.get('lc_value') or self.lc_value
            value = vals.get('lc_margin') or self.lc_margin
            vals['lc_margin'] = value * margin / 100
        super(AccountLetter, self).write(vals)
        return True
    
    
    @api.onchange('name')
    def _get_default_account(self):
        for letter in self:
            if letter.type == 'credit':
                config = self.env['bnk.lc.config'].search([],limit=1,order="id desc")
                if config:
                    letter.lc_margin_account_id = config.lc_account_id and config.lc_account_id.id or False
                    letter.lc_commission_account_id = config.lc_bank_exp_account_id and config.lc_bank_exp_account_id.id or False
                    letter.lc_loan_account_id = config.lc_loan_account_id and config.lc_loan_account_id.id or False
                    letter.lc_manag_exp_account_id = config.lc_manag_exp_account_id and config.lc_manag_exp_account_id.id or False
            if letter.type == 'guarantee':
                config = self.env['bnk.lg.config'].search([], limit=1, order="id desc")
                if config:
                    letter.lc_margin_account_id = config.lg_account_id and config.lg_account_id.id or False
                    letter.lc_commission_account_id = config.lg_bank_exp_account_id and config.lg_bank_exp_account_id.id or False
                    letter.lc_loan_account_id = config.lg_loan_account_id and config.lg_loan_account_id.id or False
                    letter.lg_renewal_account_id = config.lg_renewal_account_id and config.lg_renewal_account_id.id or False
                    letter.lg_liquidating_account_id = config.lg_liquidating_account_id and config.lg_liquidating_account_id.id or False

    
    def confirm_release(self):
        if self.form_for:
            action = self.env.ref('bank_letters.action_wizard_lc_release_form_4')
            res = self.env.ref('bank_letters.wizard_lc_release_view_form_4', False)
        else:
            action = self.env.ref('bank_letters.action_wizard_lc_release')
            res = self.env.ref('bank_letters.wizard_lc_release_view', False)

        result = action.read()[0]
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        return result
    
    
    def action_draw_lg(self):
        bank_related_account_id = self.journal_id.default_credit_account_id
        ref = 'LG With Draw number ' + self.number + ' / ' + self.name
        move = self.create_journal_entry(self.journal_id.id, date.today(), bank_related_account_id.id,
                                   self.lc_margin_account_id.id, self.name, ref, self.lc_margin,'draw')
        if move:
            self.state = 'draw'
        else:
            raise Warning("Something went wrong.\n The Entry doesn't created\n please review your administer.")
    
    
    def action_liquidating(self):
        partner_related_account_id = self.partner_id.property_account_receivable_id
        ref = 'LG Liquidating number ' + self.number + ' / ' + self.name
        company_currency = self.env.user.company_id.currency_id
        partner_value = self.lc_value
        liquidating_value = self.lc_value - self.lc_margin
        lg_value = self.lc_margin
        if company_currency != self.currency_id:
            partner_value = self.currency_id.compute(partner_value, company_currency)
            liquidating_value = self.currency_id.compute(liquidating_value, company_currency)
            lg_value = self.currency_id.compute(lg_value, company_currency)
        partner_debit_line_vals = {
            'name': self.name,
            'account_id': partner_related_account_id.id,
            'debit': partner_value,
            'ref': ref,
            'currency_id': self.currency_id and self.currency_id.id or False,
        }
        liquidating_credit_line_vals = {
            'name': self.name,
            'account_id': self.lg_liquidating_account_id.id,
            'credit': liquidating_value,
            'ref': ref,
            'currency_id': self.currency_id and self.currency_id.id or False,
            'analytic_account_id': self.analytic_account_id and self.analytic_account_id.id or False,

        }
        lg_credit_line_vals = {
            'name': self.name,
            'account_id': self.lc_margin_account_id.id,
            'credit': lg_value,
            'ref': ref,
            'currency_id': self.currency_id and self.currency_id.id or False,
        }

        move_vals = {
            'name': self.name,
            'journal_id': self.journal_id.id,
            'date': date.today(),
            'ref': ref,
            'state': 'posted',
            'letter_id': self.id,
            'line_ids': [(0, 0, partner_debit_line_vals),(0, 0, liquidating_credit_line_vals), (0, 0, lg_credit_line_vals)]
        }
        move = self.env['account.move'].create(move_vals)
        if move:
            self.state = 'liquidating'
        else:
            raise Warning("Something went wrong.\n The Entry doesn't created\n please review your administer.")


class LetterType(models.Model):
    _name = "account.letter.type"
    
    name = fields.Char('Name', size=128, required=True)
class AccountMoveInherit(models.Model):
    _inherit = 'account.move'
    
    letter_id = fields.Many2one('account.letter',string="Letter")


class lgRenwal(models.Model):
    _name = "account.letter.renewal"
    
    letter_id = fields.Many2one('account.letter', string="Letter")
    lg_date_end = fields.Date('End Date', required=True)
    lg_renewal_fees = fields.Float('Renewal Fees', required=True)
    move_id = fields.Many2one(string='Move',comodel_name='account.move', required=True)
    
class LcRelease(models.Model):
    _name = "account.letter.release"
    
    letter_id = fields.Many2one('account.letter', string="Letter")
    shipment_val = fields.Float(string="Shipment Amount")
    lc_val = fields.Float(string="LC Amount")
    loan_val = fields.Float(string="Loan Amount",)
## Ahmed Salama Code End.
