# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta


class OwnerContract(models.Model):
    _name = 'owner.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'description'

    name = fields.Char(string="Seq", required=False, )
    description = fields.Char(string="Name", required=False, )
    project_id = fields.Many2one(comodel_name="project.project", string="Project Name", required=False, )
    customer_id = fields.Many2one(comodel_name="res.partner", string="Customer", compute='get_data_from_project',
                                  store=True, required=False, )
    subcontractor_id = fields.Many2one(comodel_name="res.partner", string="Subcontractor",
                                       domain=[('supplier_rank', '!=', 0)], required=False, )
    date = fields.Date(string="Date", required=False, default=fields.Date.context_today)

    contract_id = fields.Many2one(comodel_name="contracts", string="Contract", required=False, )  # Make New Model
    customer_account_id = fields.Many2one(comodel_name="account.account", string="Customer Account", required=False, )
    revenue_account_id = fields.Many2one(comodel_name="account.account", string="Revenue Account", required=False, )

    site_receive_date = fields.Date(string="Site Receive Date", required=False, default=fields.Date.context_today)
    project_end_date = fields.Date(string="Project End Date", required=False, )
    difference_days = fields.Float(string="Duration", required=False, related='project_id.project_period')
    ref = fields.Char(string="Reference", required=False, )
    quotation_number_id = fields.Many2one(comodel_name="sale.order", string="Quotation Number", required=False, )

    contract_line_ids = fields.One2many(comodel_name="owner.contract.line", inverse_name="owner_contract_id", string="",
                                        required=False, )
    deduction_ids = fields.One2many(comodel_name="owner.contract.deduction", inverse_name="owner_cont_id", string="",
                                    required=False, )
    addition_ids = fields.One2many(comodel_name="owner.contract.addition", inverse_name="owner_cont_id", string="",
                                   required=False, )

    type = fields.Selection(string="Contractor Type",
                            selection=[('contractor', 'Contractor'), ('subcontractor', 'Subcontractor'), ],
                            required=False, )

    contract_value = fields.Float(string="Contract Value", compute='get_contract_value', store=True, required=False, )
    owner_contractor_invoice_count = fields.Integer(string="", required=False,
                                                    compute="get_owner_contractor_invoice_count")
    sub_contractor_invoice_count = fields.Integer(string="", required=False,
                                                  compute="get_owner_contractor_invoice_count")

    contract_language = fields.Selection(string="Contract Language",
                                         selection=[('arabic', 'Arabic'), ('english', 'English'),
                                                    ('bilingual', 'Bilingual')], required=False, )
    contract_type = fields.Selection(string="Contract Type",
                                     selection=[('lamsum', 'Lumpsum'), ('unit_price', 'Unit Price'), ],
                                     required=False, )
    payment_method_id = fields.Many2one(comodel_name="account.payment.method", string="Payment Method",
                                        required=False, )
    contract_condition = fields.Selection(string="Contract Condition",
                                          selection=[('at_hack', 'Ad-Hock'), ('fidic', 'Fidic'), ], required=False, )
    insurance_form = fields.Char(string="Insurance", required=False, )

    payment_term_id = fields.Many2one(comodel_name="account.payment.term", string="Payment Term", required=False, )

    tax_id = fields.Many2one(comodel_name="account.tax", domain=[('is_contract_tax', '=', True)], string="Taxes",
                             required=False, )
    subcontractor_type = fields.Selection(string="", selection=[('civil', 'Civil'), ('electricity', 'Electricity'),
                                                                ('mechanics', 'Mechanics'), ], )
    work_plan_id = fields.Many2one(comodel_name="work.plan", string="Work Plan", compute='get_work_plan', store=True,
                                   required=False, )
    constrained_by_ids = fields.Many2many(comodel_name="constrained.by", string="Constrained By", )

    down_payment_fixed = fields.Float(string="Down Payment Fixed", required=False, )
    down_payment_percentage = fields.Float(string="Down Payment(%)", required=False, )
    performance = fields.Float(string="Performance bond (%)", required=False, )
    performance_amount = fields.Float(string="Performance Amount", required=False, )
    retation_amount = fields.Float(string="Retention (%)", required=False, )
    retation_amount_value = fields.Float(string="Retention Amount", required=False, )
    down_payment_account_id = fields.Many2one(comodel_name="deduction.accounts", string="Down Payment Type",
                                              domain=[('deduction_type', '=', 'down_payment')], required=False, )
    performance_account_id = fields.Many2one(comodel_name="deduction.accounts", string="Performance Type",
                                             domain=[('deduction_type', '=', 'performance_bond')], required=False, )
    retention_account_id = fields.Many2one(comodel_name="deduction.accounts", string="Retention Type",
                                           domain=[('deduction_type', '=', 'retention')], required=False, )
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], default='draft', string='State')
    down_payment_journal_id = fields.Many2one(comodel_name="account.move", string="Down Payment Journal",
                                              required=False, )

    def action_confirm(self):
        if self.down_payment_account_id:
            if not self.down_payment_journal_id:
                # down_payment_tax_amount = self.down_payment_fixed * self.tax_id.amount / 100

                journal_entry = self.env['account.move']
                journal_lines = [(5, 0, 0)]
                journal_lines.append((0, 0, {  # credit --> recivable total -- debit -- details
                    'account_id': self.down_payment_account_id.counterpart_account_id.id,
                    'name': self.down_payment_account_id.name,
                    'partner_id': self.customer_id.id if self.type == 'contractor' else self.subcontractor_id.id,
                    # 'currency_id':rec2.move_id.currency_id.id,
                    'credit': self.down_payment_fixed if self.type == 'contractor' else 0.0,
                    'debit': self.down_payment_fixed if self.type == 'subcontractor' else 0.0,
                }))
                # if self.tax_id.down_payment_tax_account_id:
                #     journal_lines.append((0, 0, {  # credit --> recivable total -- debit -- details
                #         'account_id': self.tax_id.down_payment_tax_account_id.id,
                #         'name': 'Down Payment Taxes',
                #         'partner_id': self.customer_id.id,
                #         # 'currency_id':rec2.move_id.currency_id.id,
                #         'credit': down_payment_tax_amount if self.type == 'contractor' else 0.0,
                #         'debit': down_payment_tax_amount  if self.type == 'subcontractor' else 0.0,
                #     }))
                # else:
                #     raise exceptions.ValidationError('You Must Set Down Payment Account In Taxes')
                if not self.down_payment_account_id.down_payment_account_id:
                    raise exceptions.ValidationError('You Must Set Down Payment Account In Down Payment type')
                else:
                    journal_lines.append((0, 0, {
                        'account_id': self.down_payment_account_id.down_payment_account_id.id,
                        'name': 'إستحقاق دفعه مقدمه',
                        'partner_id': self.customer_id.id if self.type == 'contractor' else self.subcontractor_id.id,
                        # 'currency_id': self.currency_id.id,
                        'debit': self.down_payment_fixed if self.type == 'contractor' else 0.0,
                        'credit': self.down_payment_fixed if self.type == 'subcontractor' else 0.0,
                    }))

                if journal_lines:
                    if self.down_payment_account_id.journal_id:
                        down_payment_journal = journal_entry.create({
                            'ref': self.name,
                            'date': date.today(),
                            'journal_id': self.down_payment_account_id.journal_id.id,
                            'move_type': 'entry',
                            'line_ids': journal_lines
                        })
                        down_payment_journal.action_post()
                        self.down_payment_journal_id = down_payment_journal.id
                    else:
                        raise exceptions.ValidationError('You Must Set Journal In Down Payment type')

        self.state = 'confirmed'

    @api.onchange('performance', 'contract_value')
    def get_performance_amount(self):
        if self.performance:
            self.performance_amount = self.contract_value * self.performance / 100

    @api.onchange('performance_amount')
    def get_performance(self):
        if self.performance_amount and self.quotation_number_id.amount_total != 0:
            self.performance = self.performance_amount * 100 / self.contract_value

    @api.onchange('retation_amount', 'contract_value')
    def get_retation_amount_value(self):
        if self.retation_amount:
            self.retation_amount_value = self.contract_value * self.retation_amount / 100

    @api.onchange('retation_amount_value')
    def get_retation_amount(self):
        if self.retation_amount_value and self.quotation_number_id.amount_total != 0:
            self.retation_amount = self.retation_amount_value * 100 / self.contract_value

    @api.onchange('down_payment_percentage', 'contract_value')
    def get_down_payment_fixed(self):
        if self.down_payment_percentage:
            self.down_payment_fixed = self.contract_value * self.down_payment_percentage / 100

    @api.onchange('down_payment_fixed')
    def get_down_payment_percentage(self):
        if self.down_payment_fixed and self.quotation_number_id.amount_total != 0:
            self.down_payment_percentage = self.down_payment_fixed * 100 / self.contract_value

    @api.depends('project_id')
    def get_work_plan(self):
        for res in self:
            res.work_plan_id = False
            for rec in self.env['work.plan'].search([('project_id', '=', res.project_id.id)], limit=1):
                res.work_plan_id = rec.id

    @api.model
    def create(self, vals):
        res = super(OwnerContract, self).create(vals)
        date_today = datetime.strptime(str(date.today()), '%Y-%m-%d').date()
        if res.type == 'contractor':
            res.name = self.env['ir.sequence'].next_by_code('owner.contract.code')
            res.contract_id = self.env['contracts'].search([('is_owner_contract', '=', True)]).id
            res.customer_account_id = res.contract_id.customer_account_id.id
            res.revenue_account_id = res.contract_id.revenue_account_id.id
            res.conditions = res.contract_id.terms_conditions
        elif res.type == 'subcontractor':
            res.contract_id = self.env['contracts'].search([('is_subcontractor_contract', '=', True)]).id
            res.customer_account_id = res.contract_id.customer_account_id.id
            res.revenue_account_id = res.contract_id.revenue_account_id.id
            res.conditions = res.contract_id.terms_conditions

            if res.subcontractor_type == 'civil':
                res.name = str(date_today.year) + '-' + str(res.project_id.project_no) + '-' + str('C-') + str(
                    self.env['ir.sequence'].next_by_code('subcontractor.contract.code'))
            elif res.subcontractor_type == 'electricity':
                res.name = str(date_today.year) + '-' + str(res.project_id.project_no) + '-' + str('E-') + str(
                    self.env['ir.sequence'].next_by_code('subcontractor.contract.code.2'))
            elif res.subcontractor_type == 'mechanics':
                res.name = str(date_today.year) + '-' + str(res.project_id.project_no) + '-' + str('M-') + str(
                    self.env['ir.sequence'].next_by_code('subcontractor.contract.code.3'))
        else:
            res.name = 'New'

        if not res.work_plan_id and res.type == 'subcontractor':
            raise exceptions.ValidationError('You must create work plan item first.')

        if res.type == 'contractor':
            contract_lines = [(5, 0, 0)]
            if res.quotation_number_id:
                for rec in res.quotation_number_id.order_line:
                    contract_lines.append((0, 0, {
                        'code': rec.code,
                        'product_id': rec.product_id.id,
                        'description': rec.name,
                        'quantity': rec.product_uom_qty,
                        'price_unit': rec.price_unit if res.type == 'contractor' else 0.0,
                        'product_uom_id': rec.product_uom.id,
                        'tax_id': [(6, 0, res.tax_id.ids)]
                    }))

            res.contract_line_ids = contract_lines

        return res

    def write(self, vals):
        res = super(OwnerContract, self).write(vals)
        if self.contract_line_ids:
            for rec in self.contract_line_ids:
                rec.tax_id = [(6, 0, self.tax_id.ids)]
        return res

    @api.depends('owner_contractor_invoice_count', 'sub_contractor_invoice_count')
    def get_owner_contractor_invoice_count(self):
        self.owner_contractor_invoice_count = self.env['account.move'].search_count(
            [('contract_id', '=', self.id), ('move_type', '=', 'out_invoice'), ('contract_type', '=', self.type)])
        self.sub_contractor_invoice_count = self.env['account.move'].search_count(
            [('contract_id', '=', self.id), ('move_type', '=', 'in_invoice'), ('contract_type', '=', self.type)])

    def button_invoice_create(self):
        lines = []

        for rec in self.contract_line_ids:
            lines.append((0, 0, {
                'product_id': rec.product_id.id,
                'account_id': rec.product_id.property_account_income_id.id,
                'name': rec.work_plan_item_id.name,
                'price_unit': rec.price_unit,
                'total_contract_qty': rec.quantity,
                'quantity': 1,
                'product_uom_id': rec.product_uom_id.id,
                'exclude_from_invoice_tab': False,
            }))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'view_type': 'form',
            'name': 'Account Invoice',
            'target': 'current',
            'context': {'default_type': 'out_invoice', 'default_invoice_date': self.date,
                        'default_contract_type': self.type, 'default_contract_project_id': self.project_id.id,
                        'default_is_contract_invoice': True, 'default_contract_type_id': self.contract_id.id,
                        'default_contract_id': self.id, 'default_contract_quotation_id': self.quotation_number_id.id,
                        'default_invoice_line_ids': lines},

        }

    def button_bill_create(self):
        lines = [(5, 0, 0)]
        for rec in self.contract_line_ids:
            lines.append((0, 0, {
                'product_id': rec.product_id.id,
                'price_unit': rec.price_unit,
                'total_contract_qty': rec.quantity,
                'quantity': 0,
                'product_uom_id': rec.product_uom_id.id,
            }))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'view_type': 'form',
            'name': 'Account Invoice',
            'target': 'current',
            'context': {'default_type': 'in_invoice', 'default_invoice_date': self.date,
                        'default_contract_type': self.type, 'default_contract_project_id': self.project_id.id,
                        'default_is_contract_invoice': True, 'default_contract_type_id': self.contract_id.id,
                        'default_contract_id': self.id, 'default_invoice_line_ids': lines},

        }

    def open_related_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'name': 'Account Invoice',
            'target': 'current',
            'domain': [('contract_id', '=', self.id), ('move_type', '=', 'out_invoice'), ('contract_type', '=', self.type)],
            'context': {'create': False, 'edit': False},

        }

    def open_related_bills(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'name': 'Account Invoice',
            'target': 'current',
            'domain': [('contract_id', '=', self.id), ('move_type', '=', 'in_invoice'), ('contract_type', '=', self.type)],
            'context': {'create': False, 'edit': False},
        }

    @api.depends('contract_line_ids', 'tax_id')
    def get_contract_value(self):
        self.contract_value = sum(self.contract_line_ids.mapped('price_subtotal'))

    @api.depends('project_id')
    def get_data_from_project(self):
        for rec in self:
            if rec.project_id:
                rec.customer_id = rec.project_id.partner_id.id
                rec.project_end_date = rec.project_id.project_end_date
                rec.project_location_id = rec.project_id.location_id
            else:
                rec.customer_id = False

    @api.onchange('project_id')
    def get_quotation(self):
        for rec in self:
            if rec.project_id:
                rec.quotation_number_id = rec.project_id.so_id.id
            else:
                rec.quotation_number_id = False

    @api.onchange('contract_id')
    def get_contract_data(self):
        for rec in self:
            if rec.contract_id:
                rec.customer_account_id = rec.contract_id.customer_account_id.id
                rec.revenue_account_id = rec.contract_id.revenue_account_id.id

    def action_remove_lines(self):
        for item in self:
            if item.contract_line_ids:
                for line in item.contract_line_ids:
                    if line.delete_line:
                        line.unlink()


