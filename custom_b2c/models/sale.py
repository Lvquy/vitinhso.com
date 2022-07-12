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


    def get_loi_nhuan_ban_hang(self):
        ICP = self.env['ir.config_parameter'].sudo()
        discount_up_cp= float(ICP.get_param('custom_b2c.discount_up_cp', default=0))
        loi_nhuan_ban_hang= float(ICP.get_param('custom_b2c.loi_nhuan_ban_hang', default=0))
        total = float((self.amount_total*discount_up_cp)*0.01)
        up_loi_nhuan = (loi_nhuan_ban_hang + total)
        ICP.set_param('custom_b2c.loi_nhuan_ban_hang', up_loi_nhuan)


    def action_confirm(self):
        #check pay method
        for rec in self:
            if rec.pay_method.is_wallet_vts is True:
                #kt so du -> tru tien
                WALLET = rec.partner_id.user_profile.wallet_balance
                if WALLET >=  rec.amount_total:
                    rec.partner_id.user_profile.wallet_balance -= rec.amount_total
                    rec.get_loi_nhuan_ban_hang()
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
                rec.get_loi_nhuan_ban_hang()
                #ck ngan hang

        total = self.amount_total
        cost = 0
        for i in self.order_line:
            cost = cost + i.product_id.standard_price
        loinhuan = total - cost
        discount = self.env['ir.config_parameter'].sudo().get_param('custom_b2c.discount')
        cty_discount = self.env['ir.config_parameter'].sudo().get_param('custom_b2c.discount_for_cty')
        a = float(total)
        b = float(discount)
        d = float(cty_discount)
        c = a*b*0.01
        cty_rw = a*d*0.01
        reward = int(c)
        reward_cty = int(cty_rw)
        ln_cty = loinhuan
        REPORT_B2C = self.env['report.b2c']
        REPORT_B2C.create({
            'price':ln_cty,
            'type_profit':'sale',
            'date_update': datetime.today()
        })
        ADMIN_CTY = self.env['user.profile'].search([('is_adm_cty','=',True)],limit=1)
        ADMIN_CTY.reward_points +=reward_cty
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

        REPORT_B2C = self.env['report.b2c']
        REPORT_B2C.create({
            'price': -ln_cty,
            'type_profit': 'sale'
        })

        self.partner_id.reward_points -= reward
        res = super(SaleOrderInherit, self).action_cancel()
        return res
