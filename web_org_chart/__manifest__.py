# See LICENSE file for full copyright and licensing details.
{
    'name': 'Organizational Chart',
    'version': '13.0.1.0.0',
    'summary': """Hierarchical Structure of Companies Employee""",
    'description': """Hierarchical Structure of Companies Employee
                Generate organization chart
                Odoo chart view
                Odoo tree structure graph
                Employee hierarchy chart
                Employee structure
                Employee level and grade
    """,
    'category': 'Extra Tools',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'maintainer': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'license': 'LGPL-3',
    'depends': [
        'hr'
    ],
    'data': [
        "views/templates.xml",
        "views/web_org_chart.xml",
    ],
    'qweb': ['static/src/xml/web_org_chart.xml'],
    'images': ['static/description/Web_OrgChart.png'],
    'price': 20,
    'currency': 'EUR',

}