class OwnerContractLine(models.Model):
    _name = 'owner.contract.line'

    code = fields.Char(string="Code", required=False, )
    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )
    description = fields.Text(string="Description", required=False, )
    quantity = fields.Float(string="Quantity", required=False, )
    price_unit = fields.Float(string="Unit Price", required=False, )
    product_uom_id = fields.Many2one(comodel_name="uom.uom", string="Unit Of Measure", required=False, )
    tax_id = fields.Many2many(comodel_name="account.tax", string="Taxes", required=False, )
    price_subtotal = fields.Float(string="Subtotal", compute='get_price_subtotal', store=True, required=False, )
    total_work_plan_qty = fields.Float(string="Total Qty", required=False, )
    note = fields.Text(string="Note", required=False, )

    owner_contract_id = fields.Many2one(comodel_name="owner.contract", string="", required=False, )

    work_plan_item_id = fields.Many2one(comodel_name="work.plan.items.line", string="Work Plan Item", required=False, )

    update_product = fields.Boolean(string="Update Products", )
    delete_line = fields.Boolean(default=True)

    @api.onchange('product_id', 'work_plan_item_id')
    def get_product_data(self):
        for rec in self:
            rec.code = rec.product_id.default_code
            prev_qty = self.env['owner.contract.line'].search(
                [('product_id', '=', rec.product_id.id), ('work_plan_item_id', '=', rec.work_plan_item_id.id)])
            total_prev_qty = 0.0
            for prev in prev_qty:
                total_prev_qty += prev.quantity

            for line in rec.owner_contract_id.work_plan_id.work_plan_line_ids:
                if rec.product_id.id == line.product_id.id and rec.work_plan_item_id == line.work_plan_item_id:
                    # rec.price_unit = line.price_unit
                    rec.quantity = line.quantity - total_prev_qty
                    rec.total_work_plan_qty = line.quantity
                    # rec.product_uom_id = line.product_uom_id.id
            for ord_line in rec.owner_contract_id.quotation_number_id.order_line:
                if rec.product_id.id == ord_line.product_id.id:
                    rec.price_unit = ord_line.price_unit
                    # rec.quantity = line.quantity
                    rec.product_uom_id = rec.product_id.uom_id.id

    @api.onchange('update_product', 'quantity', 'product_id')
    def get_products_from_contract_quotation(self):
        for rec in self:
            if not rec.owner_contract_id.work_plan_id:
                products = []
                for res in rec.owner_contract_id.quotation_number_id.order_line:
                    products.append(res.product_id.id)

                return {'domain': {'product_id': [('id', 'in', products)]}}
            else:
                products = []
                for res in rec.owner_contract_id.work_plan_id.work_plan_line_ids:
                    products.append(res.product_id.id)

                return {'domain': {'product_id': [('id', 'in', products)]}}

    @api.depends('product_id', 'quantity', 'price_unit', 'tax_id')
    def get_price_subtotal(self):
        for rec in self:
            tax_amount = 0.0
            for tax in rec.tax_id:
                tax_amount += tax.amount / 100 * rec.price_unit * rec.quantity
            rec.price_subtotal = (rec.price_unit * rec.quantity) + tax_amount

    @api.onchange('product_id', 'update_product', 'work_plan_item_id')
    def filter_work_plan_items(self):
        for rec in self:
            work_plan_items = self.env['work.plan'].search([('project_id', '=', rec.owner_contract_id.project_id.id),
                                                            ('id', '=', rec.owner_contract_id.work_plan_id.id)],
                                                           limit=1)
            work_plan_items_line = []
            for rec2 in work_plan_items:
                for line in rec2.work_plan_line_ids:
                    if line.product_id == rec.product_id:
                        work_plan_items_line.append(line.work_plan_item_id.id)

            return {'domain': {'work_plan_item_id': [('id', 'in', work_plan_items_line)]}}


