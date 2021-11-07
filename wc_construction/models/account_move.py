# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

from datetime import datetime, date
from num2words import num2words
from collections import defaultdict



class AccountTax(models.Model):
    _inherit = 'account.tax'

    is_contract_tax = fields.Boolean(string="Contract Tax", )
    down_payment_tax_account_id = fields.Many2one(comodel_name="account.account", string="إستحقاق دفعه مقدمه",
                                                  required=False, )


class Talyat(models.Model):
    _name = 'talyat.talyat'
    _rec_name = 'name'
    _description = ''

    name = fields.Char(string="Name", required=False, )
    account_id = fields.Many2one(comodel_name="account.account", string="Account", required=False, )


class Deductions(models.Model):
    _name = 'deduct.deduct'
    _rec_name = 'name'
    _description = ''

    name = fields.Char(string="Name", required=False, )
    account_id = fields.Many2one(comodel_name="account.account", string="Account", required=False, )


class AccountMove(models.Model):
    _inherit = 'account.move'


    contract_quotation_id = fields.Many2one(comodel_name="sale.order", string="Contract Quotation", required=False, )
    contract_project_id = fields.Many2one(comodel_name="project.project", string="Contract Project", required=False, )
    is_contract_invoice = fields.Boolean(string="", )
    contract_type_id = fields.Many2one(comodel_name="contracts", string="Contract Type", required=False, )
    contract_id = fields.Many2one(comodel_name="owner.contract", string="Contract",
                                  domain=[('state', '=', 'confirmed')], required=False, )
    contract_type = fields.Selection(string="Contract Type",
                                     selection=[('contractor', 'Contractor'), ('subcontractor', 'Subcontractor'), ],
                                     required=False, )
    prev_contract_invoices = fields.Integer(string="", compute='get_prev_contract_invoices', required=False, )
    prev_contract_bills = fields.Integer(string="", compute='get_prev_contract_bills', required=False, )
    contract_products_ids = fields.Many2many(comodel_name="product.product", compute='get_contract_products',
                                             string="", )
    addition_ids = fields.One2many(comodel_name="invoice.addition", inverse_name="move_id", string="", required=False, )
    deduction_ids = fields.One2many(comodel_name="invoice.deduction", inverse_name="move_id", string="",
                                    required=False, )

    total_deductions = fields.Monetary(string="Total Deductions", required=False, compute="get_totals")
    total_additions = fields.Monetary(string="Total Additions", required=False, compute="get_totals")
    total_with_deduct_addition = fields.Monetary(string="Net Total", required=False, compute="get_totals")
    deduction_journal_id = fields.Many2one(comodel_name="account.move", string="Deduction Journal", required=False, )
    addition_journal_id = fields.Many2one(comodel_name="account.move", string="Addition Journal", required=False, )
    # Add by omnya
    discount_amount = fields.Float(string='Discount')
    invoice_final = fields.Boolean(string='Final Subcontractor Invoice')

    down_payment_fixed = fields.Float(string="Down Payment Fixed", compute='get_down_payment_fixed', required=False, )
    down_payment_percentage = fields.Float(string="Down Payment(%)", required=False, )
    performance = fields.Float(string="Performance bond (%)", required=False, )
    performance_amount = fields.Float(string="Performance Amount", compute='get_performance_amount', required=False, )
    retation_amount = fields.Float(string="Retention (%)", required=False, )
    retation_amount_value = fields.Float(string="Retention Amount", compute='get_retation_amount_value',
                                         required=False, )
    down_payment_account_id = fields.Many2one(comodel_name="deduction.accounts", string="Down Payment Type",
                                              domain=[('deduction_type', '=', 'down_payment')], required=False, )
    performance_account_id = fields.Many2one(comodel_name="deduction.accounts", string="Performance Type",
                                             domain=[('deduction_type', '=', 'performance_bond')], required=False, )
    retention_account_id = fields.Many2one(comodel_name="deduction.accounts", string="Retention Type",
                                           domain=[('deduction_type', '=', 'retention')], required=False, )
    p_d_r_journal = fields.Many2one(comodel_name="account.move", string="Journal Entry", required=False, )

    cashing_done = fields.Float(string="ما تم صرفه", compute='get_chashing_done_and_previous_chashing',
                                required=False, )
    previous_chashing = fields.Float(string="ما سبق", compute='get_chashing_done_and_previous_chashing',
                                     required=False, )
    talyat = fields.Monetary(string="تعليات", required=False, )
    deductions = fields.Monetary(string="استقطاعات", required=False, )
    talyat_id = fields.Many2one(comodel_name="talyat.talyat", string="تعليــات", required=False, )
    deductions_id = fields.Many2one(comodel_name="deduct.deduct", string="استقطــاعات", required=False, )

    all_total_amount_invoices = fields.Monetary(string="Total Amount", compute='get_all_total_amount_invoices',
                                                required=False, )
    all_cashing_done = fields.Monetary(string="ما تم تحصيلة", compute='get_chashing_done_and_previous_chashing',
                                       required=False, )
    total_amount_invoices_all_cashing_done = fields.Monetary(string="الإجمالي الحالي",
                                                             compute='get_total_amount_invoices_all_cashing_done',
                                                             required=False, )
    state = fields.Selection(selection_add=[('dep_approved', 'Department Approved'),
                                            ('gm_approved', 'GM Approved'),
                                            ('posted',)], required=False)

    is_need_approve = fields.Boolean(string="", compute='check_need_approve')
    validate_done_approve = fields.Boolean(string='Validated', invisible=1, default=False)

    total_retention = fields.Monetary(string='Total Retention')
    total_down_payment = fields.Monetary(string='Total Down Payment')
    total_performance = fields.Monetary(string='Total Performance')
    lines_updated = fields.Boolean()

    amount_words = fields.Char('Amount in Words:',
                               help="The invoice total amount in words is automatically generated by the system..few languages are supported currently",
                               compute='_compute_num2words')
    project_id = fields.Many2one('account.analytic.account', string='Project', copy=False)

    @api.constrains('ref', 'move_type', 'partner_id', 'journal_id', 'invoice_date')
    def _check_duplicate_supplier_reference(self):
        moves = self.filtered(lambda move: move.is_purchase_document() and move.ref and move.contract_type != 'subcontractor')
        if not moves:
            return

        self.env["account.move"].flush([
            "ref", "move_type", "invoice_date", "journal_id",
            "company_id", "partner_id", "commercial_partner_id",
        ])
        self.env["account.journal"].flush(["company_id"])
        self.env["res.partner"].flush(["commercial_partner_id"])

        # /!\ Computed stored fields are not yet inside the database.
        self._cr.execute('''
            SELECT move2.id
            FROM account_move move
            JOIN account_journal journal ON journal.id = move.journal_id
            JOIN res_partner partner ON partner.id = move.partner_id
            INNER JOIN account_move move2 ON
                move2.ref = move.ref
                AND move2.company_id = journal.company_id
                AND move2.commercial_partner_id = partner.commercial_partner_id
                AND move2.move_type = move.move_type
                AND (move.invoice_date is NULL OR move2.invoice_date = move.invoice_date)
                AND move2.id != move.id
            WHERE move.id IN %s
        ''', [tuple(moves.ids)])
        duplicated_moves = self.browse([r[0] for r in self._cr.fetchall()])
        if duplicated_moves:
            raise ValidationError(_('Duplicated vendor reference detected. You probably encoded twice the same vendor bill/credit note:\n%s') % "\n".join(
                duplicated_moves.mapped(lambda m: "%(partner)s - %(ref)s - %(date)s" % {
                    'ref': m.ref,
                    'partner': m.partner_id.display_name,
                    'date': format_date(self.env, m.invoice_date),
                })
            ))
    

    def _constrains_date_sequence(self):
        # Make it possible to bypass the constraint to allow edition of already messed up documents.
        # /!\ Do not use this to completely disable the constraint as it will make this mixin unreliable.
        constraint_date = fields.Date.to_date(self.env['ir.config_parameter'].sudo().get_param(
            'sequence.mixin.constraint_start_date',
            '1970-01-01'
        ))
        for record in self:
            date = fields.Date.to_date(record[record._sequence_date_field])
            sequence = record[record._sequence_field]
            if record.contract_type == 'subcontractor':
                return True
            if sequence and date and date > constraint_date:
                format_values = record._get_sequence_format_param(sequence)[1]
                if (
                    format_values['year'] and format_values['year'] != date.year % 10**len(str(format_values['year']))
                    or format_values['month'] and format_values['month'] != date.month
                ):
                    raise ValidationError(_(
                        "The %(date_field)s (%(date)s) doesn't match the %(sequence_field)s (%(sequence)s).\n"
                        "You might want to clear the field %(sequence_field)s before proceeding with the change of the date.",
                        date=format_date(self.env, date),
                        sequence=sequence,
                        date_field=record._fields[record._sequence_date_field]._description_string(self.env),
                        sequence_field=record._fields[record._sequence_field]._description_string(self.env),
                    ))


    def _compute_num2words(self):
        self.amount_words = (num2words(self.amount_total, lang='ar')).upper()

    @api.depends('is_need_approve')
    def check_need_approve(self):
        for rec in self:
            rec.is_need_approve = False
            if not rec.validate_done_approve:
                if self.env.user.has_group('procurment_list_project.group_control_po_validate'):
                    rec.is_need_approve = True
                elif self.env.user.has_group(
                        'procurment_list_project.group_control_po_validate_type_c') and rec.ref == "Contract-Type-C":
                    rec.is_need_approve = True
                elif self.env.user.has_group(
                        'procurment_list_project.group_control_po_validate_type_m') and rec.ref == "Contract-Type-M":
                    rec.is_need_approve = True
                elif self.env.user.has_group(
                        'procurment_list_project.group_control_po_validate_type_e') and rec.ref == "Contract-Type-E":
                    rec.is_need_approve = True

    def action_gm_approve(self):
        for item in self:
            item.write({'state': 'gm_approved'})

    def action_dep_approve(self):
        for inv in self:
            if not inv.lines_updated and inv.contract_type in ['contractor', 'subcontractor']:
                raise exceptions.ValidationError(_("You must update deduction lines first.."))
            inv.write({'validate_done_approve': True, 'state': 'dep_approved'})

    def button_cancel(self):
        self.write({'state': 'cancel', 'validate_done_approve': False})

    @api.depends('all_total_amount_invoices')
    def get_all_total_amount_invoices(self):
        self.all_total_amount_invoices = sum(self.invoice_line_ids.mapped('total_amount'))

    @api.depends('total_amount_invoices_all_cashing_done')
    def get_total_amount_invoices_all_cashing_done(self):
        if self.move_type in ['out_invoice', 'out_refund']:
            self.total_amount_invoices_all_cashing_done = self.all_total_amount_invoices - self.all_cashing_done
        elif self.move_type in ['in_invoice', 'in_refund']:
            self.total_amount_invoices_all_cashing_done = self.all_total_amount_invoices - self.cashing_done
        else:
            self.total_amount_invoices_all_cashing_done = 0.0

    @api.depends('move_type', 'partner_id')
    def get_chashing_done_and_previous_chashing(self):
        for rec in self:
            cashing_done = 0.0
            previous_chashing = 0.0
            all_cashing_done = 0.0
            account_move_line = self.env['account.move.line'].search(
                [('partner_id', '=', rec.partner_id.id), ('move_id.state', '=', 'posted'), '|',
                 ('account_id.internal_type', '=', 'payable'), ('account_id.internal_type', '=', 'receivable'),
                 ('project_contract_id', '=', self.contract_project_id.id)])
            for move_line in account_move_line:
                if rec.move_type in ['out_invoice', 'out_refund']:
                    cashing_done += move_line.credit
                    all_cashing_done += move_line.credit
                    previous_chashing += move_line.debit
                elif rec.move_type in ['in_invoice', 'in_refund']:
                    cashing_done += move_line.debit
                    previous_chashing += move_line.credit
            rec.cashing_done = cashing_done
            rec.previous_chashing = previous_chashing
            rec.all_cashing_done = all_cashing_done

    @api.depends('performance', 'amount_total')
    def get_performance_amount(self):
        for line in self:
            line.performance_amount = 0.0
            if line.total_performance:
                line.performance_amount = line.total_performance
            elif line.performance:
                line.performance_amount = line.amount_total * line.performance / 100

    @api.depends('retation_amount', 'amount_total')
    def get_retation_amount_value(self):
        for rec in self:
            rec.retation_amount_value = 0.0
            if rec.total_retention:
                rec.retation_amount_value = rec.total_retention
            elif rec.retation_amount:
                rec.retation_amount_value = rec.amount_total * rec.retation_amount / 100

    @api.depends('down_payment_percentage', 'amount_total')
    def get_down_payment_fixed(self):
        for line in self:
            line.down_payment_fixed = 0.0
            if line.total_down_payment and not line.final_invoice:
                line.down_payment_fixed = line.total_down_payment
            elif line.total_down_payment and line.final_invoice:
                for invoice_line in line.invoice_line_ids.filtered(lambda x: x.name == 'Down Payment' and x.is_final_downpaymet_line == False):
                    line.down_payment_fixed = invoice_line.price_subtotal
            elif line.down_payment_percentage:
                line.down_payment_fixed = line.amount_total * line.down_payment_percentage / 100


    def action_post(self):
        res = super(AccountMove, self).action_post()
        analytic_lines = self.env['account.analytic.line'].search([('project_id', '=', self.contract_project_id.id)])
        if not analytic_lines:
            if self.contract_project_id and self.contract_project_id.analytic_account_id:
                self.env['account.analytic.line'].create({
                    'name': self.contract_project_id.name + '-' + "Analytic" if self.contract_project_id else '_',
                    'account_id': self.contract_project_id.analytic_account_id.id
                })
        return res
    

    # @api.depends('deduction_ids', 'addition_ids', 'amount_total', 'retation_amount_value', 'down_payment_fixed',
    #              'performance_amount', 'talyat', 'deductions')
    @api.depends('invoice_line_ids', 'deduction_ids', 'addition_ids', 'amount_total', 'retation_amount_value', 'down_payment_fixed',
                 'performance_amount', 'talyat', 'deductions')
    def get_totals(self):
        for line in self:
            line.total_additions = 0.0
            line.total_deductions = 0.0
            for line_invoice in line.invoice_line_ids.filtered(lambda x : x.name=='Addition'):
                line.total_additions += line_invoice.price_subtotal

            for line_invoice in line.invoice_line_ids.filtered(lambda x : x.name=='Deduction'):
                line.total_deductions += line_invoice.price_subtotal
            line.total_with_deduct_addition = line.amount_total


    def get_additions_and_deductions_values(self):
        if not self.deduction_ids:
            deductions_values = [(5, 0, 0)]
            for deduct in self.contract_id.deduction_ids:
                deductions_values.append((0, 0, {
                    'deduction_accounts_id': deduct.deduction_accounts_id.id,
                    'account_id': deduct.account_id.id,
                    'name': deduct.deduction_accounts_id.name,
                    'is_percentage': deduct.is_percentage,
                    'percentage_value': deduct.percentage_value,
                }))
            self.deduction_ids = deductions_values

        if not self.addition_ids:
            additions_values = [(5, 0, 0)]
            for addition in self.contract_id.addition_ids:
                additions_values.append((0, 0, {
                    'deduction_accounts_id': addition.deduction_accounts_id.id,
                    'account_id': addition.account_id.id,
                    'name': addition.deduction_accounts_id.name,
                    'is_percentage': addition.is_percentage,
                    'percentage_value': addition.percentage_value,
                }))

            self.addition_ids = additions_values

    def create_journal_entry_to_deduction(self):
        if self.is_contract_invoice:
            if not self.deduction_journal_id:
                if self.deduction_ids:
                    journal_entry = self.env['account.move']
                    journal_lines = [(5, 0, 0)]
                    for rec2 in self.deduction_ids:
                        journal_lines.append((0, 0, {  # debit --> recivable total -- credit -- details
                            'account_id': rec2.account_id.id,
                            'name': rec2.name,
                            'partner_id': self.partner_id.id,
                            # 'currency_id':rec2.move_id.currency_id.id,
                            'credit': rec2.value if self.contract_type == 'contractor' else 0.0,
                            'debit': rec2.value if self.contract_type == 'subcontractor' else 0.0,
                        }))
                    if not self.contract_type_id.customer_account_id:
                        raise exceptions.ValidationError('You Must Set Customer Account In Contract Type')
                    else:
                        journal_lines.append((0, 0, {
                            'account_id': self.contract_type_id.customer_account_id.id,
                            'name': 'Deduction',
                            'partner_id': self.partner_id.id,
                            # 'currency_id': self.currency_id.id,
                            'debit': sum(
                                self.deduction_ids.mapped('value')) if self.contract_type == 'contractor' else 0.0,
                            'credit': sum(
                                self.deduction_ids.mapped('value')) if self.contract_type == 'subcontractor' else 0.0,
                        }))

                    if journal_lines:
                        deduction_journal = journal_entry.create({
                            'ref': self.name,
                            'date': date.today(),
                            'journal_id': self.journal_id.id,
                            'move_type': 'entry',
                            'line_ids': journal_lines
                        })
                        deduction_journal.action_post()
                        self.deduction_journal_id = deduction_journal.id

    def create_journal_entry_to_addition(self):
        if self.is_contract_invoice:
            if not self.addition_journal_id:
                if self.addition_ids:
                    journal_entry = self.env['account.move']
                    journal_lines = [(5, 0, 0)]
                    for rec in self.addition_ids:
                        journal_lines.append((0, 0, {  # debit --> details -- credit --> total
                            'account_id': rec.account_id.id,
                            'name': rec.name,
                            'partner_id': self.partner_id.id,
                            # 'currency_id':rec.move_id.currency_id.id,
                            'debit': rec.value if self.contract_type == 'contractor' else 0.0,
                            'credit': rec.value if self.contract_type == 'subcontractor' else 0.0,
                        }))

                    if not self.contract_type_id.revenue_account_id:
                        raise exceptions.ValidationError('You Must Set Revenue Account In Contract Type')
                    else:
                        journal_lines.append((0, 0, {
                            'account_id': self.contract_type_id.revenue_account_id.id,
                            'name': 'Addition',
                            'partner_id': self.partner_id.id,
                            # 'currency_id': self.currency_id.id,
                            'credit': sum(
                                self.addition_ids.mapped('value')) if self.contract_type == 'contractor' else 0.0,
                            'debit': sum(
                                self.addition_ids.mapped('value')) if self.contract_type == 'subcontractor' else 0.0,
                        }))

                    if journal_lines:
                        addition_journal = journal_entry.create({
                            'ref': self.name,
                            'date': date.today(),
                            'journal_id': self.journal_id.id,
                            'move_type': 'entry',
                            'line_ids': journal_lines
                        })
                        addition_journal.action_post()
                        self.addition_journal_id = addition_journal.id

    def create_journal_entry_to_down_payment_performance_retention(self):
        if self.is_contract_invoice:
            if self.type != 'entry':
                journal_entry = self.env['account.move']
                journal_lines = [(5, 0, 0)]
                if self.down_payment_account_id:
                    journal_lines.append((0, 0, {  # debit --> details -- credit --> total
                        'account_id': self.down_payment_account_id.counterpart_account_id.id,
                        'name': self.down_payment_account_id.name,
                        'partner_id': self.partner_id.id,
                        # 'currency_id':rec.move_id.currency_id.id,
                        'debit': self.down_payment_fixed if self.contract_type == 'contractor' else 0.0,
                        'credit': self.down_payment_fixed if self.contract_type == 'subcontractor' else 0.0,
                    }))

                if self.performance_account_id:
                    journal_lines.append((0, 0, {  # debit --> details -- credit --> total
                        'account_id': self.performance_account_id.counterpart_account_id.id,
                        'name': self.performance_account_id.name,
                        'partner_id': self.partner_id.id,
                        # 'currency_id':rec.move_id.currency_id.id,
                        'debit': self.performance_amount if self.contract_type == 'contractor' else 0.0,
                        'credit': self.performance_amount if self.contract_type == 'subcontractor' else 0.0,
                    }))

                if self.retention_account_id:
                    journal_lines.append((0, 0, {  # debit --> details -- credit --> total
                        'account_id': self.retention_account_id.counterpart_account_id.id,
                        'name': self.retention_account_id.name,
                        'partner_id': self.partner_id.id,
                        # 'currency_id':rec.move_id.currency_id.id,
                        'debit': self.retation_amount_value if self.contract_type == 'contractor' else 0.0,
                        'credit': self.retation_amount_value if self.contract_type == 'subcontractor' else 0.0,
                    }))
                if self.talyat:
                    if self.talyat_id.account_id:
                        journal_lines.append((0, 0, {  # debit --> details -- credit --> total
                            'account_id': self.talyat_id.account_id.id,
                            'name': self.talyat_id.name,
                            'partner_id': self.partner_id.id,
                            # 'currency_id':rec.move_id.currency_id.id,
                            'debit': self.talyat if self.contract_type == 'contractor' else 0.0,
                            'credit': self.talyat if self.contract_type == 'subcontractor' else 0.0,
                        }))
                    else:
                        raise exceptions.ValidationError('يجب إدخال حساب في قائمة التعليات')
                if self.deductions:
                    if self.deductions_id.account_id:
                        journal_lines.append((0, 0, {  # debit --> details -- credit --> total
                            'account_id': self.deductions_id.account_id.id,
                            'name': self.deductions_id.name,
                            'partner_id': self.partner_id.id,
                            # 'currency_id':rec.move_id.currency_id.id,
                            'debit': self.deductions if self.contract_type == 'contractor' else 0.0,
                            'credit': self.deductions if self.contract_type == 'subcontractor' else 0.0,
                        }))
                    else:
                        raise exceptions.ValidationError('يجب إدخال حساب في قائمة الاستقطاعات')

                if not self.contract_type_id.revenue_account_id:
                    raise exceptions.ValidationError('You Must Set Revenue Account In Contract Type')
                else:
                    journal_lines.append((0, 0, {
                        'account_id': self.contract_type_id.revenue_account_id.id,
                        'name': 'All Down Payment,Performance,Retention',
                        'partner_id': self.partner_id.id,
                        # 'currency_id': self.currency_id.id,
                        'credit': (
                                self.down_payment_fixed + self.performance_amount + self.retation_amount_value + self.talyat + self.deductions) if self.contract_type == 'contractor' else 0.0,
                        'debit': (
                                self.down_payment_fixed + self.performance_amount + self.retation_amount_value + self.talyat + self.deductions) if self.contract_type == 'subcontractor' else 0.0,
                    }))

                if self.down_payment_account_id or self.performance_account_id or self.retention_account_id:
                    if journal_lines:
                        p_d_r_journal = journal_entry.create({
                            'ref': self.name,
                            'date': date.today(),
                            'journal_id': self.journal_id.id,
                            'move_type': 'entry',
                            'line_ids': journal_lines
                        })
                        p_d_r_journal.action_post()
                        self.p_d_r_journal = p_d_r_journal.id

    def _get_computed_account_to_lines(self, product_id):
        self.ensure_one()

        if not product_id:
            return

        fiscal_position = self.fiscal_position_id
        accounts = product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
        if self.is_sale_document(include_receipts=True):
            # Out invoice.
            return accounts['income']
        elif self.is_purchase_document(include_receipts=True):
            # In invoice.
            return accounts['expense']

    def update_deduction_lines(self):
        lines = []
        total_deduction, total_addition, total_performance, total_retation, total_talyat, total_stectaat = 0, 0, 0, 0, 0, 0

        if not self.invoice_final:
            # Deductions
            # if self.deduction_ids and self.contract_type == 'subcontractor':
            #     for record in self.deduction_ids:
            #         # self.total_deductions += (self.amount_total * record.percentage_value / 100)
            #         price = -(self.amount_total * record.percentage_value / 100)
            #         lines.append((0, 0, {
            #             'account_id': record.account_id.id,
            #             'name': "Deduction",
            #             'price_unit': price,
            #             'price_unit2': price,
            #             'current_qty2': 1,
            #             'exclude_from_invoice_tab': False,
            #             'is_deduction': True
            #         }))

            # Additions
            addion_lines = []
            from_contrat_addition = False
            if not self.addition_ids and self.contract_id.addition_ids:
                if self.contract_type == 'contractor':
                    addion_lines = self.contract_id.addition_ids
                    from_contrat_addition = True
                else:
                    addion_lines = []
            else:
                addion_lines = self.addition_ids
            if addion_lines:
                for record in addion_lines:
                    # self.total_additions += self.amount_total * record.percentage_value / 100
                    price = self.amount_total * record.percentage_value / 100
                    tax_ids = False
                    tax_lines = self.invoice_line_ids.filtered(lambda x: x.tax_ids)
                    invoice_lines = tax_lines and tax_lines[0] if tax_lines else False
                    if invoice_lines:
                        tax_ids = invoice_lines.tax_ids.ids
                    else:
                        tax_ids = False
                    lines.append((0, 0, {
                        'account_id': record.account_id.id,
                        'name': "Addition",
                        'price_unit': price,
                        'price_unit2': price,
                        'current_qty2': 1,
                        'exclude_from_invoice_tab': False,
                        'is_deduction': False,
                        'tax_ids':[(6, 0, tax_ids if tax_ids else [])]
                    }))
            
            # Dedudctions

            deduction_lines = []
            from_contrat_deduction = False
            if not self.deduction_ids and self.contract_id.deduction_ids:
                if self.contract_type == 'contractor':
                    deduction_lines = self.contract_id.deduction_ids
                    from_contrat_deduction = True
                else:
                    deduction_lines = []
            else:
                deduction_lines = self.deduction_ids
            if deduction_lines:
                for record in deduction_lines:
                    # self.total_deductions += (self.amount_total * record.percentage_value / 100)
                    price = -(self.amount_total * record.percentage_value / 100)
                    tax_ids = False
                    tax_lines = self.invoice_line_ids.filtered(lambda x: x.tax_ids)
                    invoice_lines = tax_lines and tax_lines[0] if tax_lines else False
                    if invoice_lines:
                        tax_ids = invoice_lines.tax_ids.ids
                    else:
                        tax_ids = False
                    lines.append((0, 0, {
                        'account_id': record.account_id.id,
                        'name': "Deduction",
                        'price_unit': price,
                        'price_unit2': price,
                        'current_qty2': 1,
                        'exclude_from_invoice_tab': False,
                        'is_deduction': True,
                        'tax_ids':[(6, 0, tax_ids if tax_ids else [])]
                    }))

            if from_contrat_addition or from_contrat_deduction:
                self.get_additions_and_deductions_values()

            # Down Payment
            if self.contract_id.down_payment_account_id:
                down_payment = self.amount_total * self.down_payment_percentage / 100
                self.total_down_payment = down_payment * -1
                lines.append((0, 0, {
                    'account_id': self.contract_id.down_payment_account_id.counterpart_account_id.id,
                    'name': "Down Payment",
                    'price_unit': down_payment * -1,
                    'price_unit2': down_payment * -1,
                    'current_qty2': 1,
                    'exclude_from_invoice_tab': False,
                    'is_deduction': True
                }))

            if self.final_invoice:
                invoices = self.env['account.move'].search([('partner_id', '=', self.partner_id.id),
                                                        ('contract_project_id', '=', self.contract_project_id.id),
                                                        ('contract_id', '=', self.contract_id.id),
                                                        ('id', '!=', self.id), ('state', '=', 'posted')])
                down_payment_value = 0
                if invoices:
                    down_payment = 0
                    down_payment_current = 0
                    down_payment_value = 0
                    for invoice in invoices:
                        for line in invoice.invoice_line_ids.filtered(lambda x: x.name == 'Down Payment'):
                            down_payment += line.price_unit
                    if self.contract_id.down_payment_account_id:
                        down_payment_current = self.amount_total * self.down_payment_percentage / 100
                    if down_payment:
                        down_payment_fixed_contract = self.contract_id.down_payment_fixed
                        if down_payment_fixed_contract:
                            down_payment_value = (down_payment_fixed_contract + down_payment - down_payment_current) * -1
                        else:
                            down_payment_value = down_payment - down_payment_current
                    else:
                        down_payment_value = (self.contract_id.down_payment_fixed - down_payment_current ) * -1
                    self.total_down_payment = down_payment_value - down_payment_current
                    lines.append((0, 0, {
                        'account_id': self.contract_id.down_payment_account_id.counterpart_account_id.id,
                        'name': "Down Payment",
                        'price_unit': down_payment_value,
                        'price_unit2': down_payment_value,
                        'current_qty2': 1,
                        'exclude_from_invoice_tab': False,
                        'is_deduction': True,
                        'is_final_downpaymet_line': True,
                    }))

            # Performance
            if self.contract_id.performance_account_id:
                performance = self.amount_total * self.performance / 100
                self.total_performance = performance * -1
                lines.append((0, 0, {
                    'account_id': self.contract_id.performance_account_id.counterpart_account_id.id,
                    'name': "Performance Bond",
                    'price_unit': -performance,
                    'price_unit2': -performance,
                    'current_qty2': 1,
                    'exclude_from_invoice_tab': False,
                    'is_deduction': True
                }))

            # Retention
            if self.contract_id.retention_account_id:
                retention = self.amount_total * self.retation_amount / 100
                self.total_retention = retention * -1
                lines.append((0, 0, {
                    'account_id': self.contract_id.retention_account_id.counterpart_account_id.id,
                    'name': "Retention",
                    'price_unit': -retention,
                    'price_unit2': -retention,
                    'current_qty2': 1,
                    'exclude_from_invoice_tab': False,
                    'is_deduction': True
                }))

            # تـعـليـات
            if self.talyat and self.contract_type == 'contractor' or 'subcontractor':
                self.talyat_id = self.env['talyat.talyat'].search([], limit=1)
                lines.append((0, 0, {
                    'account_id': self.talyat_id.account_id.id,
                    'name': "تـعـلـيـات",
                    'price_unit': -self.talyat if not self.invoice_final else self.talyat,
                    'price_unit2': -self.talyat if not self.invoice_final else self.talyat,
                    'current_qty2': 1,
                    'exclude_from_invoice_tab': False,
                    'is_deduction': True if not self.invoice_final else False
                }))

            # اسـتـقـطـاعات
            if self.deductions and self.contract_type == 'subcontractor' or 'contractor':
                self.deductions_id = self.env['deduct.deduct'].search([], limit=1)
                lines.append((0, 0, {
                    'account_id': self.deductions_id.account_id.id,
                    'name': "أسـتـقـطاعـات",
                    'price_unit': -self.deductions if not self.invoice_final else self.deductions,
                    'price_unit2': -self.deductions if not self.invoice_final else self.deductions,
                    'current_qty2': 1,
                    'exclude_from_invoice_tab': False,
                    'is_deduction': True if not self.invoice_final else False
                }))

        else:
            invoices = self.env['account.move'].search([('partner_id', '=', self.partner_id.id),
                                                        ('contract_project_id', '=', self.contract_project_id.id),
                                                        ('contract_id', '=', self.contract_id.id),
                                                        ('id', '!=', self.id), ('state', '!=', 'cancel')])
            for line in invoices:
                total_deduction += line.total_deductions
                total_addition += line.total_additions
                total_performance += abs(line.performance_amount)
                total_retation += abs(line.retation_amount_value)
                total_talyat += abs(line.talyat)
                total_stectaat += abs(line.deductions)

            if total_deduction and self.contract_type == 'subcontractor':
                deduction_account = self.env['deduction.accounts'].search([('deduction_type', '=', 'deduction')],
                                                                          limit=1)
                lines.append((0, 0, {
                    'account_id': deduction_account.counterpart_account_id.id,
                    'name': "Deduction",
                    'price_unit': total_deduction,
                    'price_unit2': total_deduction,
                    'current_qty2': 1,
                    'exclude_from_invoice_tab': False,
                }))

            if total_addition and self.contract_type == 'contractor':
                addition_account = self.env['deduction.accounts'].search([('deduction_type', '=', 'addition')],
                                                                         limit=1)
                lines.append((0, 0, {
                    'account_id': addition_account.counterpart_account_id.id,
                    'name': "Addition",
                    'price_unit': total_addition,
                    'price_unit2': total_addition,
                    'current_qty2': 1,
                    'exclude_from_invoice_tab': False,
                }))

            if total_performance:
                lines.append((0, 0, {
                    'account_id': self.contract_id.performance_account_id.counterpart_account_id.id,
                    'name': "Performance Bond",
                    'price_unit': total_performance,
                    'price_unit2': total_performance,
                    'current_qty2': 1,
                    'exclude_from_invoice_tab': False,
                }))

            if total_retation:
                lines.append((0, 0, {
                    'account_id': self.contract_id.retention_account_id.counterpart_account_id.id,
                    'name': "Retention",
                    'price_unit': total_retation,
                    'price_unit2': total_retation,
                    'current_qty2': 1,
                    'exclude_from_invoice_tab': False,
                }))

            # تـعـليـات
            if total_talyat and self.contract_type == 'contractor':
                self.talyat_id = self.env['talyat.talyat'].search([], limit=1)
                lines.append((0, 0, {
                    'account_id': self.talyat_id.account_id.id,
                    'name': "تـعـلـيـات",
                    'price_unit': total_talyat,
                    'price_unit2': total_talyat,
                    'current_qty2': 1,
                    'exclude_from_invoice_tab': False,
                    'is_deduction': True if not self.invoice_final else False
                }))

            # اسـتـقـطـاعات
            if total_stectaat and self.contract_type == 'subcontractor':
                self.deductions_id = self.env['deduct.deduct'].search([], limit=1)
                lines.append((0, 0, {
                    'account_id': self.deductions_id.account_id.id,
                    'name': "أسـتـقـطاعـات",
                    'price_unit': total_stectaat,
                    'price_unit2': total_stectaat,
                    'current_qty2': 1,
                    'exclude_from_invoice_tab': False,
                    'is_deduction': True if not self.invoice_final else False
                }))
        self.invoice_line_ids = lines
        self.lines_updated = True

    @api.onchange('contract_id')
    def get_contract_data(self):
        if self.is_contract_invoice:
            lines = []

            self.write({
                'down_payment_percentage': self.contract_id.down_payment_percentage,
                'down_payment_account_id': self.contract_id.down_payment_account_id.id,
                'performance': self.contract_id.performance,
                'performance_account_id': self.contract_id.performance_account_id.id,
                'retation_amount': self.contract_id.retation_amount,
                'retention_account_id': self.contract_id.retention_account_id.id,
                'contract_project_id': self.contract_id.project_id.id,
                'invoice_payment_term_id': self.contract_id.payment_term_id.id,
                'contract_type_id': self.contract_id.contract_id.id,
                'project_id': self.contract_project_id.analytic_account_id.id,
                'contract_quotation_id': self.contract_id.quotation_number_id.id,
                'partner_id': self.contract_id.customer_id.id if self.contract_id.type == 'contractor' else self.contract_id.subcontractor_id.id
            })

            self.get_additions_and_deductions_values()

            for rec in self.contract_id.contract_line_ids:
                job_cost = self.env['job.costing'].search([('name', '=', rec.product_id.name)], limit=1)
                lines.append((0, 0, {
                    'product_id': rec.product_id.id,
                    'account_id': self.contract_id.revenue_account_id.id,
                    # self._get_computed_account_to_lines(rec.product_id)
                    'name': rec.work_plan_item_id.name if rec.work_plan_item_id else rec.product_id.name,
                    'work_plan_item_id': rec.work_plan_item_id.id if rec.work_plan_item_id else False,
                    'price_unit': rec.price_unit,
                    'price_unit2': rec.price_unit,
                    'total_qty': rec.total_work_plan_qty,
                    'product_uom_id': rec.product_uom_id.id,
                    'exclude_from_invoice_tab': False,
                    'tax_ids': rec.tax_id.ids,
                    'analytic_account_id': self.contract_project_id.analytic_account_id.id,
                    'job_cost_id': job_cost.id
                }))
            self._onchange_partner_id()

            if not self.invoice_final:
                self.invoice_line_ids = lines

            for line in self.invoice_line_ids:
                # line._onchange_price_subtotal()
                line.get_original_quantity()
                # line.calculate_total_qty()
                line.calculate_previous_qty()
                line.onchange_completed_percentage_view()
            self._onchange_invoice_line_ids()

    @api.depends('partner_id', 'is_contract_invoice', 'contract_id')
    def get_contract_products(self):
        self.contract_products_ids = False

    @api.onchange('contract_project_id', 'partner_id', 'is_contract_invoice', 'contract_type_id', 'contract_type')
    def filter_contract(self):
        return {
            'domain':
                {
                    'contract_id': [
                        ('id', 'in', self.env['owner.contract'].search([('type', '=', self.contract_type)]).ids),
                        ('state', '=', 'confirmed'), ('project_id', '=', self.contract_project_id.id)]
                }
        }

    @api.onchange('contract_project_id', 'is_contract_invoice', 'contract_type_id', 'contract_type')
    def filter_project(self):
        projects = []
        for rec in self.env['owner.contract'].search([('type', '=', self.contract_type)]):
            projects.append(rec.project_id.id)
        return {
            'domain':
                {
                    'contract_project_id': [('id', 'in', projects)]
                }
        }

    @api.onchange('contract_project_id')
    def get_partner(self):
        self.partner_id = self.contract_project_id.partner_id.id

    @api.depends('prev_contract_invoices', 'contract_id', 'partner_id', 'is_contract_invoice', 'contract_type')
    def get_prev_contract_invoices(self):
        self.prev_contract_invoices = self.env['account.move'].search_count(
            [('contract_id', '=', self.contract_id.id), ('move_type', '=', 'out_invoice'),
             ('is_contract_invoice', '=', True), ('contract_type', '=', self.contract_type),
             ('partner_id', '=', self.partner_id.id), ('id', '!=', self._origin.id), ('id', '<', self._origin.id)])

    def open_related_invoices_contract(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'name': 'Contract Invoices',
            'target': 'current',
            'domain': [('contract_id', '=', self.contract_id.id), ('move_type', '=', 'out_invoice'),
                       ('is_contract_invoice', '=', True), ('contract_type', '=', self.contract_type),
                       ('partner_id', '=', self.partner_id.id), ('id', '!=', self._origin.id),
                       ('id', '<', self._origin.id)],
            'context': {'default_move_type': 'out_invoice', 'default_contract_type': self.contract_type,
                        'default_contract_project_id': self.contract_project_id.id, 'default_is_contract_invoice': True,
                        'default_contract_type_id': self.contract_type_id.id,
                        'default_contract_id': self.contract_id.id},

        }

    @api.depends('prev_contract_bills', 'contract_id', 'partner_id', 'is_contract_invoice', 'contract_type')
    def get_prev_contract_bills(self):
        self.prev_contract_bills = self.env['account.move'].search_count(
            [('contract_id', '=', self.contract_id.id), ('move_type', '=', 'in_invoice'),
             ('is_contract_invoice', '=', True),
             ('contract_type', '=', self.contract_type), ('partner_id', '=', self.partner_id.id),
             ('id', '!=', self._origin.id),
             ('id', '<', self._origin.id)])

    def open_related_bills_contract(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'name': 'Contract Invoices',
            'target': 'current',
            'domain': [('contract_id', '=', self.contract_id.id), ('move_type', '=', 'in_invoice'),
                       ('is_contract_invoice', '=', True),
                       ('contract_type', '=', self.contract_type), ('partner_id', '=', self.partner_id.id),
                       ('id', '!=', self._origin.id), ('id', '<', self._origin.id)],
            'context': {'default_move_type': 'in_invoice', 'default_contract_type': self.contract_type,
                        'default_contract_project_id': self.contract_project_id.id, 'default_is_contract_invoice': True,
                        'default_contract_type_id': self.contract_type_id.id,
                        'default_contract_id': self.contract_id.id},

        }


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    completed_percentage_view = fields.Float('% Completed View', )
    price_unit2 = fields.Float(string='Price', digits='Product Price')

    project_contract_id = fields.Many2one(comodel_name="project.project", string="Project",
                                          compute='get_contract_project', store=True, required=False, )
    is_deduction = fields.Boolean(string='Is Deduction')
    is_final_downpaymet_line = fields.Boolean('Is final downpayment Line', default=False)
    work_plan_item_id = fields.Many2one('work.plan.items.line', string='Work Plan Item')


    @api.depends('product_id', 'quantity', 'move_id', 'move_id.invoice_line_ids')
    def get_contract_project(self):
        for rec in self:
            if rec.move_id.contract_project_id:
                rec.project_contract_id = rec.move_id.contract_project_id.id
            else:
                rec.project_contract_id = False

    
    @api.onchange('completed_percentage_view', 'current_qty2', 'price_unit2')
    def onchange_completed_percentage_view(self):
        for line in self:
            if line.completed_percentage_view:
                line.price_unit = line.price_unit2
                line.price_unit2 = line.price_unit2
                line.total_amount = line.price_unit2 * line.current_qty2 *(line.completed_percentage_view / 100)
                line.price_subtotal = line.total_amount
            else:
                line.price_unit2 = line.price_unit2
                line.price_unit = line.price_unit2
                line.total_amount = line.current_qty2 * line.price_unit2
                line.price_subtotal = line.total_amount


    # @api.onchange('product_id')
    # def product_id_onchange_test(self):
    #     for item in self:
    #         if item.product_id:
    #             item.price_unit2 = item.product_id.lst_price

    @api.onchange('quantity', 'discount', 'price_unit', 'tax_ids', 'price_unit2', 'completed_percentage_view', 'current_qty2')
    def _onchange_price_subtotal(self):
        for line in self:
            if not line.move_id.is_invoice(include_receipts=True):
                continue
            line.update(line._get_price_total_and_subtotal())
            line.update(line._get_fields_onchange_subtotal())

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        # raise Warning('create',vals_list)
        ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
        BUSINESS_FIELDS = (
            'price_unit', 'price_unit', 'quantity', 'discount', 'tax_ids', 'completed_percentage_view', 'price_unit2', 'current_qty2')

        for vals in vals_list:
            move = self.env['account.move'].browse(vals['move_id'])
            vals.setdefault('company_currency_id',
                            move.company_id.currency_id.id)  # important to bypass the ORM limitation where monetary fields are not rounded; more info in the commit message

            currency_id = vals.get('currency_id') or move.company_id.currency_id.id
            if currency_id == move.company_id.currency_id.id:
                balance = vals.get('debit', 0.0) - vals.get('credit', 0.0)
                vals.update({
                    'currency_id': currency_id,
                    'amount_currency': balance,
                })
            else:
                vals['amount_currency'] = vals.get('amount_currency', 0.0)

            if move.is_invoice(include_receipts=True):
                currency = move.currency_id
                partner = self.env['res.partner'].browse(vals.get('partner_id'))
                taxes = self.new({'tax_ids': vals.get('tax_ids', [])}).tax_ids
                tax_ids = set(taxes.ids)
                taxes = self.env['account.tax'].browse(tax_ids)

                # Ensure consistency between accounting & business fields.
                # As we can't express such synchronization as computed fields without cycling, we need to do it both
                # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
                # business [resp. accounting] fields are recomputed.
                if any(vals.get(field) for field in ACCOUNTING_FIELDS):
                    if vals.get('currency_id'):
                        balance = vals.get('amount_currency', 0.0)
                    else:
                        balance = vals.get('debit', 0.0) - vals.get('credit', 0.0)

                    price_subtotal = self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                        vals.get('completed_percentage_view', 0.0),
                        vals.get('price_unit2', 0.0),
                        vals.get('current_qty2', 0.0),

                    ).get('price_subtotal', 0.0)
                    vals.update(self._get_fields_onchange_balance_model(
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        balance,
                        move.move_type,
                        currency,
                        taxes,
                        price_subtotal,
                    ))
                    vals.update(self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                        vals.get('completed_percentage_view', 0.0),
                        vals.get('price_unit2', 0.0),
                        vals.get('current_qty2', 0.0),

                    ))
                elif any(vals.get(field) for field in BUSINESS_FIELDS):
                    vals.update(self._get_price_total_and_subtotal_model(
                        vals.get('price_unit', 0.0),
                        vals.get('quantity', 0.0),
                        vals.get('discount', 0.0),
                        currency,
                        self.env['product.product'].browse(vals.get('product_id')),
                        partner,
                        taxes,
                        move.move_type,
                        vals.get('completed_percentage_view', 0.0),
                        vals.get('price_unit2', 0.0),
                        vals.get('current_qty2', 0.0),
                    ))
                    vals.update(self._get_fields_onchange_subtotal_model(
                        vals['price_subtotal'],
                        move.move_type,
                        currency,
                        move.company_id,
                        move.date,
                    ))

            # Ensure consistency between taxes & tax exigibility fields.
            if 'tax_exigible' in vals:
                continue
            if vals.get('tax_repartition_line_id'):
                repartition_line = self.env['account.tax.repartition.line'].browse(vals['tax_repartition_line_id'])
                tax = repartition_line.invoice_tax_id or repartition_line.refund_tax_id
                vals['tax_exigible'] = tax.tax_exigibility == 'on_invoice'
            elif vals.get('tax_ids'):
                taxes = self.new({'tax_ids': vals.get('tax_ids', [])}).tax_ids
                tax_ids = set(taxes.ids)
                taxes = self.env['account.tax'].browse(tax_ids)
                # taxes = self._get_computed_taxes()
                vals['tax_exigible'] = not any([tax['tax_exigibility'] == 'on_payment' for tax in taxes])

        lines = super(models.Model, self).create(vals_list)
        # raise Warning(vals_list)

        moves = lines.mapped('move_id')
        if self._context.get('check_move_validity', True):
            moves._check_balanced()
        moves._check_fiscalyear_lock_date()
        lines._check_tax_lock_date()

        return lines

    def _get_fields_onchange_balance(self, quantity=None, discount=None, amount_currency=None, move_type=None,
                                     currency=None, taxes=None, price_subtotal=None, force_computation=False,
                                     ):
        self.ensure_one()
        return self._get_fields_onchange_balance_model(
            quantity=quantity or self.quantity,
            discount=discount or self.discount,
            amount_currency=amount_currency or self.amount_currency,
            move_type=move_type or self.move_id.move_type,
            currency=currency or self.currency_id or self.move_id.currency_id,
            taxes=taxes or self.tax_ids,
            price_subtotal=price_subtotal or self.price_subtotal,
            force_computation=force_computation
            

        )

    @api.model
    def _get_fields_onchange_balance_model(self, quantity, discount, amount_currency, move_type, currency, taxes,
                                           price_subtotal, force_computation=False):
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1
        amount_currency *= sign

        if not force_computation and currency.is_zero(amount_currency - price_subtotal):
            return {}

        taxes = taxes.flatten_taxes_hierarchy()
        if taxes and any(tax.price_include for tax in taxes):
            force_sign = -1 if move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
            taxes_res = taxes._origin.with_context(force_sign=force_sign).compute_all(amount_currency,
                                                                                      currency=currency,
                                                                                      handle_price_include=False)
            for tax_res in taxes_res['taxes']:
                tax = self.env['account.tax'].browse(tax_res['id'])
                if tax.price_include:
                    amount_currency += tax_res['amount']
        discount_factor = 1 - (discount / 100.0)
        if amount_currency and discount_factor:
            # discount != 100%
            vals = {
                'quantity': quantity or 1.0,
                'price_unit': amount_currency / discount_factor / (quantity or 1.0),
                'price_unit2' :self.price_unit2,
                'current_qty2': self.current_qty2,
                'previous_qty': self.previous_qty,
                'actual_quant': self.actual_quant,
                'completed_percentage_view': self.completed_percentage_view,
                'work_plan_item_id': self.work_plan_item_id.id if self.work_plan_item_id else False,
            }
        elif amount_currency and not discount_factor:
            # discount == 100%
            vals = {
                'quantity': quantity or 1.0,
                'discount': 0.0,
                'price_unit': amount_currency / (quantity or 1.0),
                'price_unit2' : self.price_unit2,
                'current_qty2': self.current_qty2,
                'previous_qty': self.previous_qty,
                'actual_quant': self.previous_qty,
                'completed_percentage_view': self.completed_percentage_view,
                'work_plan_item_id': self.work_plan_item_id.id if self.work_plan_item_id else False,
            }
        elif not discount_factor:
            # balance of line is 0, but discount  == 100% so we display the normal unit_price
            vals = {}
        else:
            # balance is 0, so unit price is 0 as well
            vals = {'price_unit': 0.0}
        return vals

    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None,
                                      partner=None, taxes=None, move_type=None, completed_percentage_view=None,
                                      price_unit2=None,current_qty2=None):
        self.ensure_one()
        return self._get_price_total_and_subtotal_model(
            price_unit=price_unit or self.price_unit,
            quantity=quantity or self.quantity,
            discount=discount or self.discount,
            currency=currency or self.currency_id,
            product=product or self.product_id,
            partner=partner or self.partner_id,
            taxes=taxes or self.tax_ids,
            move_type=move_type or self.move_id.move_type,
            completed_percentage_view=completed_percentage_view or self.completed_percentage_view,
            price_unit2=price_unit2 or self.price_unit2,
            current_qty2=current_qty2 or self.current_qty2
        )

    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes,
                                            move_type, completed_percentage_view, price_unit2,current_qty2):
        res = {}


        # Compute 'price_subtotal'.
        
        price_unit_wo_discount = price_unit2 * (1 - (discount / 100.0))
        if completed_percentage_view != 0:
            price_unit_wo_discount = price_unit_wo_discount * (completed_percentage_view/100)
        else:
            price_unit_wo_discount = price_unit_wo_discount
        
        subtotal = current_qty2 * price_unit_wo_discount

        # Compute 'price_total'.
        if taxes:
            taxes_res = taxes._origin.compute_all(price_unit_wo_discount,
                                                  quantity=current_qty2, currency=currency, product=product,
                                                  partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
            res['price_unit'] = price_unit
            res['price_unit2'] = price_unit2
            res['completed_percentage_view'] = completed_percentage_view
            res['current_qty2'] = current_qty2
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
            res['price_unit'] = price_unit
            res['price_unit2'] = price_unit2
            res['completed_percentage_view'] = completed_percentage_view
            res['current_qty2'] = current_qty2

        # In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res

    update_product = fields.Boolean(string="Update Products", )

    @api.onchange('product_id')
    def get_product_data(self):
        for rec in self:
            if rec.move_id.is_contract_invoice:
                for line in rec.move_id.contract_id.contract_line_ids:
                    if rec.product_id.id == line.product_id.id:
                        rec.price_unit = line.price_unit
                        rec.total_contract_qty = line.quantity
                        rec.product_uom_id = line.product_uom_id.id
                        rec.price_unit2 = line.price_unit
            else:
                rec.price_unit2 = rec.product_id.lst_price

    @api.onchange('update_product', 'quantity')
    def get_products_from_contract(self):
        for rec in self:
            products = []
            for res in rec.move_id.contract_id.contract_line_ids:
                products.append(res.product_id.id)
            if rec.move_id.is_contract_invoice:
                return {'domain': {'product_id': [('id', 'in', products)]}}

    def _get_computed_taxes(self):
        self.ensure_one()

        if not self.move_id.is_contract_invoice:
            return super(AccountMoveLine, self)._get_computed_taxes()
        else:
            return False


class InvoiceDeduction(models.Model):
    _name = 'invoice.deduction'

    deduction_accounts_id = fields.Many2one(comodel_name="deduction.accounts",
                                            domain=[('deduction_type', '=', 'deduction')], string="Deduction",
                                            required=False, )
    account_id = fields.Many2one(comodel_name="account.account", string="Account", required=False, )
    name = fields.Char(string="Name", required=False, )
    is_percentage = fields.Boolean(string="Is Percentage")
    percentage_value = fields.Float(string="Percentage/Value", required=False, )
    value = fields.Float(string="Value", required=False, compute="get_value")  #

    move_id = fields.Many2one(comodel_name="account.move", string="", required=False, )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue

            line.name = line._get_computed_name()
            line.account_id = line._get_computed_account()
            line.tax_ids = line._get_computed_taxes()
            if not line.move_id.contract_id:
                line.product_uom_id = line._get_computed_uom()
            if not line.move_id.contract_id:
                line.price_unit = 1

        if len(self) == 1:
            return {'domain': {'product_uom_id': [('category_id', '=', self.product_uom_id.category_id.id)]}}

    @api.onchange('deduction_accounts_id')
    def get_account(self):
        for rec in self:
            rec.account_id = rec.deduction_accounts_id.counterpart_account_id.id
            rec.is_percentage = rec.deduction_accounts_id.is_percentage

    @api.depends('deduction_accounts_id', 'move_id.amount_total', 'percentage_value', 'move_id.total_deductions')
    def get_value(self):
        for rec in self:
            rec.value = 0.0
            if rec.percentage_value:
                if self.move_id.total_deductions:
                    if rec.is_percentage:
                        percentage_total = 0
                        for deduction in self.move_id.deduction_ids:
                            percentage_total+= deduction.percentage_value
                        rec.value = (self.move_id.total_deductions/percentage_total) * rec.percentage_value * (-1)
                    else:
                        rec.value = rec.percentage_value
                    # rec.value = self.move_id.total_deductions
                elif rec.is_percentage:
                    rec.value = rec.move_id.amount_total * rec.percentage_value / 100
                else:
                    rec.value = rec.percentage_value


class InvoiceAddition(models.Model):
    _name = 'invoice.addition'

    deduction_accounts_id = fields.Many2one(comodel_name="deduction.accounts",
                                            domain=[('deduction_type', '=', 'addition')], string="Addition",
                                            required=False, )
    account_id = fields.Many2one(comodel_name="account.account", string="Account", required=False, )
    name = fields.Char(string="Name", required=False, )
    is_percentage = fields.Boolean(string="Is Percentage")
    percentage_value = fields.Float(string="Percentage/Value", required=False, )
    value = fields.Float(string="Value", required=False, compute="get_value")

    move_id = fields.Many2one(comodel_name="account.move", string="", required=False, )

    @api.onchange('deduction_accounts_id')
    def get_account(self):
        for rec in self:
            rec.account_id = rec.deduction_accounts_id.counterpart_account_id.id
            rec.is_percentage = rec.deduction_accounts_id.is_percentage

    @api.depends('deduction_accounts_id', 'move_id.amount_total', 'percentage_value', 'move_id.total_additions')
    def get_value(self):
        for rec in self:
            rec.value = 0.0
            if rec.percentage_value:
                if self.move_id.total_additions:
                    if rec.is_percentage:
                        percentage_total = 0
                        for addition in self.move_id.addition_ids:
                            percentage_total+= addition.percentage_value
                        rec.value = (self.move_id.total_additions/percentage_total) * rec.percentage_value
                    else:
                        rec.value = rec.percentage_value
                    # rec.value = self.move_id.total_additions
                elif rec.is_percentage:
                    rec.value = rec.move_id.amount_total * rec.percentage_value / 100
                else:
                    rec.value = rec.percentage_value


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('account_id'):
                project_id = self.env['project.project'].search([('analytic_account_id', '=', vals.get('account_id'))], limit=1)
                vals['project_id'] = project_id and project_id.id

        result = super(AccountAnalyticLine, self).create(vals_list)
        return result