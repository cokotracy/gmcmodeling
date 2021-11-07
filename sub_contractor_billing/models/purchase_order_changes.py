from odoo import models, fields, api
from odoo.tools.float_utils import float_compare
from datetime import datetime, date


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    job_type = fields.Many2one(
        'job.type',
        string='Job Type')
    p_project_id = fields.Many2one('project.project', string='Project Name')
    project_no = fields.Char('Project No.')
    project_start_date = fields.Date(string='Project Beginning')
    project_end_date = fields.Date(sting='Project End')
    project_period = fields.Char(sting='Project Period')
    job_order_id = fields.Many2one(comodel_name="project.task", string="Task / Job Order", required=False, )

    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        if res.type_po == 'C':
            X = self.env['ir.sequence'].next_by_code('purchase.order.seq.c')
            res.name = 'PO' + str(datetime.now().year) + '-' + str(res.project_no) + '-' + str(res.type_po) + '-' + str(
                X)

        elif res.type_po == 'E':
            X = self.env['ir.sequence'].next_by_code('purchase.order.seq.e')
            res.name = 'PO' + str(datetime.now().year) + '-' + str(res.project_no) + '-' + str(res.type_po) + '-' + str(
                X)

        elif res.type_po == 'M':
            X = self.env['ir.sequence'].next_by_code('purchase.order.seq.m')
            res.name = 'PO' + str(datetime.now().year) + '-' + str(res.project_no) + '-' + str(res.type_po) + '-' + str(
                X)

        else:
            res.name = self.env['ir.sequence'].next_by_code('purchase.order.seq')

        if res.order_line:
            for line in res.order_line:
                if line.product_id.type == 'service':
                    if line.recently_done_update:
                        line.write(
                            {'qty_received': line.qty_received + line.recently_done_qty,
                             'recently_done_update': False})
        return res

    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        if vals.get('order_line'):
            for line in self.order_line:
                if line.product_id.type == 'service':
                    if line.recently_done_update:
                        line.write(
                            {'qty_received': line.qty_received + line.recently_done_qty,
                             'recently_done_update': False})
        return res


    def _prepare_invoice(self):
        self.ensure_one()
        result = super(PurchaseOrder, self)._prepare_invoice()
        if self.p_project_id:
            result.update({'project_name_id': self.p_project_id and self.p_project_id.id})
        return result
    # Override create bill buttons
    def action_view_invoice(self, invoices=False):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the purchase order, we read them in sudo to fill the
            # cache.
            self.sudo()._read(['invoice_ids'])
            invoices = self.invoice_ids
        result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'default_type': 'in_invoice',
            'default_company_id': self.company_id.id,
            'default_purchase_id': self.id,
            'default_partner_id': self.partner_id.id,
            ##ADDED BY Gold
            'default_type_bill': self.type_po,
            'default_contract_project_id': self.p_project_id.id,
        }
        self.sudo()._read(['invoice_ids'])
        # choose the view_mode accordingly
        if not create_bill:
            if len(invoices) > 1:
                result['domain'] = [('id', 'in', invoices.ids)]
            elif len(invoices) == 1:
                res = self.env.ref('account.view_move_form', False)
                form_view = [(res and res.id or False, 'form')]
                if 'views' in result:
                    result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
                else:
                    result['views'] = form_view
                result['res_id'] = invoices.id
            else:
                result = {'type': 'ir.actions.act_window_close'}
        else:
            if len(self.invoice_ids) > 1:
                result['domain'] = [('id', 'in', self.invoice_ids.ids)]
            else:
                res = self.env.ref('account.view_move_form', False)
                form_view = [(res and res.id or False, 'form')]
                if 'views' in result:
                    result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
                else:
                    result['views'] = form_view
                # Do not set an invoice_id if we want to create a new bill.
                result['res_id'] = self.invoice_ids.id or False
        result['context']['default_invoice_origin'] = self.name
        result['context']['default_ref'] = self.partner_ref
        if self.p_project_id:
            result['context']['default_project_name_id'] = self.p_project_id.id
        if self.job_type:
            result['context']['default_job_type_id'] = self.job_type.id
        if self.project_no:
            result['context']['default_project_no'] = self.project_no
        if self.project_start_date:
            result['context']['default_project_start_date'] = self.project_start_date
        if self.project_end_date:
            result['context']['default_project_end_date'] = self.project_end_date
        if self.project_period:
            result['context']['default_project_period'] = self.project_period
        if self.p_project_id.analytic_account_id:
            result['context']['default_project_id'] = self.p_project_id.analytic_account_id.id
        return result

    # def action_view_invoice(self):  11-10-2020
    #     """
    #     This function returns an action that display existing vendor bills of
    #     given purchase order ids. When only one found, show the vendor bill immediately.
    #     """

    #     # raise Warning(self.invoice_count)
    #     print('here')
    #     # action = self.env.ref('account.action_vendor_bill_template')
    #     action = self.env.ref('action_view_invoice')
    #     result = action.read()[0]
    #     create_bill = self.env.context.get('create_bill', False)
    #     # override the context to get rid of the default filtering

    #     last_invoice = self.env['account.invoice'].search([('origin', '=', self.name)],
    #                                                       order='id desc', limit=1)
    #     # raise Warning(last_invoice[self.invoice_count-1].id)
    #     result['context'] = {
    #         'type': 'in_invoice',
    #         'default_purchase_id': self.id,
    #         'default_currency_id': self.currency_id.id,
    #         'default_company_id': self.company_id.id,
    #         'company_id': self.company_id.id,
    #         # Updates
    #         'default_job_type_id': self.job_type.id,
    #         'default_project_name_id': self.p_project_id.id,
    #         'default_previous_invoice_id': last_invoice.id,
    #     }
    #     # choose the view_mode accordingly
    #     if len(self.invoice_ids) > 1 and not create_bill:
    #         result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
    #     else:
    #         res = self.env.ref('account.invoice_supplier_form', False)
    #         result['views'] = [(res and res.id or False, 'form')]
    #         # Do not set an invoice_id if we want to create a new bill.
    #         if not create_bill:
    #             result['res_id'] = self.invoice_ids.id or False
    #     return result


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    recently_done_qty = fields.Float(string="Recently Done")
    recently_done_update = fields.Boolean()

    @api.onchange('recently_done_qty')
    def recently_done_qty_on_change(self):
        if self.recently_done_qty > 0:
            self.recently_done_update = True

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        if self.product_id.purchase_method == 'purchase':
            qty = self.product_qty - self.qty_invoiced
        else:
            qty = self.qty_received - self.qty_invoiced
        if float_compare(qty, 0.0, precision_rounding=self.product_uom.rounding) <= 0:
            qty = 0.0
        res =  {
            'name': '%s: %s' % (self.order_id.name, self.name),
            'job_cost_id': self.job_cost_id.id,
            'job_cost_line_id': self.job_cost_line_id.id,
            'purchase_line_id': self.id,
            'product_uom_id': self.product_uom.id,
            'product_id': self.product_id.id,
            'price_unit': self.price_unit,
            'quantity': qty,
            'price_unit2': self.price_unit,
            'current_qty2': qty,
            'analytic_account_id': self.account_analytic_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'tax_ids': [(6, 0, self.taxes_id.ids)],
            'display_type': self.display_type,
        }
        if not move:
            return res
        if self.currency_id == move.company_id.currency_id:
            currency = False
        else:
            currency = move.currency_id
        res.update({
            'move_id': move.id,
            'currency_id': currency and currency.id or False,
            'date_maturity': move.invoice_date_due,
            'partner_id': move.partner_id.id,
        })
        return res

