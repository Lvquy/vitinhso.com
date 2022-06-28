# -*- coding: utf-8 -*-



from odoo import api, fields, models


class Product(models.Model):
    _inherit = 'product.product'

    warranty = fields.Integer(string="Thời gian bảo hành (Tháng)")
    vitri_kehang = fields.Many2one(comodel_name='ke.hang', string='Vị trí trong kho')

    def setprice_product(self):
        return {
            'name': ('Cài đặt giá cho sản phẩm'),
            'type': 'ir.actions.act_window',
            'res_model': 'set.price',
            'view_mode': 'form',
            'target': 'new',
        }
    def compute_hide(self):
        if self.hide == True:
            self.hide = False
        else:
            self.hide = True