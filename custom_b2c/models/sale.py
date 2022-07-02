# -*- coding: utf-8 -*-
from odoo import models, fields
from datetime import  datetime
from odoo.exceptions import UserError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    _description = "Sales Order Custom"

    pay_method = fields.Many2one(comodel_name='payment.acquirer',
                                 domain=[('state','=','enabled')],track_visibility='onchange',
                                 string='Phương thức thanh toán')

    def action_confirm(self):
        #check pay method
        for rec in self:
            if rec.pay_method.is_wallet_vts is True:
                #kt so du -> tru tien
                WALLET = rec.partner_id.user_profile.wallet_balance
                if WALLET >=  rec.amount_total:
                    rec.partner_id.user_profile.wallet_balance -= rec.amount_total
                else:
                    notification = {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': ('Thông báo'),
                            'message': 'Số dư ví không đủ',
                            'type': 'warning',  # types: success,warning,danger,info
                            'next': {'type': 'ir.actions.act_window_close'},
                            'sticky': False,  # True/False will display for few seconds if false
                        },
                    }
                    return notification
            else:
                pass
                #ck ngan hang
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


