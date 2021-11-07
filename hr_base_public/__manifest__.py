# -*- coding: utf-8 -*-

{
    'name': 'HR Base , Puplic replacement',
    'version': '12.0.1.0.0',
    'category': 'Human Resources',
    'author': "White-code, Pankaj",
    'summary': 'Replace ment for modules in odoo 13 and not exist in odoo 12',
    'depends': [
        'hr','base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_public_views.xml',
       
    ],
    'installable': True,
    'application': False,
}
