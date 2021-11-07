# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'PURCHASE AGREEMENT workflow',
    'version': '13.0.1.0.0',
    'category': '',
    'website': 'https://system.white-code.co.uk/web#id=1300&action=395&model=project.task&view_type=form&menu_id=263',
    'summary': 'Purchase Agreement Workflow Approval',
    'description': """""",
    'depends': ['base', 'purchase', 'purchase_requisition'],
    'data': [
        # 'security/purchase_agreement_security.xml',
        'views/purchase_agreement_view.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
