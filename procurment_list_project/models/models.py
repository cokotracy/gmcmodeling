# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date


class StockMove(models.Model):
    _inherit = 'stock.move'

    procurement_line_id = fields.Many2one(comodel_name="procurment.list.lines", string="", required=False, )


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    procurement_list_id = fields.Many2one(comodel_name="procurment.list", string="", required=False, )

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    procurement_line_id = fields.Many2one(comodel_name="procurment.list.lines", string="", required=False, )

class ProcurementList(models.Model):
    _name = 'procurment.list'
    _inherit = 'mail.thread'
    _description = 'Procurement List'
    _order = 'id desc'

    @api.model
    def _default_picking_type_id(self):
        picking_types = self.env['stock.picking.type'].search(
            [('code', '=', 'internal')], limit=1)
        return picking_types

    @api.model
    def _default_source_location_id(self):
        location = self.env['stock.location'].search(
            [('is_default', '=', True)], limit=1)
        return location

    name = fields.Many2one('project.project', string='project name', tracking=True)
    project_no = fields.Char(string='project_no', tracking=True)
    partner_id = fields.Many2one('res.partner', string='customer', tracking=True)
    start_date = fields.Date(string='start date', tracking=True)
    end_date = fields.Date(string='end date', tracking=True)
    procurment_lines = fields.One2many('procurment.list.lines', 'procurment_id', string='Project tender',
                                       tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', tracking=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
                                          tracking=True)
    discount = fields.Float(string='Discount %', tracking=True)
    type_send = fields.Selection([
        ('C', 'Civil'), ('M', 'Mechanics'), ('E', 'Electricity')],
        string='Type', tracking=True)

    # Add by omnya_compute_count_of_attachemnt
    sub_procurement_lines = fields.One2many('procurment.list.lines', 'sub_procurement_id', string='Sample List')

    picking_type_id = fields.Many2one(comodel_name="stock.picking.type", string="Operation Type",
                                      default=_default_picking_type_id, domain=[('code', '=', 'internal')],
                                      required=False, tracking=True)
    source_location_id = fields.Many2one(comodel_name="stock.location", string="Source Location",
                                         default=_default_source_location_id, required=False, tracking=True)
    location_id = fields.Many2one(comodel_name="stock.location", string="Destination Location",
                                  domain=[('usage', '=', 'internal')], tracking=True, required=False, )

    @api.onchange('picking_type_id')
    def get_source_location(self):
        self.source_location_id = self.picking_type_id.default_location_src_id

    def confirm_procurment_list(self, send_to_po):
        if not self.procurment_lines:
            raise exceptions.ValidationError("Lines is empty check lines that contain products and try again")

        products_line = self.procurment_lines.mapped('product')
        if not products_line:
            raise exceptions.ValidationError("There is no products in lines to check")

        records = self.env['stock.picking']
        products_list = []
        flag = False
        if send_to_po:
            for rec in self.procurment_lines.filtered(lambda line: line.remain_partial_qty > 0 and line.send_to_po == True):
                if rec.product:
                    if not rec.moved:
                        product_uom = rec.remain_partial_qty
                        products_list.append((0, 0, {
                            'product_id': rec.product.id,
                            'name': rec.product.name,
                            'product_uom': rec.uom_id.id,
                            'product_uom_qty': product_uom,
                            # 'product_uom_qty': rec.planned_qty if not rec.qty_actually else rec.qty_actually,
                            'procurement_line_id': rec.id,
                            'cost_id': rec.cost_id and rec.cost_id.id,
                            'job_cost_line_id': rec.job_cost_line_id and rec.job_cost_line_id.id
                        }))
                    if rec.planned_qty == rec.qty_actually and rec.remain_partial_qty == 0:
                        rec.moved = True
                    flag = False if rec.moved else True
        else:
            for rec in self.procurment_lines.filtered(lambda line: line.remain_partial_qty > 0 and line.send_to_pr == True):
                if rec.product and rec.send_to_pr:
                    if not rec.moved:
                        product_uom = rec.remain_partial_qty
                        products_list.append((0, 0, {
                            'product_id': rec.product.id,
                            'name': rec.product.name,
                            'product_uom': rec.uom_id.id,
                            'product_uom_qty': product_uom,
                            # 'product_uom_qty': rec.planned_qty if not rec.qty_actually else rec.qty_actually,
                            'procurement_line_id': rec.id,
                            'cost_id': rec.cost_id and rec.cost_id.id,
                            'job_cost_line_id': rec.job_cost_line_id and rec.job_cost_line_id.id
                        }))
                    if rec.planned_qty == rec.qty_actually and rec.remain_partial_qty == 0:
                        rec.moved = True
                    flag = False if rec.moved else True
        if flag:
            picking_created = records.create({
                'move_type': 'direct',
                'partner_id': self.partner_id.id,
                'picking_type_id': self.picking_type_id.id,
                'state': 'draft',
                'location_id': self.source_location_id.id,
                'procurement_list_id': self.id,
                'location_dest_id': self.location_id.id,
                'move_lines': products_list,
            })
            picking_created.action_confirm()
            picking_created.action_assign()
            return picking_created

    def send_to_pr(self):
        self.confirm_procurment_list(send_to_po=False)
        stock_moves = self.env['stock.move']

        li = []
        for rec in self.procurment_lines.filtered(lambda line: line.send_to_pr == True and line.remain_partial_qty > 0 and line.code in ['a', 'b']):
            if rec.send_to_pr and rec.action_line == 0:
                if not rec.type_send_line:
                    raise UserError('Choose Type first')
                for move in stock_moves.search([('procurement_line_id', '=', rec.id)]):
                    print ('find move for  linnnnn', rec)
                    if move.picking_id.state in ['confirmed', 'assigned']:
                        if (
                                move.reserved_availability < move.product_uom_qty and move.reserved_availability != 0) or (
                                move.reserved_availability == 0 and move.quantity_done == 0):
                            rec.action_line = 1
                            if rec.qty_actually > rec.partial_qty or rec.planned_qty > rec.partial_qty:
                                rec.action_line = 4  # partially
                            dic = {'job_id': rec.job_id, 'cost_id': rec.cost_id, 'product_id': rec.product,
                                   'vendor': rec.vendor,
                                   'job_cost_line': rec.job_cost_line_id,
                                   'actual_qty': rec.remain_partial_qty,
                                   # 'actual_qty': rec.qty_actually - move.reserved_availability,
                                   'planned_qty': rec.planned_qty,
                                   'procurement_line_id': rec.id, 'type_send_line': rec.type_send_line}
                            li.append(dic)

            elif rec.send_to_pr and rec.action_line == 4 and rec.remain_partial_qty != 0 or not rec.moved:
                for move in stock_moves.search([('procurement_line_id', '=', rec.id)], order='date desc',
                                               limit=1):
                    if move.picking_id.state in ['confirmed', 'assigned']:
                        if (
                                move.reserved_availability < move.product_uom_qty and move.reserved_availability != 0) or (
                                move.reserved_availability == 0 and move.quantity_done == 0):
                            dic = {'job_id': rec.job_id,
                                   'cost_id': rec.cost_id,
                                   'product_id': rec.product,
                                   'vendor': rec.vendor,
                                   'job_cost_line': rec.job_cost_line_id,
                                   'actual_qty': rec.remain_partial_qty,
                                   'planned_qty': rec.planned_qty,
                                   'price_unit': 0.00, 'procurement_line_id': rec.id,
                                   'type_send_line': rec.type_send_line}
                            li.append(dic)
            rec.qty_actually += rec.remain_partial_qty
            rec.remain_partial_qty = 0.0


        # ADD by omnya ########################
        for sub_pro in self.sub_procurement_lines:
            if sub_pro.send_to_pr and sub_pro.action_line == 0:
                sub_pro.action_line = 1
                for rec in self.procurment_lines:
                    if rec.action_line == 1 and rec.send_to_pr:

                        if rec.product == sub_pro.parent_product:
                            dic1 = {'job_id': rec.job_id, 'cost_id': rec.cost_id,
                                    'product_id': sub_pro.product, 'vendor': sub_pro.vendor,
                                    'job_cost_line': rec.job_cost_line_id, 'actual_qty': sub_pro.qty_actually,
                                    'planned_qty': sub_pro.planned_qty}
                            li.append(dic1)
        ##############################################

        jobs_ids = sorted(set(x['job_id'] for x in li))
        for l in jobs_ids:
            ins_c = []
            ins_m = []
            ins_e = []
            for rec in li:
                if l.id == rec['job_id'].id:
                    if rec.get('type_send_line') and rec['type_send_line'] == 'C':
                        for move_line in stock_moves.search(
                                [('procurement_line_id', '=', rec['procurement_line_id'])], order='date desc',
                                limit=1):
                            if move_line.picking_id.state in ['confirmed', 'assigned']:
                                if (
                                        move_line.reserved_availability < move_line.product_uom_qty and move_line.reserved_availability != 0 and move_line.quantity_done != move_line.product_uom_qty) or (
                                        move_line.reserved_availability == 0 and move_line.quantity_done == 0):
                                    ins_dic = {'job_cost_line_id': rec['job_cost_line'].id,
                                           'cost_id': rec['cost_id'].id,
                                           'requisition_type': 'purchase',
                                           'product_id': rec['product_id'].id,
                                           'description': rec['product_id'].name,
                                           'uom': rec['product_id'].uom_id.id,
                                           'qty': move_line.product_uom_qty,
                                           'procurement_line_id': rec['procurement_line_id'],
                                           # 'qty': rec['actual_qty'] if rec['actual_qty'] >= 0.00 else rec['planned_qty'],
                                           'partner_id': rec['vendor'].id if not rec['vendor'].id else [rec['vendor'].id],
                                           }
                                    ins_c.append((0, 0, ins_dic))
                    if rec.get('type_send_line') and rec['type_send_line'] == 'M':
                            for move_line in stock_moves.search(
                                    [('procurement_line_id', '=', rec['procurement_line_id'])], order='date desc',
                                    limit=1):
                                if move_line.picking_id.state in ['confirmed', 'assigned']:
                                    if (
                                            move_line.reserved_availability < move_line.product_uom_qty and move_line.reserved_availability != 0 and move_line.quantity_done != move_line.product_uom_qty) or (
                                            move_line.reserved_availability == 0 and move_line.quantity_done == 0):
                                        ins_dic = {'job_cost_line_id': rec['job_cost_line'].id,
                                               'cost_id': rec['cost_id'].id,
                                               'requisition_type': 'purchase',
                                               'product_id': rec['product_id'].id,
                                               'description': rec['product_id'].name,
                                               'uom': rec['product_id'].uom_id.id,
                                               'qty': move_line.product_uom_qty,
                                               'procurement_line_id': rec['procurement_line_id'],
                                               # 'qty': rec['actual_qty'] if rec['actual_qty'] >= 0.00 else rec['planned_qty'],
                                               'partner_id': rec['vendor'].id if not rec['vendor'].id else [rec['vendor'].id],
                                               }
                                        ins_m.append((0, 0, ins_dic))
                    if rec.get('type_send_line') and rec['type_send_line'] == 'E':
                            for move_line in stock_moves.search(
                                    [('procurement_line_id', '=', rec['procurement_line_id'])], order='date desc',
                                    limit=1):
                                if move_line.picking_id.state in ['confirmed', 'assigned']:
                                    if (
                                            move_line.reserved_availability < move_line.product_uom_qty and move_line.reserved_availability != 0 and move_line.quantity_done != move_line.product_uom_qty) or (
                                            move_line.reserved_availability == 0 and move_line.quantity_done == 0):
                                        ins_dic = {'job_cost_line_id': rec['job_cost_line'].id,
                                               'cost_id': rec['cost_id'].id,
                                               'requisition_type': 'purchase',
                                               'product_id': rec['product_id'].id,
                                               'description': rec['product_id'].name,
                                               'uom': rec['product_id'].uom_id.id,
                                               'qty': move_line.product_uom_qty,
                                               'procurement_line_id': rec['procurement_line_id'],
                                               # 'qty': rec['actual_qty'] if rec['actual_qty'] >= 0.00 else rec['planned_qty'],
                                               'partner_id': rec['vendor'].id if not rec['vendor'].id else [rec['vendor'].id],
                                               }
                                        ins_e.append((0, 0, ins_dic))
                    
            if ins_c:
                dic = {
                    'analytic_account_id': self.analytic_account_id.id,
                    'department_id': self.department_id.id,
                    'task_id': l.id,
                    'requisition_line_ids': ins_c,
                    'project_id': self.name.id,
                    'type_pr': 'C',
                    'procurement_id': self.id}
                pl = self.env['material.purchase.requisition']
                pl.create(dic)
            if ins_m:
                dic = {
                    'analytic_account_id': self.analytic_account_id.id,
                    'department_id': self.department_id.id,
                    'task_id': l.id,
                    'requisition_line_ids': ins_m,
                    'project_id': self.name.id,
                    'type_pr': 'M',
                    'procurement_id': self.id}
                pl = self.env['material.purchase.requisition']
                pl.create(dic)
            if ins_e:
                dic = {
                    'analytic_account_id': self.analytic_account_id.id,
                    'department_id': self.department_id.id,
                    'task_id': l.id,
                    'requisition_line_ids': ins_e,
                    'project_id': self.name.id,
                    'type_pr': 'E',
                    'procurement_id': self.id}
                pl = self.env['material.purchase.requisition']
                pl.create(dic)
            # dic = {
            #     'analytic_account_id': self.analytic_account_id.id,
            #     'department_id': self.department_id.id,
            #     'task_id': l.id,
            #     'requisition_line_ids': ins,
            #     'project_id': self.name.id,
            #     'type_pr': rec['type_send_line']}
            # pl = self.env['material.purchase.requisition']
            # pl.create(dic)

    def send_to_po(self):
        self.confirm_procurment_list(send_to_po=True)
        stock_moves = self.env['stock.move']
        for rec in self.procurment_lines.filtered(lambda line: line.send_to_po == True and line.remain_partial_qty > 0 and line.code in ['a', 'b']):
            li = []
            if rec.send_to_po:
                if not rec.type_send_line:
                    raise UserError('Choose Type first')
                if not rec.vendor.id:
                    raise UserError('Any PO order you must have a vendor')
                elif rec.action_line == 0:
                    for move in stock_moves.search([('procurement_line_id', '=', rec.id)]):
                        if move.picking_id.state in ['confirmed', 'assigned']:
                            if (
                                    move.reserved_availability < move.product_uom_qty and move.reserved_availability != 0) or (
                                    move.reserved_availability == 0 and move.quantity_done == 0):
                                rec.action_line = 2
                                if rec.qty_actually > rec.partial_qty or rec.planned_qty > rec.partial_qty:
                                    rec.action_line = 4  # partially

                                dic = {'job_id': rec.job_id,
                                       'cost_id': rec.cost_id,
                                       'product_id': rec.product,
                                       'vendor': rec.vendor,
                                       'job_cost_line': rec.job_cost_line_id,
                                       'actual_qty': rec.remain_partial_qty,
                                       # 'actual_qty': rec.qty_actually - move.reserved_availability,
                                       'planned_qty': rec.planned_qty,
                                       'price_unit': 0.00, 'procurement_line_id': rec.id,
                                       'account_analytic_id': rec.procurment_id.analytic_account_id.id,
                                       'type_send_line': rec.type_send_line
                                       }
                                li.append(dic)
                    rec.qty_actually += rec.remain_partial_qty
                    rec.remain_partial_qty = 0.0


                elif rec.send_to_po and rec.action_line == 4 and rec.remain_partial_qty != 0 or not rec.moved:
                    for move in stock_moves.search([('procurement_line_id', '=', rec.id)], order='date desc',
                                                   limit=1):
                        if move.picking_id.state in ['confirmed', 'assigned']:
                            if (
                                    move.reserved_availability < move.product_uom_qty and move.reserved_availability != 0) or (
                                    move.reserved_availability == 0 and move.quantity_done == 0):
                                dic = {'job_id': rec.job_id,
                                       'cost_id': rec.cost_id,
                                       'product_id': rec.product,
                                       'vendor': rec.vendor,
                                       'job_cost_line': rec.job_cost_line_id,
                                       'actual_qty': rec.remain_partial_qty,
                                       'partial_qty': rec.partial_qty,
                                       # 'actual_qty': pro_line.qty_actually - move.reserved_availability,
                                       'planned_qty': rec.planned_qty,
                                       'price_unit': 0.00, 'procurement_line_id': rec.id,
                                       'account_analytic_id': rec.procurment_id.analytic_account_id.id,
                                       'type_send_line': rec.type_send_line}
                                li.append(dic)
                rec.qty_actually += rec.remain_partial_qty
                rec.remain_partial_qty = 0.0
                # rec.moved = False

        # ADD by omnya ###################
        for sub_rec in self.sub_procurement_lines:
            if sub_rec.send_to_po:
                if not sub_rec.vendor.id:
                    raise UserError('Any PO order you must have a vendor')
                elif sub_rec.action_line == 0:
                    sub_rec.action_line = 2
                    for rec in self.procurment_lines:
                        if rec.action_line == 2 and rec.send_to_po:
                            dic = {'job_id': rec.job_id,
                                   'cost_id': rec.cost_id,
                                   'product_id': sub_rec.product,
                                   'vendor': rec.vendor or sub_rec.vendor,
                                   'job_cost_line': rec.job_cost_line_id,
                                   'actual_qty': sub_rec.qty_actually,
                                   # 'actual_qty': sub_rec.qty_actually - sub_rec.partial_qty,
                                   'planned_qty': sub_rec.planned_qty,
                                   'price_unit': 0.00,
                                   }
                            li.append(dic)
        ################################################################
        jobs_ids = set(x['job_id'] for x in li)
        vendor_ids = set(x['vendor'] for x in li)
        for j in jobs_ids:
            for v in vendor_ids:
                if v.id:
                    temp = False
                    for rec in li:
                        if (j.id == rec['job_id'].id) and (v.id == rec['vendor'].id):
                            temp = True
                    if temp:
                    # get type per line
                        if rec['type_send_line'] == 'C':
                            origin = "Procurement-C"
                        elif rec['type_send_line'] == 'M':
                            origin = "Procurement-M"
                        elif rec['type_send_line'] == 'E':
                            origin = "Procurement-E"
                        else:
                            origin = False
                        dic = {'partner_id': v.id, 
                            'type_po': rec['type_send_line'], 
                            'p_project_id': self.name.id,
                            'job_order_id': j.id,
                            'project_no': self.project_no, 'project_start_date': self.start_date,
                            'project_end_date': self.end_date,
                            'project_period': self.name.project_period,
                            'origin': origin,
                            'currency_id': self.env.user.company_id.currency_id.id,
                            'date_order': fields.Date.today(),
                            'company_id': self.env.user.company_id.id,
                            }
                        pl = self.env['purchase.order']
                        pl = pl.create(dic)
                        ins = []
                        for rec in li:
                            if (j.id == rec['job_id'].id) and (v.id == rec['vendor'].id):
                                qty = 0
                                if rec['procurement_line_id']:
                                    for move_line in stock_moves.search(
                                            [('procurement_line_id', '=', rec['procurement_line_id'])], order='date desc',
                                            limit=1):
                                        if move_line.picking_id.state in ['confirmed', 'assigned']:
                                            if (
                                                    move_line.reserved_availability < move_line.product_uom_qty and move_line.reserved_availability != 0 and move_line.quantity_done != move_line.product_uom_qty) or (
                                                    move_line.reserved_availability == 0 and move_line.quantity_done == 0):

                                                    qty = move_line.product_uom_qty - move_line.reserved_availability
                                            else:
                                                qty = move_line.product_uom_qty
                                else:
                                    qty = rec['actual_qty']
                                dic = {
                                    'job_cost_line_id': rec['job_cost_line'].id,
                                    'product_id': rec['product_id'].id,
                                    'job_cost_id': rec['cost_id'].id,
                                    'date_planned': datetime.now(),
                                    'name': rec['product_id'].name,
                                    # 'validate_price': rec['price_unit'],
                                    # 'validate_qty': rec['actual_qty'] if rec['actual_qty'] != 0.00 else rec[
                                    #     'planned_qty'],
                                    'product_qty': qty,
                                    'product_uom': rec['product_id'].uom_id.id,
                                    'price_unit': rec['product_id'].lst_price,
                                    # 'taxes_id': [rec['product_id'].taxes_id.id],
                                    'order_id': pl.id,
                                    'account_analytic_id': rec['account_analytic_id'],
                                    'procurement_line_id': rec['procurement_line_id']
                                }
                                pll = self.env['purchase.order.line']
                                pll.create(dic)
                                ins.append(dic)


