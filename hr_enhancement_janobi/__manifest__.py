# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Al-Janobi HR Enhancements',
    'category': 'Human Resources/Employees',
    'sequence': 39,
    'summary': 'Add HR features for Al-Janobi',
    'description': "",
    'installable': True,
    'depends': [
        'hr', 'hr_contract', 'hr_recruitment', 'project', 'analytic', 'hr_payroll', 'hr_work_entry','approvals'
    ],
    'data': [
        'data/sequences.xml',
        'data/report_paperformat.xml',
        'views/employee.xml',
        'views/contract.xml',
        'views/reconcile.xml',
        'views/payment.xml',
        'views/approval.xml',
        'views/department.xml',
        'reports/approval_report_template.xml',
        'reports/approval_report.xml',
        'reports/job_offer_report.xml',
        'reports/contract_report.xml',
        'reports/payslip_report.xml',
        'reports/badge_report.xml',
        'reports/reconcile_report.xml',
        'data/mail_template_data.xml',
        'wizards/employee_move.xml',
        'wizards/job_offer_send.xml',
        'wizards/contract_send.xml',
        'security/ir.model.access.csv',
    ],
}
