# -*- coding: utf-8 -*-
{
    'name': 'POS Counter Bill',
    'summary': "Counter wise Bill print in POS",
    'description': """
Point of Sale Counter Bill Print.
========================
Module Contains : Counter Assigning for Product,
Bill Print : Counter wise Bill Print with auto cut facility (need auto cut printer).
    """,

    'author': 'iPredict IT Solutions Pvt. Ltd.',
    'website': 'http://ipredictitsolutions.com',
    "support": "ipredictitsolutions@gmail.com",

    'category': 'Point of Sale',
    'version': '13.0.0.1.0',
    'depends': ['point_of_sale'],

    'data': [
        'security/ir.model.access.csv',
        'views/pos_view.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],

    'license': "OPL-1",
    'price': 40,
    'currency': "EUR",

    'installable': True,
    'application': True,

    'images': ['static/description/main.png'],
    'live_test_url': 'https://youtu.be/mCU1EsgPRQ8',
}
