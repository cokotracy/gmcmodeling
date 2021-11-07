# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning

## Ahmed Salama Code Start ---->
class BangLCConfig(models.Model):
    _name = 'bnk.lc.config'
    _description = 'LC & Form 4 Configuration'
    
    lc_account_id = fields.Many2one(comodel_name='account.account',
                                    string="LC Account",required=True)
    lc_loan_account_id = fields.Many2one(comodel_name='account.account',
                                         string="Loans Account",required=True)
    lc_bank_exp_account_id = fields.Many2one(comodel_name='account.account',
                                             string="Bank Expense Account",required=True)
    lc_manag_exp_account_id = fields.Many2one(comodel_name='account.account',
                                              string="Managerial Expense Account",required=True)
class BangLGConfig(models.Model):
    _name = 'bnk.lg.config'
    _description = 'LG Configuration'
    
    lg_account_id = fields.Many2one(comodel_name='account.account',
                                    string="LG Account",required=True)
    lg_loan_account_id = fields.Many2one(comodel_name='account.account',
                                         string="Loans Account",required=True)
    lg_bank_exp_account_id = fields.Many2one(comodel_name='account.account',
                                             string="Bank Expense Account",required=True)
    lg_renewal_account_id = fields.Many2one(comodel_name='account.account',
                                            string='Renewal Account',required=True,)
    lg_liquidating_account_id = fields.Many2one(comodel_name='account.account',
                                                string='Liquidating Account',required=True,)



## Ahmed Salama Code End.