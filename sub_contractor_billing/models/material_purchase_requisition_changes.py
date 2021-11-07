from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError


class MaterialPurchaseRequisition(models.Model):
    _inherit = 'material.purchase.requisition'


    procurement_id = fields.Many2one('procurment.list', String='Procurement List')

    @api.model
    def _prepare_pick_vals(self, line=False, stock_id=False):
        pick_vals = super(MaterialPurchaseRequisition, self)._prepare_pick_vals(line=line, stock_id=stock_id)
        if line and line.cost_id:
            pick_vals.update({'cost_id': line.cost_id.id})
        if line and line.job_cost_line_id:
            pick_vals.update({'job_cost_line_id': line.job_cost_line_id.id})

    @api.model
    def _prepare_po_line(self, line=False, purchase_order=False):
        stock_moves = self.env['stock.move']
        qty = 0
        if line.procurement_line_id:
            for move in stock_moves.search([('procurement_line_id', '=', line.procurement_line_id.id)]):
                if move.picking_id.state in ['confirmed', 'assigned']:
                    if (move.reserved_availability < move.product_uom_qty and move.reserved_availability != 0) or (move.reserved_availability == 0 and move.quantity_done == 0):
                        qty = move.product_uom_qty - move.reserved_availability
                    else:
                        qty = move.product_uom_qty

        else:
            qty = line.qty

        po_line_vals = {
            'product_id': line.product_id.id,
            'name': line.product_id.name,
            'product_qty': qty,
            'product_uom': line.uom.id,
            'date_planned': fields.Date.today(),
            'price_unit': line.product_id.lst_price,
            'order_id': purchase_order.id,
            'account_analytic_id': self.analytic_account_id.id,
            'job_cost_id': line.cost_id and line.cost_id.id,
            'job_cost_line_id': line.job_cost_line_id and line.job_cost_line_id.id,
            # 'custom_requisition_line_id': line.id,
        }
        return po_line_vals

    # def request_stock(self):
    #     print ('calllinggg')
    #     stock_obj = self.env['stock.picking']
    #     move_obj = self.env['stock.move']
    #     internal_obj = self.env['stock.picking.type'].search([('code','=', 'internal')], limit=1)
    #     internal_stock_obj = self.env['stock.location'].search([('usage','=', 'internal'),('is_default', '=', True)], limit=1)
    #     purchase_obj = self.env['purchase.order']
    #     purchase_line_obj = self.env['purchase.order.line']
    #     line_obj = []
    #     #         if not internal_obj:
    #     #             raise UserError(_('Please Specified Internal Picking Type.'))
    #     for rec in self:
    #         if not rec.requisition_line_ids:
    #             raise Warning(_('Please create some requisition lines.'))
    #         # if any(line.requisition_type == 'internal' for line in rec.requisition_line_ids):
    #             # if not rec.location_id.id:
    #             #     raise Warning(_('Select Source location under the picking details.'))
    #             # if not rec.custom_picking_type_id.id:
    #             #     raise Warning(_('Select Picking Type under the picking details.'))
    #             # if not rec.dest_location_id:
    #             #     raise Warning(_('Select Destination location under the picking details.'))
    #             #                 if not rec.employee_id.dest_location_id.id or not rec.employee_id.department_id.dest_location_id.id:
    #             #                     raise Warning(_('Select Destination location under the picking details.'))
                
    #         if internal_stock_obj:
    #             print ('internal_objinternal_obj', internal_obj)
    #             picking_vals = {
    #                     'partner_id' : rec.employee_id.address_home_id.id,
    #                     # 'min_date' : fields.Date.today(),
    #                     'location_id' : internal_stock_obj.id,
    #                     'location_dest_id' : rec.project_id.stock_location_id and rec.project_id.stock_location_id.id or rec.employee_id.dest_location_id.id or rec.employee_id.department_id.dest_location_id.id,
    #                     'picking_type_id' : internal_obj.id,
    #                     'note' : rec.reason,
    #                     'custom_requisition_id' : rec.id,
    #                     'origin' : rec.name,
    #                 }
    #             print ('internal_obj', picking_vals)
    #             stock_id = stock_obj.sudo().create(picking_vals)
    #             print (stock_id)
    #             delivery_vals = {
    #                     'delivery_picking_id' : stock_id.id,
    #                 }
    #             rec.write(delivery_vals)

    #         po_dict = {}
    #         for line in rec.requisition_line_ids:
    #             # if line.requisition_type == 'internal':
    #                 # pick_vals = rec._prepare_pick_vals(line, stock_id)
    #                 # move_id = move_obj.sudo().create(pick_vals)
    #             # else:
    #                 qty = 0
    #                 all_from_default = False
    #                 remaining_qty = 0
    #                 if internal_stock_obj:
    #                     quant = self.env['stock.quant'].search([('product_id', '=', line.product_id.id), ('location_id', '=', internal_stock_obj.id)])
    #                     if quant and quant.reserved_quantity > 0:
    #                         if quant.reserved_quantity > line.qty:
    #                             all_from_default = True
    #                             qty = line.qty
    #                             remaining_qty = 0
    #                         else:
    #                             qty = quant.reserved_quantity
    #                             remaining_qty = line.qty - qty
    #                         pick_vals = {
    #                             'product_id' : line.product_id.id,
    #                             'product_uom_qty' : qty,
    #                             'product_uom' : line.uom.id,
    #                             'location_id' : internal_stock_obj.id,
    #                             'location_dest_id' : rec.project_id.stock_location_id and rec.project_id.stock_location_id.id,
    #                             'name' : line.product_id.name,
    #                             'picking_id' : stock_id.id,
    #                         }
    #                         move_id = move_obj.sudo().create(pick_vals)
    #                     else:
    #                         remaining_qty = line.qty
    #                 else:
    #                     remaining_qty = line.qty
    #                 if not line.partner_id:
    #                     raise Warning(_('PLease Enter Atleast One Vendor on Requisition Lines'))
    #                 for partner in line.partner_id:
    #                     if partner not in po_dict:
    #                         po_vals = {
    #                             'partner_id': partner.id,
    #                             'currency_id': rec.env.user.company_id.currency_id.id,
    #                             'date_order': fields.Date.today(),
    #                             'company_id': rec.env.user.company_id.id,
    #                             'custom_requisition_id': rec.id,
    #                             'origin': rec.name,
    #                             'p_project_id': rec.project_id.id,
    #                             'project_no': rec.project_id.project_no,
    #                             'project_start_date': rec.project_id.project_start_date,
    #                             'project_end_date': rec.project_id.project_end_date,
    #                             'project_period': rec.project_id.project_period,
    #                             'job_order_id': rec.task_id.id,
    #                             'type_po': rec.type_pr,
    #                         }
    #                         purchase_order = purchase_obj.create(po_vals)
    #                         po_dict.update({partner: purchase_order})
    #                         po_line_vals = rec._prepare_po_line(line, purchase_order, remaining_qty)
    #                         #                            {
    #                         #                                     'product_id': line.product_id.id,
    #                         #                                     'name':line.product_id.name,
    #                         #                                     'product_qty': line.qty,
    #                         #                                     'product_uom': line.uom.id,
    #                         #                                     'date_planned': fields.Date.today(),
    #                         #                                     'price_unit': line.product_id.lst_price,
    #                         #                                     'order_id': purchase_order.id,
    #                         #                                     'account_analytic_id': rec.analytic_account_id.id,
    #                         #                            }
    #                         purchase_line_obj.sudo().create(po_line_vals)
    #                     else:
    #                         purchase_order = po_dict.get(partner)
    #                         po_line_vals = rec._prepare_po_line(line, purchase_order, remaining_qty)
    #                         #                            po_line_vals =  {
    #                         #                                 'product_id': line.product_id.id,
    #                         #                                 'name':line.product_id.name,
    #                         #                                 'product_qty': line.qty,
    #                         #                                 'product_uom': line.uom.id,
    #                         #                                 'date_planned': fields.Date.today(),
    #                         #                                 'price_unit': line.product_id.lst_price,
    #                         #                                 'order_id': purchase_order.id,
    #                         #                                 'account_analytic_id': rec.analytic_account_id.id,
    #                         #                            }
    #                         purchase_line_obj.sudo().create(po_line_vals)
    #                 rec.state = 'stock'

    def request_stock(self):
        stock_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        # internal_obj = self.env['stock.picking.type'].search([('code','=', 'internal')], limit=1)
        # internal_obj = self.env['stock.location'].search([('usage','=', 'internal')], limit=1)
        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']
        #         if not internal_obj:
        #             raise UserError(_('Please Specified Internal Picking Type.'))
        for rec in self:
            if not rec.requisition_line_ids:
                raise Warning(_('Please create some requisition lines.'))
            if any(line.requisition_type == 'internal' for line in rec.requisition_line_ids):
                if not rec.location_id.id:
                    raise Warning(_('Select Source location under the picking details.'))
                if not rec.custom_picking_type_id.id:
                    raise Warning(_('Select Picking Type under the picking details.'))
                if not rec.dest_location_id:
                    raise Warning(_('Select Destination location under the picking details.'))
                #                 if not rec.employee_id.dest_location_id.id or not rec.employee_id.department_id.dest_location_id.id:
                #                     raise Warning(_('Select Destination location under the picking details.'))
                picking_vals = {
                    'partner_id': rec.employee_id.address_home_id.id,
                    # 'min_date' : fields.Date.today(),
                    'location_id': rec.location_id.id,
                    'location_dest_id': rec.dest_location_id and rec.dest_location_id.id or rec.employee_id.dest_location_id.id or rec.employee_id.department_id.dest_location_id.id,
                    'picking_type_id': rec.custom_picking_type_id.id,  # internal_obj.id,
                    'note': rec.reason,
                    'custom_requisition_id': rec.id,
                    'origin': rec.name,
                }
                stock_id = stock_obj.sudo().create(picking_vals)
                delivery_vals = {
                    'delivery_picking_id': stock_id.id,
                }
                rec.write(delivery_vals)

            po_dict = {}
            for line in rec.requisition_line_ids:
                if line.requisition_type == 'internal':
                    pick_vals = rec._prepare_pick_vals(line, stock_id)
                    move_id = move_obj.sudo().create(pick_vals)
                else:
                    
                    if not line.partner_id:
                        raise Warning(_('PLease Enter Atleast One Vendor on Requisition Lines'))
                    for partner in line.partner_id:
                        if partner not in po_dict:
                            po_vals = {
                                'partner_id': partner.id,
                                'currency_id': rec.env.user.company_id.currency_id.id,
                                'date_order': fields.Date.today(),
                                'company_id': rec.env.user.company_id.id,
                                'custom_requisition_id': rec.id,
                                'origin': rec.name,
                                'p_project_id': rec.project_id.id,
                                'project_no': rec.project_id.project_no,
                                'project_start_date': rec.project_id.project_start_date,
                                'project_end_date': rec.project_id.project_end_date,
                                'project_period': rec.project_id.project_period,
                                'job_order_id': rec.task_id.id,
                                'type_po': rec.type_pr,
                            }
                            purchase_order = purchase_obj.create(po_vals)
                            po_dict.update({partner: purchase_order})
                            po_line_vals = rec._prepare_po_line(line, purchase_order)
                            #                            {
                            #                                     'product_id': line.product_id.id,
                            #                                     'name':line.product_id.name,
                            #                                     'product_qty': line.qty,
                            #                                     'product_uom': line.uom.id,
                            #                                     'date_planned': fields.Date.today(),
                            #                                     'price_unit': line.product_id.lst_price,
                            #                                     'order_id': purchase_order.id,
                            #                                     'account_analytic_id': rec.analytic_account_id.id,
                            #                            }
                            purchase_line_obj.sudo().create(po_line_vals)
                        else:
                            purchase_order = po_dict.get(partner)
                            po_line_vals = rec._prepare_po_line(line, purchase_order)
                            #                            po_line_vals =  {
                            #                                 'product_id': line.product_id.id,
                            #                                 'name':line.product_id.name,
                            #                                 'product_qty': line.qty,
                            #                                 'product_uom': line.uom.id,
                            #                                 'date_planned': fields.Date.today(),
                            #                                 'price_unit': line.product_id.lst_price,
                            #                                 'order_id': purchase_order.id,
                            #                                 'account_analytic_id': rec.analytic_account_id.id,
                            #                            }
                            purchase_line_obj.sudo().create(po_line_vals)
                rec.state = 'stock'


class MaterialPurchaseRequisitionLine(models.Model):
    _inherit = "material.purchase.requisition.line"


    procurement_line_id = fields.Many2one('procurment.list.lines', String='Procurement List Line')