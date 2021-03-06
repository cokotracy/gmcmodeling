# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MaterialPlanning(models.Model):
    _name = 'material.plan'
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.description = self.product_id.name
    
    product_id = fields.Many2one(
        'product.product',
        string='Product'
    )
    description = fields.Char(
        string='Description'
    )
    product_uom_qty = fields.Integer(
        'Quantity',
        default=1.0
    )
    product_uom = fields.Many2one(
        'uom.uom',#product.uom
        'Unit of Measure'
    )
    material_task_id = fields.Many2one(
        'project.task',
        'Material Plan Task'
    )

class ConsumedMaterial(models.Model):
    _name = 'consumed.material'
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.description = self.product_id.name
            
    
    product_id = fields.Many2one(
        'product.product',
        string='Product'
    )
    description = fields.Char(
        string='Description'
    )
    product_uom_qty = fields.Integer(
        'Quantity',
        default=1.0
    )
    product_uom = fields.Many2one(
        'uom.uom',#product.uom
        'Unit of Measure'
    )
    consumed_task_material_id = fields.Many2one(
        'project.task',
        string='Consumed Material Plan Task'
    )

# add by mokhlef
class KeyPersonnelTask(models.Model):
    _name = 'key.personnel.task'

    position_id = fields.Many2one(comodel_name="hr.job", string="Position", required=False, )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee Name", required=False, )
    mobile = fields.Char(string="Mobile", required=False, )
    email_id = fields.Char(string="Email ID", required=False, )
    task_id = fields.Many2one(comodel_name="project.task", string="", required=False, )

# //////////////////////////////////////////////////////////////////////

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    @api.depends('picking_ids.requisition_line_ids')
    def _compute_stock_picking_moves(self):
        for rec in self:
            rec.ensure_one()
            for picking in rec.picking_ids:
                rec.move_ids = picking.requisition_line_ids.ids
    
    def total_stock_moves_count(self):
        for task in self:
            task.stock_moves_count = len(task.move_ids)
    
    def _compute_notes_count(self):
        for task in self:
            task.notes_count = len(task.notes_ids)

    # add by mokhlef
    job_order_no = fields.Char(string="Job Order No", required=False, )
    project_ID = fields.Char(string="Project ID", required=False, )
    client_name = fields.Char(string="Client Name", required=False, )
    client_manager = fields.Char(string="Client Manager", required=False, )
    entry_date = fields.Datetime(string="Entry Date", required=False, default=fields.Datetime.now)
    location = fields.Char(string="Location", required=False, )
    po_number = fields.Char(string="PO Number", required=False, )
    po_date = fields.Datetime(string="Po Date", required=False, default=fields.Datetime.now)
    start_date = fields.Date(string="Start Date", required=False, default=fields.Date.context_today)
    hand_over_date = fields.Date(string="Hand Over Date", required=False, default=fields.Date.context_today)
    remarks = fields.Text(string="Remarks", required=False, )
    key_personnel_ids = fields.One2many(comodel_name="key.personnel.task", inverse_name="task_id", string="",
                                        required=False, )

# ////////////////////////////////////////////////////////////////////////////

    picking_ids = fields.One2many(
        'material.purchase.requisition',
        'task_id',
        string='Stock Pickings'
    )
    move_ids = fields.Many2many(
        'material.purchase.requisition.line',
        compute='_compute_stock_picking_moves',
        store=True,
    )
    material_plan_ids = fields.One2many(
        'material.plan',
        'material_task_id',
        string='Material Plannings'
    )
    consumed_material_ids = fields.One2many(
        'consumed.material',
        'consumed_task_material_id',
        string='Consumed Materials'
    )
    stock_moves_count = fields.Integer(
        compute='total_stock_moves_count', 
        string='# of Stock Moves',
        store=True,
    )
    parent_task_id = fields.Many2one(
        'project.task', 
        string='Parent Task', 
        readonly=True
    )
    child_task_ids = fields.One2many(
        'project.task', 
        'parent_task_id', 
        string='Child Tasks'
    )
    notes_ids = fields.One2many(
        'note.note', 
        'task_id', 
        string='Notes',
    )
    notes_count = fields.Integer(
        compute='_compute_notes_count', 
        string="Notes"
    )
    job_number = fields.Char(
        string = "Job Number",
        copy = False,
    )
    
    @api.model
    def create(self,vals):
        number = self.env['ir.sequence'].next_by_code('project.task')
        vals.update({
            'job_number': number,
        })
        return super(ProjectTask, self).create(vals) 
    
    def view_stock_moves(self):
        for rec in self:
            stock_move_list = []
            for move in rec.move_ids:
                #stock_move_list.append(move.id)
                stock_move_list += move.requisition_id.delivery_picking_id.move_lines.ids
        result = self.env.ref('stock.stock_move_action')
        action_ref = result or False
        result = action_ref.read()[0]
        result['domain'] = str([('id', 'in', stock_move_list)])
        return result
        
    def view_notes(self):
        for rec in self:
            res = self.env.ref('odoo_job_costing_management.action_task_note_note')
            res = res.read()[0]
            res['domain'] = str([('task_id','in',rec.ids)])
        return res
