# -*- coding: utf-8 -*-
# Copyright 2019 Fenix Engineering Solutions
# @author Jose F. Fernandez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    'name': "Project Task Documents",
    'version': "14.0",
    'category': "Project",
    'summary': "Add documents to project task",
    'images': [
        'static/description/cover.png'
    ],
    'depends': ['project', 'odoo_job_costing_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_inherit.xml',
        'views/automatic_tasks_view.xml'
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
