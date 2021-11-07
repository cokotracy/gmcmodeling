# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Procurment Report',
    'version': '13.1',
    'depends': ['base', 'mail', 'odoo_job_costing_management',
                'procurment_list_project', 'wc_document_control', 'report_xlsx'],
    'sequence': 15,

    'data': [
        'security/access.xml',
        'security/ir.model.access.csv',
        'views/procurmentwizard.xml',

    ],

    'installable': True,
    'application': True,
    'auto_install': False,

}
