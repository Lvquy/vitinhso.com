# -*- coding: utf-8 -*-

from odoo import fields,api,models
from datetime import datetime
from odoo.exceptions import UserError


class SuaChua(models.Model):
    _name = 'sua.chua'
    _description = 'Sửa chữa bảo hành từ khách hàng.'
    _rec_name = 'code'

    code = fields.Char(string='Mã đơn',default=lambda self: ('New'), readonly=True)
    kho_hang = fields.Many2one(comodel_name='nha.kho',string='Kho Hàng')
    nguoi_nhan = fields.Many2one(comodel_name='hr.employee',string='Nhân viên nhận')
    ngay_nhan = fields.Date(string='Ngày nhận', default = datetime.today())
    ngay_tra = fields.Date(string='Ngày trả')
    ly_do_sua = fields.Text(string='Chuẩn đoán lỗi')
    khach_hang = fields.Many2one(comodel_name='res.partner', string='Khách hàng')
    products = fields.One2many(comodel_name='product.suachua.lines', inverse_name='product',string='Mặt hàng')
    note = fields.Text(string='Kết quả sửa chữa')
    state = fields.Selection([('0','Nháp'),('1','Đã xác nhận'),('2','Đã trả cho khách')],string='Trạng thái',default='0')
    chi_phi = fields.Integer(string='Chi phí sửa chữa')

    @api.model
    def create(self, vals):
        if vals.get('code', ('New') == ('New')):
            vals['code'] = self.env['ir.sequence'].next_by_code('suachua.code') or ('New')
            res = super(SuaChua, self).create(vals)
        return res

    def confirm(self):
        for rec in self:
            if rec.state == '0':
                rec.state = '1'
                rec.ngay_nhan = datetime.today()
            else:
                raise UserError('Làm mới trình duyệt')

    def done(self):
        for rec in self:
            if rec.state == '1':
                rec.state = '2'
                rec.ngay_tra = datetime.today()
            else:
                raise UserError('Làm mới trình duyệt')


class ProductSuachuaLine(models.Model):
    _name = 'product.suachua.lines'

    product_template = fields.Many2one(comodel_name='product.template', string='Mặt hàng')
    product = fields.Many2one(comodel_name='sua.chua', string='Mặt hàng')
    serial_num = fields.Char(string='Serial/Model/Code')
    qty = fields.Integer(string='Số lượng')
    note = fields.Text(string='Note')