class ProcurementListtLines(models.Model):
    _name = 'procurment.list.lines'
    _description = 'Procurement List Lines'

    job_id = fields.Many2one('project.task')
    cost_id = fields.Many2one('job.costing')
    job_cost_line_id = fields.Many2one('job.cost.line')
    project_id = fields.Many2one('project.project')

    name = fields.Char(string='work item')
    work_item_code = fields.Char(string='work item code')
    item_type = fields.Selection([('view', 'view'), ('transaction', 'transaction')], string='Type')
    product_code = fields.Char(string='Reference')
    product = fields.Many2one('product.product', string='product')
    vendor = fields.Many2one('res.partner', string='vendor')
    code = fields.Selection(
        [('a', 'Approved as submitted'), ('b', 'Approved with comments'), ('c', 'Revised and Re submitial required'),
         ('d', 'Disapproved see attached sheet'), ('e', 'Under Preview'), ('p', 'Pending')], string='code', default='e')
    send_to_pr = fields.Boolean(string='PR')
    send_to_po = fields.Boolean(string='PO')
    procurment_id = fields.Many2one('procurment.list', string='Procurment ID')
    action_line = fields.Integer(string='active', default=0,
                                 invisible=1)  # 0 -->> no action 1 -->>send to pr  2-->send to po
    planned_qty = fields.Float(string='Planned Qty')
    cost_price = fields.Float(string='Cost/Price', invisible=True)
    uom_id = fields.Many2one('uom.uom', string='Uom')
    qty_actually = fields.Float(string='Actual Qty')
    submitted_date = fields.Date(string='Submission Date')
    returned_date = fields.Date(string='Return Date')
    note = fields.Text(string='Note')
    doc_count = fields.Integer(compute='_compute_count_of_attachemnt')
    sub_procurement_id = fields.Many2one('procurment.list')
    parent_product = fields.Many2one('product.product', string='Parent Product')
    job_type_id = fields.Many2one(comodel_name="job.type", string="Job Type", required=False)
    moved = fields.Boolean()
    partial_qty = fields.Float(string='Residual Qty', compute='compute_partial_qty')
    remain_partial_qty = fields.Float(string='Ordered Qty')
    taken_partial_qty = fields.Float(string='TK Partial Qty')
    type_send_line = fields.Selection([
        ('C', 'Civil'), ('M', 'Mechanics'), ('E', 'Electricity')],
        string='Type', tracking=True)

    @api.depends('planned_qty', 'qty_actually')
    def compute_partial_qty(self):
        for item in self:
            # item.taken_partial_qty += item.remain_partial_qty
            item.partial_qty = 0
            item.partial_qty = item.planned_qty - item.qty_actually
            # if item.remain_partial_qty != 0:
            #     item.partial_qty = item.taken_partial_qty

    # @api.depends('remain_partial_qty')
    # def compute_actual_qty(self):
    #     print ('eeee')
    #     for item in self:
    #         item.qty_actually += item.remain_partial_qty

    @api.onchange('product', 'parent_product', 'planned_qty')
    def filter_parent_product(self):
        for rec in self:
            if len(rec.sub_procurement_id.name.project_tender_ids.mapped('related_product')) > 0:
                selected_products = rec.sub_procurement_id.name.project_tender_ids.mapped('related_product.id')
                return {'domain': {'parent_product': [('id', 'in', selected_products)]}}

    @api.onchange('product', 'parent_product', 'planned_qty')
    def filter_product(self):
        for rec in self:
            selected_products = rec.sub_procurement_id.name.project_tender_ids.job_cost_id.job_cost_line_ids.mapped(
                'product_id.id') + rec.sub_procurement_id.name.project_tender_ids.job_cost_id.subcontractor_line_ids.mapped(
                'product_id.id') + rec.sub_procurement_id.name.project_tender_ids.job_cost_id.job_labour_line_ids.mapped(
                'product_id.id') + rec.sub_procurement_id.name.project_tender_ids.job_cost_id.equipment_line_ids.mapped(
                'product_id.id') + rec.sub_procurement_id.name.project_tender_ids.job_cost_id.job_overhead_line_ids.mapped(
                'product_id.id') + rec.sub_procurement_id.name.project_tender_ids.job_cost_id.other_line_ids.mapped(
                'product_id.id')
            return {'domain': {'product': [('id', 'in', selected_products)]}}

    def _compute_count_of_attachemnt(self):
        for d in self:
            if d.id:
                d.doc_count = self.env['procurment.list.lines.attachment'].search_count(
                    [('procurment_line_ref.id', '=', d.id)])
            else:
                d.doc_count = 0

    def attachment_view(self):
        self.ensure_one()
        domain = [
            ('procurment_line_ref', '=', self.id)]
        return {
            'name': 'Attachments',
            'domain': domain,
            'res_model': 'procurment.list.lines.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_procurment_line_ref': '%s'}" % self.id
        }

    def create_submittal(self):
        for line in self:
            dc_lines = []
            document_control = self.env['document.control']
            if line.product:
                if not line.is_submittaled:
                    dc_lines.append((0, 0, {
                        'product_id': line.product.id,
                        'code': 'e',
                        'description': line.product.name,
                        'categ_id': line.product.categ_id.id,
                        'procurement_list_sample_line': line.id,
                    }))

                    document_control.sudo().create({
                        'projectID': line.sub_procurement_id.project_no if line.sub_procurement_id else line.procurment_id.project_no,
                        'project_id': line.sub_procurement_id.name.id if line.sub_procurement_id else line.procurment_id.name.id,
                        'client_id': line.sub_procurement_id.partner_id.id if line.sub_procurement_id else line.procurment_id.partner_id.id,
                        'client_specialist_id': line.sub_procurement_id.client_specialist_id.id if line.sub_procurement_id else line.procurment_id.client_specialist_id.id,
                        'consultant': line.sub_procurement_id.consultant.id if line.sub_procurement_id else line.procurment_id.consultant.id,
                        'attention': 'Tender Department',
                        'prepared_by_id': self.env.user.id,
                        'description': '',
                        'remarks': '',
                        'submittal_type': line.submittal_type,
                        'scope_of_work_id': line.scope_of_work_id.id,
                        'division': line.division.id,
                        'submission_date': date.today(),
                        'specifications': '',
                        'procurment_list_id': line.sub_procurement_id.id if line.sub_procurement_id else line.procurment_id.id,
                        'dc_line_ids': dc_lines,
                    })
                    line.is_submittaled = True
                    line.code = 'p'

    @api.onchange('code')
    def change_code(self):
        if self.code == 'c' or self.code == 'd':
            self.send_to_pr = False
            self.send_to_po = False

    @api.onchange('send_to_po')
    def change_code_po(self):
        # self.send_to_po = not(self.send_to_po)
        if self.send_to_po:
            self.send_to_pr = False

    @api.onchange('send_to_pr')
    def change_code_pr(self):
        # self.send_to_pr = not(self.send_to_pr)
        if self.send_to_pr:
            self.send_to_po = False


