# -*- coding: utf-8 -*-

{
    'name': 'Print Journal Entries Report in Odoo',
    'version': '13.0.1.0.0',
    'category': 'Account',
    'summary': 'Allow to print pdf report of Journal Entries.',
    'description': """
    Allow to print pdf report of Journal Entries.
""",
    'URL':"https://system.white-code.co.uk/web?#id=2214&action=395&model=project.task&view_type=form&menu_id=263",
    'depends': ['base','account'],
    'data': [
            'report/report_journal_entries.xml',
            'report/report_journal_entries_view.xml',
    ],
    'author': 'White-code, Pankaj',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/qehLT4WOWPs',
    "images":["static/description/Banner.png"],
}
