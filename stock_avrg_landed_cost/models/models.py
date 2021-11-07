from odoo import api, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def get_valuation_lines(self):

        lines = []

        for move in self.mapped('picking_ids').mapped('move_lines'):
            if move.product_id.valuation != 'real_time' or move.product_id.cost_method not in ('fifo', 'average'):
                continue
            vals = {
                'product_id': move.product_id.id,
                'move_id': move.id,
                'quantity': move.product_qty,
                'former_cost': sum(move.stock_valuation_layer_ids.mapped('value')),
                'weight': move.product_id.weight * move.product_qty,
                'volume': move.product_id.volume * move.product_qty
            }
            lines.append(vals)

        # if not lines and self.mapped('picking_ids'):
        #     # raise UserError(_('The selected picking does not contain any move that would be impacted by landed costs. Landed costs are only possible for products configured in real time valuation with real price costing method. Please make sure it is the case, or you selected the correct picking'))
        return lines

    def button_validate(self):
        if any(cost.state != 'draft' for cost in self):
            raise UserError(_('Only draft landed costs can be validated'))
        if any(not cost.valuation_adjustment_lines for cost in self):
            raise UserError(_('No valuation adjustments lines. You should maybe recompute the landed costs.'))
        if not self._check_sum():
            raise UserError(_('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))

        for cost in self:
            move = self.env['account.move']
            move_vals = {
                'journal_id': cost.account_journal_id.id,
                'date': cost.date,
                'ref': cost.name,
                'line_ids': [],
            }
            valuation_layer_ids = []
            for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
                remaining_qty = sum(line.move_id.stock_valuation_layer_ids.mapped('remaining_qty'))
                #todo
                # remaining_value = sum(line.move_id.stock_valuation_layer_ids.mapped('remaining_value'))
                # landed_cost_value = sum(line.move_id.stock_valuation_layer_ids.mapped('unit_cost'))
                _logger.warn('(remaining_qty / line.move_id.product_qty) * line.additional_landed_cost')
                _logger.warn('(%s / %s) * %s' % (remaining_qty, line.move_id.product_qty, line.additional_landed_cost))
                linked_layer = line.move_id.stock_valuation_layer_ids[:1]

                if self.accrual_reconcile == True:
                    cost_to_add = (remaining_qty / line.move_id.product_qty) * line.final_cost - line.former_cost
                else:
                    cost_to_add = (remaining_qty / line.move_id.product_qty) * line.additional_landed_cost


                valuation_layer = self.env['stock.valuation.layer'].create({
                    'value': cost_to_add,
                    'unit_cost': 0,
                    'quantity': 0,
                    'remaining_qty': 0,
                    'stock_valuation_layer_id': linked_layer.id,
                    'description': cost.name,
                    'stock_move_id': line.move_id.id,
                    'product_id': line.move_id.product_id.id,
                    'stock_landed_cost_id': cost.id,
                    'company_id': cost.company_id.id,
                })
                linked_layer.remaining_value += cost_to_add
                valuation_layer_ids.append(valuation_layer.id)
                qty_out = 0
                if line.move_id._is_in():
                    qty_out = line.move_id.product_qty - remaining_qty
                elif line.move_id._is_out():
                    qty_out = line.move_id.product_qty
                move_vals['line_ids'] += line._create_accounting_entries(move, qty_out)

                if line.product_id.cost_method == 'average':
                    quant_locs = self.env['stock.quant'].sudo().read_group([('product_id', '=', line.product_id.id)],
                                                                           ['location_id'], ['location_id'])
                    quant_loc_ids = [loc['location_id'][0] for loc in quant_locs]
                    locations = self.env['stock.location'].search(
                        [('usage', '=', 'internal'), ('company_id', '=', self.env.user.company_id.id),
                         ('id', 'in', quant_loc_ids)])
                    qty_available = line.product_id.with_context(location=locations.ids).qty_available
                    total_cost = (qty_available * line.product_id.standard_price) + cost_to_add
                    line.product_id.write({'standard_price': total_cost / qty_available})

            move = move.create(move_vals)
            cost.write({'state': 'done', 'account_move_id': move.id})
            move.post()
            self.ogcs_validaion()
        return True