class OwnerContractDeduction(models.Model):
    _name = 'owner.contract.deduction'

    deduction_accounts_id = fields.Many2one(comodel_name="deduction.accounts",
                                            domain=[('deduction_type', '=', 'deduction')], string="Deduction",
                                            required=False, )
    account_id = fields.Many2one(comodel_name="account.account", string="Account", required=False, )
    name = fields.Char(string="Name", required=False, )
    is_percentage = fields.Boolean(string="Is Percentage")
    percentage_value = fields.Float(string="Percentage/Value", required=False, )
    value = fields.Float(string="Value", required=False, compute="get_value")

    owner_cont_id = fields.Many2one(comodel_name="owner.contract", string="", required=False, )

    @api.onchange('deduction_accounts_id')
    def get_account(self):
        for rec in self:
            rec.account_id = rec.deduction_accounts_id.counterpart_account_id.id
            rec.is_percentage = rec.deduction_accounts_id.is_percentage

    @api.depends('deduction_accounts_id', 'owner_cont_id.contract_value', 'percentage_value')
    def get_value(self):
        for rec in self:
            rec.value = 0.0
            if rec.percentage_value:
                if rec.is_percentage:
                    rec.value = rec.owner_cont_id.contract_value * rec.percentage_value / 100
                else:
                    rec.value = rec.percentage_value


