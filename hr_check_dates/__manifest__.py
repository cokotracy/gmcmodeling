{
    'name': 'HR Check Dates',
    'version': '13.0.1.0.0',
    'category': 'HR',
    'summary': 'Check Important dates for Employee, Contract',
    'description': """
        This module Check Important dates for Employee, Contract
    """,
    'sequence': 1,
    'author': 'NeoNile',
    'website': 'http://neonile.org',
    'depends': ['base', 'hr_enhancement_janobi'],
    'data': [
        'company.xml',
        'data/crone.xml',
        'data/check_birthday.xml',
        'data/check_date_data.xml',
    ],
    'images': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3'
}
