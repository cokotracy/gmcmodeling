# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring, manifest-required-author
{
    'name': "Sale Jobs",
    'summary': "Sale Jobs",
    'author': "Omar Abdelaziz",
    'category': 'sale',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'odoo_job_costing_management',
        'job_cost_estimate_customer',
        'sub_contractor_billing',
	'material_purchase_requisitions',
    ],
    'data': [
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
        'views/account_report.xml',
        'views/report_invoice.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
