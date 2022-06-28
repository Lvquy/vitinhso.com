# -*- coding: utf-8 -*-



from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import UserError

class Report(models.Model):
    _name = 'report.b2c'
    _order = 'id'

    cost_total = fields.Integer(string='Tổng số vốn tiền mặt')
    ln_total = fields.Integer(string='Tổng lợi nhuận', readonly=True, compute="get_total_ln")
    ln_dautu = fields.Integer(string='Lợi nhuận đầu tư', readonly=True)
    ln_phi_giao_dich_cp = fields.Integer(string='Lợi nhận phí giao dịch cổ phần', readonly=True)
    ln_thi_cong = fields.Integer(string='Lợi nhuận thi công', readonly=True)
    ln_sale = fields.Integer(string='Lợi nhuận bán hàng', readonly=True)
    date_update = fields.Date(string='Ngày cập nhật',readonly=True,default=datetime.today())

    @api.onchange('ln_dautu','ln_phi_giao_dich_cp','ln_thi_cong')
    def get_total_ln(self):
        for rec in self:
            rec.ln_total = rec.ln_dautu + rec.ln_thi_cong + rec.ln_phi_giao_dich_cp + rec.ln_sale

class QuyCty(models.Model):
    _name = 'quy.cty'

    name = fields.Char(string='Tên quỹ')
    discount = fields.Integer(string='Số % trích từ tổng lợi nhuận')
    so_du = fields.Integer(string='Tổng quỹ', compute='get_sodu', help='Tổng quỹ từ trước tới nay theo % tổng lợi nhuận')
    create_date = fields.Date(string='Ngày tạo quỹ', default=datetime.today())
    state = fields.Selection([('0','Nháp'),('1','Xác nhận')], default='0', string='Trạng thái')
    log_quy = fields.One2many(comodel_name='log.quy', inverse_name='ten_quy', string='Lịch sử chi')
    thuong_nv = fields.One2many(comodel_name='thuong.nv', inverse_name='tu_quy', string='Thưởng đồng loạt')
    total_da_chi = fields.Integer(string='Tổng tiền đã chi', compute='_compute_total_da_chi')
    total_da_thuong = fields.Integer(string='Tổng tiền đã thưởng', compute='_compute_total_da_thuong')
    total_thuong_chi = fields.Integer(string='Tổng tiền đã sử dụng', compute='_compute_total_thuong_chi')
    con_lai = fields.Integer(string='Số dư còn lại', compute='_compute_con_lai')

    @api.onchange('so_du','total_thuong_chi')
    def _compute_con_lai(self):
        for rec in self:
            rec.con_lai = rec.so_du - rec.total_thuong_chi

    @api.onchange('log_quy')
    def _compute_total_da_chi(self):
        for rec in self:
            total_da_chi = 0
            for l in rec.log_quy.search(['&',('ten_quy','=',rec.id),('state','=','1')]):
                print(l.so_tien)
                total_da_chi += l.so_tien
            rec.total_da_chi = total_da_chi

    @api.onchange('thuong_nv')
    def _compute_total_da_thuong(self):
        for rec in self:
            total_da_thuong = 0
            for l in rec.thuong_nv.search(['&',('tu_quy','=',rec.id),('state_thuong_dong_loat', '=', '1')]):
                total_da_thuong += l.so_tien_thuong
            rec.total_da_thuong = total_da_thuong

    @api.onchange('total_da_chi','total_da_thuong')
    def _compute_total_thuong_chi(self):
        for rec in self:
            rec.total_thuong_chi = rec.total_da_thuong + rec.total_da_chi

    def confirm(self):
        for rec in self:
            rec.state = '1'

    @api.onchange('discount')
    def get_sodu(self):
        for rec in self:
            ln = 0
            REPORT = rec.env['report.b2c'].search([])
            for i in REPORT:
                ln += i.ln_total
            rec.so_du = (ln*rec.discount)*0.01

class LogQuy(models.Model):
    _name = 'log.quy'

    date_chi = fields.Date(string='Ngày chi', default=datetime.today())
    user_admin = fields.Many2one(comodel_name='res.users', string='Người nhận tiền')
    so_tien = fields.Integer(string='Số tiền')
    note = fields.Text(string='Lý do chi tiền')
    state = fields.Selection([('0','Nháp'),('1','Xác nhận')], default='0', string='Trạng thái')
    ten_quy = fields.Many2one(comodel_name='quy.cty', string='Tên quỹ')
    kieu_tien = fields.Selection([('0','Tiền mặt'),('1','Chuyển vào ví'),('2','CK ngân hàng')], string='Kiểu tiền', default='0')

    def confirm(self):
        for rec in self:
            rec.state = '1'
            if rec.kieu_tien == '1':
                rec.user_admin.user_profile.wallet_balance += rec.so_tien
class Thuong(models.Model):
    _name = 'thuong.nv'

    so_tien_thuong = fields.Integer(string='Số tiền thưởng')
    tong_nguoi_thu_huong = fields.Integer(string='Tổng người nhận thưởng', compute="_compute_tong_nguoi_thu_huong")
    ds_nguoi_thu_huong = fields.Many2many(string='Danh sách người thụ hưởng', comodel_name='res.users')
    so_tien_chia = fields.Integer(string='Số tiền mỗi người nhận được', compute='_compute_so_tien_chia')
    state_thuong_dong_loat = fields.Selection([('0', 'Mới tạo'), ('1', 'Đã thưởng')], string='Trạng thái thưởng',
                                              default='0', readonly=True)
    tu_quy = fields.Many2one(comodel_name='quy.cty', string='Nguồn tiền', readonly=True)
    kieu_tien = fields.Selection([('0','Tiền mặt'),('1','Chuyển vào ví')],string='Kiểu tiền', default='0')
    note = fields.Text(string='Note')
    ngay_thuong = fields.Date(string='Ngày thưởng', default=datetime.today(), readonly=True)


    @api.onchange('ds_nguoi_thu_huong')
    def _compute_tong_nguoi_thu_huong(self):
        for rec in self:
            rec.tong_nguoi_thu_huong = 0
            for ng in rec.ds_nguoi_thu_huong:
                rec.tong_nguoi_thu_huong += 1

    @api.onchange('so_tien_thuong','ds_nguoi_thu_huong')
    def _compute_so_tien_chia(self):
        for rec in self:
            if rec.tong_nguoi_thu_huong >0:
                rec.so_tien_chia = rec.so_tien_thuong / rec.tong_nguoi_thu_huong
            else:
                rec.so_tien_chia = 0

    def thuong_nhan_vien(self):
        for rec in self:
            if rec.so_tien_thuong > (rec.tu_quy.con_lai):
                raise UserError('Số tiền thưởng vượt quá số dư quỹ hiện tại')
            else:
                rec.ngay_thuong = datetime.today()
                if rec.kieu_tien == '1':
                    # chuyen vao vi
                    rec.state_thuong_dong_loat = '1'
                    tien_thuong = rec.so_tien_chia
                    for kh in rec.ds_nguoi_thu_huong:
                        kh.user_profile.wallet_balance += tien_thuong
                if rec.kieu_tien == '0':
                    # tien mat
                    rec.state_thuong_dong_loat = '1'

    def get_nguoi_thu_huong(self):
        for rec in self:
            USER = rec.env['res.users'].search([])
            rec.ds_nguoi_thu_huong = USER