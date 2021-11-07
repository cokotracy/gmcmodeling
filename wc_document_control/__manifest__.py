# -*- coding: utf-8 -*-
{
    'name': "wc_document_control",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Ahmed Mokhlef , Wihte Code UK",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'DC',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'odoo_job_costing_management',
                'procurment_list_project', 'report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/document_control.xml',
        'views/work_scope.xml',
        'views/document_control_lines.xml',
        'views/procurement_list.xml',
        'views/project.xml',
        'views/rfi_submittal.xml',
        'views/sir_submittal.xml',
        'views/mir_submittal.xml',
        'views/projects_weekly_reoprt.xml',
        'views/division_scope.xml',
        'views/rfi_mir_sir_lines.xml',
        'views/cvi_submittal.xml',
        'views/site_submittal.xml',
        'views/eng_instruct_submittal.xml',
        'views/variation_submittal.xml',
        'views/change_request_submittal.xml',
        'views/daily_activity_submittal.xml',
        'views/consultant.xml',
        'views/partners.xml',
        'report/report_records.xml',
        'report/report_variation_template.xml',
        'report/report_engineer_instructions_submittal_template.xml',
        'report/report_daily_activity.xml',
        'report/report_cvi_template.xml',
        'report/drawing_report_template_landscape.xml',
        'report/dc_report_template.xml',
        'report/dc_xlsx.xml',
        'report/rfi_report_template.xml',
        'report/sir_report_template.xml',
        'report/mir_report_template.xml',
        'views/document_control_template.xml',

    ],
    'images': [
        'static/description/header.jpeg',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
