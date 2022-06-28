# -*- coding: utf-8 -*-
from odoo import models
from datetime import  datetime

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    _description = "Sales Order Custom"

    def action_confirm(self):
        total = self.amount_total
        cost = 0
        for i in self.order_line:
            cost = cost + i.product_id.standard_price
        loinhuan = total - cost
        discount = self.env['ir.config_parameter'].sudo().get_param('custom_b2c.discount')
        a = float(total)
        b = float(discount)
        c = a*b*0.01
        reward = int(c)
        ln_cty = loinhuan - reward
        REPORT_B2C = self.env['report.b2c']
        REPORT_B2C.create({
            'ln_sale':ln_cty,
            'date_update': datetime.today()
        })
        if self.partner_id.user_id:
            self.partner_id.user_id.user_profile.reward_points += reward
        else:
            self.partner_id.reward_points += reward
        res = super(SaleOrderInherit,self).action_confirm()
        return res

    def action_cancel(self):
        total = self.amount_total
        cost = 0
        for i in self.order_line:
            cost = cost + i.product_id.standard_price
        loinhuan = total - cost

        discount = self.env['ir.config_parameter'].sudo().get_param('custom_b2c.discount')
        a = float(total)
        b = float(discount)
        c = a * b * 0.01
        reward = int(c)
        ln_cty = loinhuan - reward
        REPORT = self.env['report.b2c'].search([], limit=1)
        REPORT.ln_sale -= ln_cty
        self.partner_id.reward_points -= reward
        res = super(SaleOrderInherit, self).action_cancel()
        return res