class OwnerContractAddition(models.Model):
    _name = 'owner.contract.addition'

    deduction_accounts_id = fields.Many2one(comodel_name="deduction.accounts",
                                            domain=[('deduction_type', '=', 'addition')], string="Addition",
                                            required=False, )
    account_id = fields.Many2one(comodel_name="account.account", string="Account", required=False, )
    name = fields.Char(string="Name", required=False, )
    is_percentage = fields.Boolean(string="Is Percentage")
    percentage_value = fields.Float(string="Percentage/Value", required=False, )
    value = fields.Float(string="Value", required=False, compute="get_value")

    owner_cont_id = fields.Many2one(comodel_name="owner.contract", string="", required=False, )

    @api.onchange('deduction_accounts_id')
    def get_account(self):
        for rec in self:
            rec.account_id = rec.deduction_accounts_id.counterpart_account_id.id
            rec.is_percentage = rec.deduction_accounts_id.is_percentage

    @api.depends('deduction_accounts_id', 'owner_cont_id.contract_value', 'percentage_value')
    def get_value(self):
        for rec in self:
            rec.value = 0.0
            if rec.percentage_value:
                if rec.is_percentage:
                    rec.value = rec.owner_cont_id.contract_value * rec.percentage_value / 100
                else:
                    rec.value = rec.percentage_value


class ConstrainedBy(models.Model):
    _name = 'constrained.by'
    _rec_name = 'name'
    _description = ''

    name = fields.Char(string="", required=False, )
    type = fields.Selection(string="Type", selection=[('site_handover', 'Site Handover'),
                                                      ('signing_of_contract', 'Signing of Contract'),
                                                      ('advanced_payment', 'Advanced Payment'),
                                                      ('IFC_drawings', 'IFC drawings'), ], required=False, )
