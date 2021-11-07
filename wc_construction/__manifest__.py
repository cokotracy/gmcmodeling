# -*- coding: utf-8 -*-
{
    'name': "WC Constructions",
    'summary': """
        Short (1  phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """ Long description of module's purpose """,
    'author': "White Code UK",
    'category': 'Construction',
    'version': '14.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'sale', 'purchase', 'account', 'account_accountant', 'odoo_job_costing_management',
                'sub_contractor_billing', 'project_qr_code'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/owner_contract.xml',
        'views/deductions_accounts.xml',
        'views/contracts.xml',
        'views/sale_order.xml',
        'views/project.xml',
        'views/work_plan_items.xml',
        'views/product_view.xml',
        'views/work_plan.xml',
        'views/account_move.xml',
        'views/owner_contract_invoices.xml',
        'views/guarantee_letter.xml',
        'views/quatation_template_report.xml',
        'views/product_category.xml',
        'views/purchase_order.xml',
        'views/guarantee_types.xml',
        'views/partner_ledger.xml',
        'wizard/project_wizard.xml',
        'wizard/report.xml',
        'demo/demo.xml',
        'reports/owner_contract_invoice_report.xml',
    ],
}
