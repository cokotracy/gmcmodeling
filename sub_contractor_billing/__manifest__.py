# -*- coding: utf-8 -*-
{
    'name': 'Sub Contractor Billing',
    'version': '12.0.1.0.0',
    'author': 'Zienab Abd EL Nasser-',
    'license': 'AGPL-3',
    'maintainer': '<zienab.morsy@gmail.com>',
    'support': 'mostafa.ic2@gmail.com',
    'category': 'Extra Tools',
    'description': """
Project Task Stages and Department
==========================================================
""",
    'depends': [
        'project',
        'material_purchase_requisitions', 'sale', 'sale_management',
        'odoo_job_costing_management', 'project_task_documents'
    ],
    'website': '',
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_changes_view.xml',
        'views/project_views.xml',
        'views/account_invoice_view.xml',
        'views/payment_receipt.xml',
        'data/purchase_order_sequence.xml',
        'views/assets.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}
