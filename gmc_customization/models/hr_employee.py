from odoo import models,fields

class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	emp_code = fields.Char("Employee Code",required=True)
	identification_id = fields.Char("Identification No.",size=14,required=True,)
	disp_name = field_name = fields.Char(
	    string='Display Name',
	)

	email_status = fields.Selection([('pending', 'Pending'),
									('active', 'Active'),
									('blocked', 'Blocked'),
									('deleted', 'Deleted'),
									('converted', 'Converted'),
									('na', 'NA'),
									 ], "Email Status")
	email_type = fields.Selection([('buisness', 'Business Standard'),
									('exchnage', 'Exchange online'),
									 ], "Email Type")