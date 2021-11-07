# -*- coding: utf-8 -*-
{
    'name': "Purchase Custom",


    'description': """
        Add new Screen Called Kind Of Purchase & Filed in Purchase Agreement and Purchase Order 
    """,

    'author': "Whit Code & Elsayed Iraky",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','purchase','purchase_requisition'],

    'data': [
        'security/ir.model.access.csv',
        'views/kind_of_purchase.xml',
        'views/purchase_order.xml',
        'views/purchase_requisition.xml',
    ],

}