# -*- coding: utf-8 -*-
{
    'name': "Procurement List Project",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "G0o0LD",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'hr', 'account', 'account_accountant', 'product', 'employee_documents_expiry',
                'project_task_documents', 'odoo_job_costing_management', 'material_purchase_requisitions',
                'wc_construction'],

    # always loaded
    'data': [
        'security/access.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/account_move_sequence.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #    'demo/demo.xml',
    # ],
}
