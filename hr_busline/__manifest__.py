# -*- coding: utf-8 -*-

{
    'name': 'HR Employee BusLine',
    'version': '13.0.1.0.0',
    'category': 'Human Resources',
    'author': "White-code, Pankaj",
    'summary': 'Allow to add bus line in employee profile',
    'depends': [
        'hr', 'base'
    ],
    'data': [
        # 'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_bus_line_view.xml',
        'views/hr_view.xml',
    ],
    'installable': True,
    'application': False,
}
