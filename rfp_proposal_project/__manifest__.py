# -*- coding: utf-8 -*-
{
    'name': "RFP Module",


    'description': """
        Add new Screen for RFP
    """,

    'author': "Whit Code & Zienab Abd EL Nasser",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base','project'],

    'data': [

        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/rfp_view.xml',
        'views/proposal_view.xml',
        'views/project_view.xml',

    ],

}