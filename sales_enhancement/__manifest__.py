# -*- coding: utf-8 -*-
{
    'name': "Sales order Enhancement",
    'description': """
        Add new groups, fields, buttons and workflow in sales and sales customer view. 
    """,

    'author': "White Code (Omnya Rashwan)",
    'website': "https://system.white-code.co.uk/web#view_type=form&model=project.task&id=1321&active_id=1321&menu_id=, https://system.white-code.co.uk/web#view_type=form&model=project.task&id=1321&active_id=1321&menu_id=",
    'version': '1.0',
    'category': 'Sales',
    'depends': ['base', 'sale'],

    'data': [
        # 'security/ir.model.access.csv',
        'security/sales_order_security.xml',
        'views/partner_view.xml',
        'views/sales_order_view.xml',
    ],

}
