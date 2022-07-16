# -*- coding: utf-8 -*-


from odoo import fields, models, api
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = 'res.users'

    user_profile = fields.Many2one(comodel_name='user.profile', string='Tài khoản giao dịch', default=None)
    partner = fields.Many2one(comodel_name='partner', string='Cửa hàng đối tác')
    thuoc_kho = fields.Many2one(comodel_name='nha.kho', string='Nhà kho')
    sua_chua = fields.Many2many(comodel_name='sua.chua', string='Công việc sửa chữa')
    cong_viec = fields.Many2many(comodel_name='cong.viec', string='Công việc của tôi')

    def create_user_profile(self):
        for rec in self:
            if rec.user_profile:
                raise UserError('User already exists in system')
            else:
                User_Profile = rec.env['user.profile']
                LOGIN = rec.env['res.user'].search([('login','=',rec.login)],litmit=1)
                UP = User_Profile.create({
                    'name': rec.name,
                    'email': rec.login,
                    'mobile': rec.partner_id.mobile,
                    'reward_points': rec.partner_id.reward_points,
                    'login': LOGIN.id
                })
                rec.user_profile = UP.id
                rec.partner_id.user_id = rec.id
                rec.partner_id.user_profile = UP.id


    @api.onchange('user_profile')
    def onchange_user(self):
        message = "Bạn đang thay đổi tài khoản giao dịch được liên kết với tài khoản này," \
                  " \n hãy đảm bảo bạn hiểu những vấn đề liên quan sự thay đổi này"
        return {
            'warning': {'title': "Cảnh báo!", 'message': message, 'type': 'notification'},
        }
