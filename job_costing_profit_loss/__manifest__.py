# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.

{
    'name': 'P&L for Job Costing (Profit and Loss Report)',
    'price': 49.0,
    'currency': 'EUR',
        'version': '1.1.1',

    'category' : 'Projects',
    'license': 'Other proprietary',
    'summary': """P&L for Job Costing / Contracting / Construction (Profit and Loss Report).""",
    'description': """
This app allow you to add job costing profit and loss report
P&L for Job Costing (Profit and Loss Report)
P&L for Job Costing (Profit and Loss Report)
job costing
cost sheet
job contracting
contracting
construction
job cost sheet
Odoo Job Costing And Job Cost Sheet (Contracting)
Odoo job cost sheet
job cost sheet odoo
contracting odoo
odoo construction
job costing (Contracting)
odoo job costing (Contracting)
odoo job costing Contracting
job order odoo
work order odoo
job Contracting
job costing
job cost Contracting
odoo Contracting
Contracting odoo job
Features of Job Costing
Enabling Job Costing
Creating Cost Centres for Job Costing
project job cost
project job costing
project job contracting
project job contract
job contract
jobs contract
construction
Construction app
Construction odoo
odoo Construction
Construction Management
Construction Activity
Construction Jobs
Job Order Construction
Job Orders Issues
Job Order Notes
Construction Notes
Job Order Reports
Construction Reports
Job Order Note
Construction app
Construction 


""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'depends': [
        'odoo_job_costing_management',
        'job_costing_cost_actual',
    ],
    'images': ['static/description/img1.jpg'],
    'live_test_url': 'https://youtu.be/WVAXo5_RG18',
    'data':[
        'views/job_cost_line_view.xml',
        'views/job_cost_invoice.xml',
        'report/job_costing_report.xml',
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
