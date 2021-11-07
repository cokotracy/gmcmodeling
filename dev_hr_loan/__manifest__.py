# -*- coding: utf-8 -*-
{
    'name': 'Employee Loan Management',
    'version': '14.0',
    'category': 'Generic Modules/Human Resources',
    'description':
        """
        odoo Apps will add Hr Employee Loan functionality for employee
        
Employee loan management
Odoo employee loan management
HR employee loan
Odoo HR employee loan
HR loan for employee
HR loan approval functionality 
Loan Installment link with employee payslip
Loan notification employee Inbox
Loan Deduction in employee payslip
Manage employee loan 
Manage employee loan odoo
Manage HR loan for employee
Manage HR loan for employee odoo
Loan management 
Odoo loan management
Odoo loan management system
Odoo loan management app
helps you to create customized loan
 module allow HR department to manage loan of employees
Loan Request and Approval
Odoo Loan Report
create different types of loan for employees
allow user to configure loan given to employee will be interest payable or not.
Open HRMS Loan Management
Loan accounting
Odoo loan accounting
Employee can create loan request.
Manage Employee Loan and Integrated with Payroll      

    """,
    'summary': 'odoo app will add Hr Employee Loan functioality for employee',
    'depends': ['hr_payroll', 'hr_payroll_account', 'hr_work_entry_contract'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/hr_payroll_data.xml',
        'views/loan_emi_view.xml',
        'views/hr_employee_view.xml',
        'views/hr_loan_view.xml',
        'views/ir_sequence_data.xml',
        'views/employee_loan_type_views.xml',
        'edi/mail_template.xml',
        'edi/skip_installment_mail_template.xml',
        'views/pay_slip_view.xml',
        'views/salary_structure.xml',
        'wizard/import_loan_views.xml',
        'wizard/import_logs_view.xml',
        'views/dev_skip_installment.xml',
        'views/hr_loan_dashbord.xml',
        'views/loan_document.xml',
        'views/loan_report_views.xml',
        'views/add_account_in_res_partner.xml',
    ],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
