# -*- coding: utf-8 -*-
{
    'name': "HR Attendance Log",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "",
    'website': "",


    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_attendance', 'hr_contract', 'rm_hr_attendance_sheet_changes'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_attendance_log_view.xml',
        'views/hr_attendance_transfer_log_view.xml',
    ],

}
