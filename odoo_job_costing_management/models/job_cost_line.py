# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class JobCostLine(models.Model):
    _name = 'job.cost.line'
    _rec_name = 'description'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for rec in self:
            rec.description = rec.product_id.name
            rec.product_qty = 1.0
            rec.product_qty = 1.0
            rec.uom_id = rec.product_id.uom_id.id
            if rec.job_type not in ['labour', 'equipment']:
                rec.cost_price = rec.product_id.standard_price  # lst_price

    @api.onchange('employee_id')
    def onchange_employee(self):
        for rec in self:
            if rec.employee_id and rec.job_type in ['labour']:
                rec.cost_price = rec.employee_id.timesheet_cost

    @api.onchange('maintenance_id')
    def onchange_maintainance(self):
        for rec in self:
            if rec.maintenance_id and rec.job_type in ['equipment']:
                rec.cost_price = rec.maintenance_id.timesheet_cost

    @api.depends('product_qty', 'hours', 'cost_price', 'direct_id')
    def _compute_total_cost(self):
        for rec in self:
            if rec.job_type in ['labour', 'equipment']:
                rec.product_qty = 0.0
                rec.total_cost = rec.hours * rec.cost_price
            else:
                rec.hours = 0.0
                rec.total_cost = rec.product_qty * rec.cost_price

    # @api.depends('purchase_order_line_ids', 'purchase_order_line_ids.order_id.state')
    def _compute_actual_transfer_qty(self):
        for rec in self:
            rec.actual_transfer_qty = False
            # for line in rec.purchase_order_line_ids:
                # transfer = self.env['stock.move'].search([('product_id', '=', line.product_id.id),
                                                          # ('product_id', '=', rec.product_id.id),
                                                          # ('procurement_line_id', '=', line.procurement_line_id.id),
                                                          # ('state', 'in', ['partially_available', 'assigned', 'done'])])

            transfer = self.env['stock.move'].search([('product_id', '=', rec.product_id.id), ('cost_id', '=', rec.direct_id.id), ('job_cost_line_id', '=', rec.id), ('state', 'in', ['done']), ('procurement_line_id', '!=', False)])
                                                      # ('state', 'in', ['partially_available', 'assigned', 'done'])])
                                                    
            if transfer:
                # for trans in transfer:
                #     rec.actual_transfer_qty += trans.reserved_availability if trans.reserved_availability else trans.quantity_done
                # break
                for trans in transfer:
                    rec.actual_transfer_qty += trans.quantity_done
                break

    @api.depends('purchase_order_line_ids', 'purchase_order_line_ids.product_qty',
                 'purchase_order_line_ids.order_id.state')
    def _compute_actual_quantity(self):
        for rec in self:
            # rec.actual_quantity = sum([p.product_qty for p in rec.purchase_order_line_ids])
            rec.actual_quantity = sum(
                [p.order_id.state in ['purchase', 'done'] and p.product_qty for p in rec.purchase_order_line_ids])

    # @api.depends('timesheet_line_ids', 'timesheet_line_ids.unit_amount')
    @api.depends('employee_id', 'timesheet_line_ids', 'timesheet_line_ids.unit_amount', 'maintenance_id')
    def _compute_actual_hour(self):
        for rec in self:
            # if rec.job_type and rec.job_type == 'labour':
                if rec.employee_id and rec.direct_id.project_id:
                    timesheet_lines = self.env['account.analytic.line'].search([('employee_id', '=', rec.employee_id.id), ('project_id', '=', rec.direct_id.project_id.id), 
                        ('task_id', 'in', rec.direct_id.project_id.task_ids and rec.direct_id.project_id.task_ids.ids)])
                    rec.actual_hour = sum([p.unit_amount for p in timesheet_lines])
            # elif rec.job_type and rec.job_type == 'equipment':
                if rec.maintenance_id and rec.maintenance_id.timesheet_ids:
                    timesheet_lines = rec.maintenance_id.timesheet_ids
                    print ('33333', timesheet_lines)
                    rec.actual_hour = sum([p.unit_amount for p in timesheet_lines])

                else:
                    rec.actual_hour = 0.0


    @api.depends('account_invoice_line_ids', 'account_invoice_line_ids.quantity',
                 'account_invoice_line_ids.move_id.state')
    def _compute_actual_invoice_quantity(self):
        for rec in self:
            rec.actual_invoice_quantity = sum([p.quantity for p in rec.account_invoice_line_ids])
            # rec.actual_invoice_quantity = sum([p.move_id.state in ['open', 'paid'] and p.quantity or 0.0 for p in rec.account_invoice_line_ids])

    @api.depends('product_qty', 'account_invoice_line_ids', 'account_invoice_line_ids.quantity',
                 'account_invoice_line_ids.price_unit', 'account_invoice_line_ids.move_id.state')
    def _compute_actual_vendor_cost(self):
        for rec in self:
            rec.actual_vendor_cost = sum([p.quantity * p.price_unit for p in rec.account_invoice_line_ids])

    @api.onchange('qty_per_line', 'direct_id')
    def get_product_qty(self):
        for rec in self:
            rec.product_qty = rec.qty_per_line * rec.direct_id.tender_qty

    qty_per_line = fields.Float(string="Qty", required=False, )

    direct_id = fields.Many2one(
        'job.costing',
        string='Job Costing'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        copy=False,
        required=True,
    )
    description = fields.Char(
        string='Description',
        copy=False,
    )
    reference = fields.Char(
        string='Reference',
        copy=False,
    )
    date = fields.Date(
        string='Date',
        required=True,
        copy=False,
    )
    product_qty = fields.Float(
        string='Planned Qty',
        copy=False,
    )
    uom_id = fields.Many2one(
        'uom.uom',  # product.uom
        string='Uom',
    )
    cost_price = fields.Float(
        string='Cost / Unit',
        copy=False,
    )
    total_cost = fields.Float(
        string='Cost Price Sub Total',
        compute='_compute_total_cost',
        store=True,
    )
    analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.user.company_id.currency_id,
        readonly=True
    )
    job_type_id = fields.Many2one(
        'job.type',
        string='Job Type',
    )
    job_type = fields.Selection(
        selection=[('material', 'Material'),
                   ('labour', 'Labour'),
                   ('overhead', 'Overhead'), ('subcontractor', 'Subcontractor'), ('equipment', 'Equipment'),
                   ('other', 'Other')
                   ],
        string="Type",
        required=True,
    )
    basis = fields.Char(
        string='Basis'
    )
    hours = fields.Float(
        string='Hours'
    )
    purchase_order_line_ids = fields.One2many(
        'purchase.order.line',
        'job_cost_line_id',
    )
    timesheet_line_ids = fields.One2many(
        'account.analytic.line',
        'job_cost_line_id',
    )
    account_invoice_line_ids = fields.One2many(
        'account.move.line',
        'job_cost_line_id',
    )
    actual_quantity = fields.Float(
        string='Actual Purchased Quantity',
        compute='_compute_actual_quantity',
    )
    actual_invoice_quantity = fields.Float(
        string='Actual Vendor Bill Quantity',
        compute='_compute_actual_invoice_quantity',
    )
    actual_hour = fields.Float(
        string='Actual Timesheet Hours',
        compute='_compute_actual_hour',
    )

    actual_transfer_qty = fields.Float(string='Actual Transferred QTY',
                                       compute='_compute_actual_transfer_qty')

    employee_id = fields.Many2one('hr.employee', string='Employee')

    maintenance_id = fields.Many2one('maintenance.equipment', string='Maintenance')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('employee_id') and vals.get('job_type'):
                if vals.get('job_type') == 'labour':
                    employee_id = self.env['hr.employee'].browse(vals.get('employee_id'))
                    vals.update({'cost_price': employee_id.timesheet_cost})
            if vals.get('maintenance_id') and vals.get('job_type'):
                if vals.get('job_type') == 'equipment':
                    maintenance_id = self.env['maintenance.equipment'].browse(vals.get('maintenance_id'))
                    vals.update({'cost_price': maintenance_id.timesheet_cost})

        return super(JobCostLine, self).create(vals_list)