class CustomPrTree(models.Model):
    _inherit = 'material.purchase.requisition.line'

    cost_id = fields.Many2one('job.costing', string='job cost center')
    job_cost_line_id = fields.Many2one('job.cost.line', string='job cost line')


class CustomPr(models.Model):
    _inherit = 'material.purchase.requisition'

    type_pr = fields.Selection([
        ('C', 'Civil'), ('M', 'Mechanics'), ('E', 'Electricity')],
        string='Type',
        required=1,
    )


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    type_po = fields.Selection([
        ('C', 'Civil'), ('M', 'Mechanics'), ('E', 'Electricity')],
        string='Type',
    )

    validate_done = fields.Boolean(string='Validate', invisible=1, default=False)

    def validate_product(self):
        for order in self:
            # for product in order.order_line:
            #     if product.product_qty > product.validate_qty:
            #         raise UserError('Product ' + str(product.product_id.name) + 'Not valid')
            #         return False
            order.write({'validate_done': True, 'state': 'dep_approved'})

        return True
    


    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        thread_pool = self.env['mail.thread']
        partners = []
        for user in self.env.ref('procurment_list_project.group_control_po_validate').users:
            partners.append(user.partner_id.id)
        for user in self.env.ref('procurment_list_project.group_control_po_validate_type_c').users:
            partners.append(user.partner_id.id)
        for user in self.env.ref('procurment_list_project.group_control_po_validate_type_e').users:
            partners.append(user.partner_id.id)
        for user in self.env.ref('procurment_list_project.group_control_po_validate_type_m').users:
            partners.append(user.partner_id.id)
        for rec in self.order_line:
            if rec.product_qty > rec.validate_qty:  # or rec.price_unit > rec.validate_price:
                if False not in partners:
                    thread_pool.message_notify(
                        partner_ids=partners,
                        subject="PO Control Cost Notification",
                        body='This PO has order lines not valid: <a target=_BLANK href="/web?#id=' + str(
                            self.id) + '&view_type=form&model=purchase.order&action=" style="font-weight: bold">' + str(
                            self.name) + '</a>',
                        email_from=self.env.user.company_id.email, )
                        # self.env.user.company_id.catchall or
        return res


    def button_cancel(self):
        self.write({'validate_done': False})
        
        return super(PurchaseOrder, self).button_cancel()


