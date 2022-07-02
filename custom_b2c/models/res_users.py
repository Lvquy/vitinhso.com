# -*- coding: utf-8 -*-


from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    user_profile = fields.Many2one(comodel_name='user.profile', string='Tài khoản giao dịch', default=None)
    partner = fields.Many2one(comodel_name='partner', string='Cửa hàng đối tác')
    thuoc_kho = fields.Many2one(comodel_name='nha.kho', string='Nhà kho')
    sua_chua = fields.Many2many(comodel_name='sua.chua', string='Công việc sửa chữa')
    cong_viec = fields.Many2many(comodel_name='cong.viec', string='Công việc của tôi')