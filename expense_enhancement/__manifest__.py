# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Expense Enhancement',
    'version': '14.1',
    'depends': ['hr_expense'],
    'sequence': 15,

    'data': [
        'views/hr_expense_view.xml',

    ],

    'installable': True,
    'application': True,
    'auto_install': False,

}