class CustomPrLine(models.Model):
    _inherit = 'purchase.order.line'

    validate_qty = fields.Float(string='validate Qty')
    # validate_price = fields.Float(string='validate price')


class ProcurmentListLinesAttachment(models.Model):
    _name = 'procurment.list.lines.attachment'

    name = fields.Char(string='Document Number', required=1)
    procurment_line_ref = fields.Many2one('procurment.list.lines', invisible=1)
    doc_attachment_id = fields.Many2many('ir.attachment', 'procurment_attachment_ref', 'doc_id', 'attach_id3',
                                         string="Attachment")
    description = fields.Text('Description')


class ProcurmentListAttachment(models.Model):
    _inherit = 'ir.attachment'

    procurment_attachment_ref = fields.Many2many('hr.employee.document', 'doc_attachment_id', 'attach_id3', 'doc_id',
                                                 string="Attachment",
                                                 invisible=1)


class AccountMove(models.Model):
    _inherit = 'account.move'

    type_bill = fields.Selection([
        ('C', 'Civil'), ('M', 'Mechanics'), ('E', 'Electricity')],
        string='Type',
        invisible=1,
    )


    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        if res.move_type == 'in_invoice':
            project_no = self.env['project.project'].search([('id', '=', res.contract_project_id.id)])
            if res.is_contract_invoice:
                inv_type = self.env['owner.contract'].search([('id', '=', res.contract_id.id)])
                if inv_type['subcontractor_type'] == 'civil':
                    res.type_bill = 'C'
                elif inv_type['subcontractor_type'] == 'electricity':

                    res.type_bill = 'E'
                elif inv_type['subcontractor_type'] == 'mechanics':
                    res.type_bill = 'M'

            if res.type_bill == 'C':
                X = self.env['ir.sequence'].next_by_code('account.move.seq.c')
                res.name = str(datetime.now().year) + '-' + str(project_no['project_no']) + '-' + 'C' + '-' + str(X)
                res.ref = "Contract-Type-C"

            elif res.type_bill == 'E':
                X = self.env['ir.sequence'].next_by_code('account.move.seq.e')
                res.name = str(datetime.now().year) + '-' + str(project_no['project_no']) + '-' + 'E' + '-' + str(X)
                res.ref = "Contract-Type-E"

            elif res.type_bill == 'M':
                X = self.env['ir.sequence'].next_by_code('account.move.seq.m')
                res.name = str(datetime.now().year) + '-' + str(project_no['project_no']) + '-' + 'M' + '-' + str(X)
                res.ref = "Contract-Type-M"

            else:
                res.name = 'BILL/' + str(datetime.now().year) + '/' + self.env['ir.sequence'].next_by_code(
                    'account.move.seq')

        return res


class Locations(models.Model):
    _inherit = 'stock.location'

    is_default = fields.Boolean(string="Default Location?", )


class StockMove(models.Model):
    _inherit = 'stock.move'

    cost_id = fields.Many2one('job.costing', string='job cost center')
    job_cost_line_id = fields.Many2one('job.cost.line', string='job cost line')