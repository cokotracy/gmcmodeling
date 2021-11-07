from openerp import SUPERUSER_ID, api, models

class stock_picking(models.Model):
    _inherit = "stock.picking"
    
    
    def do_new_transfer(self):
        for pick in self:
            purchase_order_obj = self.env['purchase.order'].search([('name','ilike',pick.origin)])
            if purchase_order_obj.letter_of_credit:
                purchase_order_obj.letter_of_credit.write({'state': 'done'})
        
        return super(stock_picking, self).do_new_transfer()