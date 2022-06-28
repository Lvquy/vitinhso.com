# -*- coding: utf-8 -*-



from odoo import api, fields, models
from datetime import datetime


class Partner(models.Model):
    _name = 'partner'

    date_create = fields.Date(string='Ngày tạo', default=datetime.today())
    name = fields.Char(string='Tên cửa hàng', required=True)
    add = fields.Text(string='Địa chỉ')
    mobile = fields.Char(string='Số điện thoại')
    img = fields.Binary(string='Hình đại diện')
    tong_diem = fields.Integer(string='Tổng điểm')
    state = fields.Selection([('0','Mới tạo'),('1','Đã xác thực',)],string='Trạng thái', default='0')
    discount_partner = fields.Float(string='Phần trăm cho cửa hàng', help='Phần trăm theo tổng giá trị đơn hàng')
    discount_cus = fields.Float(string='Phần trăm cho khách hàng')
    discount_adm = fields.Float(string='Phần trăm cho Vi Tính Số')
    order_line = fields.One2many(comodel_name='order.partner', inverse_name='partner', string='Đơn hàng', readonly=True)


    def confirm(self):
        for rec in self:
            if rec.state == '0':
                rec.state = '1'
                rec.date_create = datetime.today()

class OrderPartner(models.Model):
    _name = 'order.partner'


    partner = fields.Many2one(stirng='Đối tác', comodel_name='partner', readonly=True)
    total = fields.Integer(string='Tổng giá trị đơn hàng')
    cus_name = fields.Char(string='Tên khách hàng')
    cus_mobile = fields.Char(string='Số điện thoại khách hàng')
    date_order = fields.Date(string='Ngày tạo đơn', default=datetime.today())
    state = fields.Selection([('0','Nháp'),('1','Đã xác nhận')],string='Trạng thái', default='0')
    note = fields.Text(string='Note')

    @api.model
    def create(self, vals):
        vals['partner'] = self.env.user.partner.id
        res = super(OrderPartner, self).create(vals)
        return res

    def confirm_order(self):
        for rec in self:
            if rec.state == '0':
                rec.state = '1'
                POINTS_CUA_HANG = 0
                POINTS_CUA_HANG = int((rec.total*rec.partner.discount_partner)*0.01)
                rec.partner.tong_diem += POINTS_CUA_HANG
                user_profile_cua_hang = rec.env.user.user_profile
                user_profile_cua_hang.reward_points += POINTS_CUA_HANG

                POINTS_KHACH_HANG = 0
                POINTS_KHACH_HANG = int((rec.total*rec.partner.discount_cus)*0.01)
                user_profile_khach_hang = rec.env['user.profile'].search([('mobile','=',rec.cus_mobile)],limit=1)
                if user_profile_khach_hang:
                    user_profile_khach_hang.reward_points += POINTS_KHACH_HANG
                POINTS_ADMIN = 0
                POINTS_ADMIN = int((rec.total*rec.partner.discount_adm)*0.01)
                user_profile_adm = rec.env['user.profile'].search([('is_adm_cty','=',True)],limit=1)
                if user_profile_adm:
                    user_profile_adm.reward_points += POINTS_ADMIN



