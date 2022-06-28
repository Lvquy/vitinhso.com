# -*- coding: utf-8 -*-


#
# from odoo import api, fields, models
# from datetime import datetime
#
# class AccountMove(models.Model):
#     _inherit = 'account.move'
#
#     def action_post(self):
#         res = super(AccountMove, self).action_post()
#         REPORT = self.env['report.b2c'].search([],limit=1)
#         REPORT.ln_sale += self.
#         return res