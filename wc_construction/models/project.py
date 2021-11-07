# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Projects(models.Model):
    _inherit = 'project.project'

    so_id = fields.Many2one(comodel_name="sale.order", string="Quotation Number", compute='get_so_id', store=True,
                            required=False, )
    quotation_count = fields.Integer(compute='get_quotation_count')
    guarantee_count = fields.Integer(string="", required=False, compute='get_guarantee_count')

    @api.depends('quotation_count')
    def get_quotation_count(self):
        for rec in self:
            rec.quotation_count = self.env['sale.order'].search_count([
                ('partner_id', '=', self.partner_id.id),
                ('project_id', '=', self.id)])

    @api.depends('guarantee_count')
    def get_guarantee_count(self):
        for rec in self:
            rec.guarantee_count = self.env['guarantee.letter'].search_count(
                [('project_id', '=', rec.id), ('partner_id', '=', rec.partner_id.id)])

    def guarantee_letter_request(self):
        guar_lett = self.env['guarantee.letter']
        guar_created = guar_lett.create({
            'project_id': self.id,
            'partner_id': self.partner_id.id,
            'submission_date': self.submission_date,
            'tender_qty': sum(self.project_tender_ids.mapped('total_amount'))
        })
        users = []
        for user in self.env.ref('account.group_account_user').users:
            users.append(user.partner_id.id)
        thread_pool = self.env['mail.thread']
        if False not in users:
            thread_pool.message_notify(
                partner_ids=users,
                subject="Guarantee Letter Notification",
                body='This Guarantee Letter Need Your Confirmation: <a target=_BLANK href="/web?#id=' + str(
                    guar_created.id) + '&view_type=form&model=guarantee.letter&action=" style="font-weight: bold">' + str(
                    guar_created.name) + '</a>',
                # email_from=self.env.user.company_id.catchall or self.env.user.company_id.email, )
                email_from=self.env.user.company_id.email )

    def open_related_guarantee_letter(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'guarantee.letter',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'name': 'Guarantee Letter',
            'target': 'current',
            'domain': [('project_id', '=', self.id), ('partner_id', '=', self.partner_id.id)],
            'context': {'default_project_id': self.id, 'default_partner_id': self.partner_id.id,
                        'default_submission_date': self.submission_date,
                        'default_tender_qty': sum(self.project_tender_ids.mapped('total_amount')), },

        }

    @api.depends('so_id')
    def get_so_id(self):
        for rec in self:
            rec.so_id = False
            so_project = self.env['sale.order'].search([('project_id', '=', rec.id)])
            for so in so_project:
                rec.so_id = so.id
                break

    def create_new_quotation(self):
        for rec in self:
            products = self.env['product.product']
            so = self.env['sale.order']
            so_lines = [(5, 0, 0)]
            for line in rec.project_tender_ids:
                if not line.uom_id:
                    if not line.related_product:
                        non_cat_uom = self.env['uom.category'].search([('name', '=', '.')])
                        if len(non_cat_uom) > 0:
                            non_cat_uom = non_cat_uom[0]
                        else:
                            non_cat_uom = self.env['uom.category'].create({
                                'name': '.',
                            })

                        non_uom = self.env['uom.uom'].search([('name', '=', '.')])
                        if len(non_uom) > 0:
                            non_uom = non_uom[0]
                        else:
                            non_uom = self.env['uom.uom'].create({
                                'name': '.',
                                'category_id': non_cat_uom.id,
                            })
                        line.uom_id = non_uom.id

                        created_product = products.sudo().create({
                            'name': line.name,
                            'lst_price': line.total_amount_unit,
                            'type': 'service',
                            'is_tender_item': True,
                            'taxes_id': False,
                            'default_code': line.code,
                            'uom_id': non_uom.id,
                            'uom_po_id': non_uom.id,
                        })
                        line.related_product = created_product.id  # make this field to prevent create product every time you need to create quotation
                else:
                    if not line.related_product:
                        created_product = products.sudo().create({
                            'name': line.name,
                            'lst_price': line.total_amount_unit,
                            'type': 'service',
                            'is_tender_item': True,
                            'taxes_id': False,
                            'default_code': line.code,
                            'uom_id': line.uom_id.id,
                            'uom_po_id': line.uom_id.id,
                        })
                        line.related_product = created_product.id
                so_lines.append((0, 0, {
                    'product_id': line.related_product.id,
                    'name': line.related_product.name,
                    'product_uom_qty': line.tender_qty,
                    'price_unit': line.total_amount_unit if not line.lump_sum_qty else (
                        line.total_amount / line.tender_qty if line.tender_qty > 0 else 0),
                    'product_uom': line.related_product.uom_id.id,
                    'tax_id': False,
                    'code': line.related_product.default_code,
                }))

            so_project = self.env['sale.order'].search([('project_id', '=', rec.id)])
            if so_project:
                so_project.write({'state': 'cancel'})
            so.create({
                'partner_id': rec.partner_id.id,
                'project_id': rec.id,
                'order_line': so_lines,
            })
            rec.get_so_id()

    def open_linked_quotation(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'name': 'Sale Order',
            'domain': [('partner_id', '=', self.partner_id.id), ('project_id', '=', self.id)],
            # ('id', '=', self.so_id.id)
            'target': 'current',
            'context': {'create': False}
        }


class ProjectTender(models.Model):
    _inherit = 'project.tender'

    @api.onchange('uom_id')
    def update_related_product(self):
        if self.uom_id:
            if self.related_product:
                self.related_product.uom_id = self.uom_id.id
                self.related_product.uom_po_id = self.uom_id.id
