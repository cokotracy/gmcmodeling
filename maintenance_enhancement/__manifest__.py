# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Expense Enhancement',
    'version': '14.1',
    'depends': ['mrp_maintenance','maintenance'],
    'sequence': 15,

    'data': [
        'views/equipment_view.xml',

    ],

    'installable': True,
    'application': True,
    'auto_install': False,

}
