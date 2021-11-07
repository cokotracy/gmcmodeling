# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Web Hijri(Islamic) Datepicker',
    'category': 'Extra tools',
    'version': '1.0',
    'author': 'Synconics Technologies Pvt. Ltd',
    'website': "http://www.synconics.com",
    'description': """This module help you to enable Web Hijri(Islamic) Datepicker in Odoo""",
    'depends': ['web'],
    'data': [
        'views/web_hijri_template.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'bootstrap': True,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
