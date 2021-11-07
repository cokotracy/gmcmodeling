from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date


class HrContract(models.Model):
    _inherit = 'hr.contract'

    contract_type = fields.Selection(string='Contract Type', selection=[('1', '1 Year'),
                                                                        ('2', '2 Years'),
                                                                        ('other', 'Other')])
    service_duration = fields.Integer(string='Service Duration(Days)', compute='_get_service_duration')
    contract_document = fields.Binary(string='Contract Document')
    housing_insured = fields.Selection(string='Housing', selection=[('insured', 'Insured'),
                                                                    ('not', 'Not Insured')])
    housing_allowance = fields.Monetary(string='Housing Allowance')
    overtime_allowance = fields.Monetary(string='Overtime Allowance')
    transportation_allowance = fields.Monetary(string='Transportation Allowance')
    meal_allowance = fields.Monetary(string='Meal Allowance')
    phone_allowance = fields.Monetary(string='Phone Allowance')
    nature_of_work_allowance = fields.Monetary(string='Nature Of Work Allowance')
    other_allowance = fields.Monetary(string='Other Allowances')
    total_wage = fields.Monetary(string='Total Wage', compute='_get_total_wage')
    number_of_tickets = fields.Integer(string='Number Of Tickets')
    tickets_type = fields.Selection(string='Tickets Type', selection=[('land', 'Land'),
                                                                      ('naval', 'Naval'),
                                                                      ('air', 'Air')])
    tickets_price = fields.Monetary(string='Tickets Price')
    in_kind_allowance_name = fields.Char(string='Allowance Name')
    in_kind_allowance_amount = fields.Monetary(string='Allowance Amount')
    in_kind_allowance_start_date = fields.Date(string='Allowance Start Date')
    in_kind_allowance_end_date = fields.Date(string='Allowance End Date')

    @api.depends('date_start')
    @api.onchange('date_start')
    def _get_service_duration(self, end_date=False):
        """
        :param end_date: if period stop is a given date , else it'll work on today's date
        """
        for record in self:
            date_end = date.today() if not end_date else end_date
            if record.date_start and record.date_start < date_end:
                if record.date_end and record.date_end < date_end:
                    record.service_duration = (record.date_end - record.date_start).days + 1
                else:
                    record.service_duration = (date_end - record.date_start).days + 1
            else:
                record.service_duration = 0

    @api.depends('housing_insured')
    @api.onchange('housing_insured')
    def _onchange_housing_insured(self):
        for record in self:
            if record.housing_insured == 'insured':
                record.housing_allowance = 0

    @api.depends('wage', 'housing_allowance', 'overtime_allowance', 'transportation_allowance', 'meal_allowance',
                 'phone_allowance', 'nature_of_work_allowance', 'other_allowance')
    @api.onchange('wage', 'housing_allowance', 'overtime_allowance', 'transportation_allowance', 'meal_allowance',
                  'phone_allowance', 'nature_of_work_allowance', 'other_allowance')
    def _get_total_wage(self):
        for record in self:
            record.total_wage = record.wage + record.housing_allowance + record.overtime_allowance \
                                + record.transportation_allowance + record.meal_allowance + record.phone_allowance \
                                + record.nature_of_work_allowance + record.other_allowance

    @api.constrains('number_of_tickets')
    @api.onchange('number_of_tickets', 'tickets_type', 'contract_type')
    @api.depends('number_of_tickets', 'tickets_type', 'contract_type')
    def _maximum_flight_tickets(self):
        for record in self:
            if record.contract_type == 'other' and record.tickets_type == 'air' and record.number_of_tickets > 4:
                record.number_of_tickets = 0
                raise ValidationError('Number of Tickets cannot exceed 4 in case of Air Tickets')
