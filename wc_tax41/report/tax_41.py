# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF, safe_eval


class Tax41(models.TransientModel):
    _name = 'wizard.tax_41'

    from_date = fields.Date(string="من تـاريخ",required=True)
    to_date = fields.Date(string="إالى تـاريخ",required=True)


    def print_tax_41_xls(self):

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'from_date': self.from_date,
                'to_date': self.to_date,

            },
        }

        return self.env.ref('wc_tax41.tax_41_xlsx').report_action(self, data=data)
