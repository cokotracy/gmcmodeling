# Copyright 2018 Giacomo Grasso <giacomo.grasso.82@gmail.com>
# Odoo Proprietary License v1.0 see LICENSE file

{
    'name': 'Orders billed amount',
    'version': '11.0.1.0',
    'category': 'Accounting',
    'description': """
            Compute billed and unbilled amounts in purchase and sale orders.
        """,
    'author': 'Giacomo Grasso - giacomo.grasso.82@gmail.com ',
    'maintainer': 'Giacomo Grasso - giacomo.grasso.82@gmail.com',
    'website': 'https://github.com/jackjack82',
    'images': ['static/description/main_screenshot.png'],
    'license': 'OPL-1',
    'currency': 'EUR',
    'depends': [
        'account',
        'sale_management',
        'purchase',
        # 'treasury_forecast',
        ],
    'data': [
        'views/purchase_order.xml',
        'views/sale_order.xml',
    ],

    'installable': True,
    'auto_install': False,
}
