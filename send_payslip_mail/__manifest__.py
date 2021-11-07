# -*- coding: utf-8 -*-
{
    'name': "Payslips Send Mails",
    'description': """
        Add new button in action menu to send mails to employees.
    """,

    'author': "White Code (Omnya Rashwan)",
    'version': '1.0',
    'category': 'Payroll',
    'depends': ['base', 'mail', 'hr_payroll'],

    'data': [
        'views/hr_payslip_view.xml',
    ],

}
