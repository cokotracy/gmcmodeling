{
    'name': "AlJanoubi Custody",

    'description': """
      
    """,

    'category': 'Human Resources',

    'author': "Neonile Solutions",
    'website': "http://www.neonile.org",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'mail', 'analytic', 'account_asset', 'base_automation', 'web_dashboard', 'web_cohort'],

    # always loaded
    'data': [
        'security/custody_security.xml',
        'security/ir.model.access.csv',
        'data/custody_creation_email.xml',
        'data/crone.xml',
        'data/sequences.xml',
        'reports/custody_report.xml',
        'reports/custody_lines_report.xml',
        'views/employee.xml',
        'views/custody.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],

}
# -*- coding: utf-8 -*-
