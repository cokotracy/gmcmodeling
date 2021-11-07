# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    @api.depends('project_id','total_progress_billing')
    def _set_total_progress_bill(self):
        for rec in self:
            rec.total_progress_billing = rec.project_id.total_progress_account

    @api.depends('amount_total','invoice_to_date','partner_id','project_id')
    def _set_invoiceto_date(self):
        for rec in self:
            invoice_to_date = 0.0
            cus_inv = self.env['account.move'].search([('state', 'in', ['posted']),('move_type','in',['in_invoice','in_refund']), ('partner_id', '=', rec.partner_id.id), ('project_id', '=', rec.project_id.id)])
            for inv in cus_inv:
                invoice_to_date  += inv.amount_total
            rec.invoice_to_date = invoice_to_date

    @api.depends('total_progress_billing', 'invoice_to_date','remaining_progress_billing')
    def _set_remaining_progress_billing(self):
        for rec in self:
            rec.remaining_progress_billing = rec.total_progress_billing - rec.invoice_to_date

    @api.depends('amount_total','amount_residual','previously_invoice','previously_invoice_due','partner_id','project_id')
    def _set_previously_invoiced(self):
        for rec in self:
            previously_invoice = 0.0
            previously_invoice_due = 0.0

            pre_inv = self.env['account.move'].search([('state', 'in', ['posted']),('move_type','in',['in_invoice','in_refund']), ('partner_id', '=', rec.partner_id.id), ('project_id', '=', rec.project_id.id)])
            if len(pre_inv) == 1:
                rec.previously_invoice = 0.0
            if len(pre_inv) > 1:
                rec.previously_invoice = 0.0
                for pre in pre_inv:
                    if pre.id != rec.id:
                        previously_invoice += pre.amount_total
                        previously_invoice_due += pre.amount_residual
            rec.previously_invoice = previously_invoice
            rec.previously_invoice_due = previously_invoice_due

                #rec.previously_invoice = rec.previously_invoice - rec.amount_total
                #rec.previously_invoice_due = rec.previously_invoice_due - rec.residual

    @api.depends('amount_total','current_invoice')
    def _set_current_invoiced(self):
        for rec in self:
            rec.current_invoice = rec.amount_total

    @api.depends('amount_residual','less_paid_amount')
    def _set_less_paid_amount(self):
        for rec in self:
            rec.less_paid_amount = rec.amount_residual

    @api.depends('less_paid_amount','previously_invoice','current_invoice','total_due')
    def _set_total_due(self):
        for rec in self:
            rec.total_due = rec.previously_invoice_due + rec.less_paid_amount

    progress_bill_title = fields.Char(
        string='Progress Billing Title',
    )
    project_id = fields.Many2one(
        'account.analytic.account',
        string='Project',
        copy=False,
    )
    total_progress_billing = fields.Float(
        string="Total Progress Billing",
        compute='_set_total_progress_bill',
        copy=False,
        store=False,
    )
    invoice_to_date = fields.Float(
        string="Invoice To Date",
        compute='_set_invoiceto_date',
        copy=False,
        store=True,
    )
    remaining_progress_billing = fields.Float(
        string="Remaining Progress Billing",
        compute='_set_remaining_progress_billing',
        copy=False,
        store=False,
    )
    previously_invoice = fields.Float(
        string="Previously Invoiced",
        compute='_set_previously_invoiced',
        copy=False,
        store=False,
    )
    previously_invoice_due = fields.Float(
        string="Previously Invoiced Due",
        compute='_set_previously_invoiced',
        copy=False,
        store=False,
    )
    current_invoice = fields.Float(
        string="Current Invoiced",
        compute='_set_current_invoiced',
        copy=False,
        store=False,
    )
    less_paid_amount = fields.Float(
        string="Less Paid Amount",
        compute='_set_less_paid_amount',
        copy=False,
        store=False,
    )
    total_due = fields.Float(
        string="Total Due Now",
        compute='_set_total_due',
        copy=False,
        store=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
