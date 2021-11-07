from odoo import fields, models, api, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    net_salary = fields.Float(string='Net Salary', compute="get_net_salary")

    def get_net_salary(self):
        for item in self:
            if item.line_ids:
                for line in item.line_ids:
                    if line.code == 'NET' and line.category_id.name == 'Net':
                        item.net_salary = line.amount
                    else:
                        item.net_salary = 0.0
            else:
                item.net_salary = 0.0

    def _find_mail_template(self):
        return self.env['ir.model.data'].xmlid_to_res_id('send_payslip_mail.mail_template_payslip',
                                                         raise_if_not_found=False)

    def action_payslip_send_mail(self):
        payslips = self.env['hr.payslip'].browse(self.env.context.get('active_ids', []))
        for payslip in payslips:
            template_id = payslip._find_mail_template()
            print(template_id, '7777')
            lang = self.env.context.get('lang')
            template = self.env['mail.template'].browse(template_id)
            print(template, '8888888')
            if template.lang:
                lang = template._render_template(template.lang, 'hr.payslip', payslip.ids[0])
            ctx = {
                'default_model': 'hr.payslip',
                'default_res_id': payslip.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'force_email': True,
                'model_description': payslip.with_context(lang=lang).name,
                'email_to': payslip.employee_id.work_email,
            }
            template.with_context(ctx).send_mail(payslip.id, True)
