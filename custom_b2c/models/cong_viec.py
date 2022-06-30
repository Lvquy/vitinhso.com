# -*- coding: utf-8 -*-



from odoo import api, fields, models
from datetime import datetime

class CongViec(models.Model):
    _name = 'cong.viec'
    _inherit = ['mail.thread','mail.activity.mixin']


    date_create = fields.Date(string='Ngày tạo công việc', default=datetime.today(),track_visibility = 'onchange')
    ten_cv = fields.Char(string='Tên công việc',track_visibility = 'onchange')
    note = fields.Html(string='Mô tả công việc')
    nhan_su = fields.Many2many(string='Nhân viên phụ trách', comodel_name='hr.employee',track_visibility = 'onchange')
    state = fields.Selection([('0','Nháp'),('1','Xác nhận'),('2','Đã hoàn thành'),('3','Đã hủy')],string='Trạng thái',
                             default='0',track_visibility = 'onchange')
    thuoc_kho = fields.Many2one(comodel_name='nha.kho', string='Thuộc kho', required=True)
    price = fields.Integer(string='Giá trị công việc')

    def confirm(self):
        for rec in self:
            rec.state ='1'
    def done(self):
        for rec in self:
            rec.state ='2'
    def cancel(self):
        for rec in self:
            rec.state ='3'

class BaoCaoCV(models.Model):
    _name = 'baocao.cv'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date_create = fields.Datetime(string='Ngày báo cáo', default=datetime.today(),readonly=True,track_visibility = 'onchange')
    nhan_vien = fields.Many2one(comodel_name='hr.employee', string='Nhân viên',track_visibility = 'onchange')
    cong_viec = fields.Html(string='Công việc đã làm trong ngày')
    state = fields.Selection([('0', 'Nháp'), ('1', 'Xác nhận')],
                             string='Trạng thái',
                             default='0', track_visibility='onchange')

    def confirm(self):
        for rec in self:
            rec.state = '1'

class NhaKho(models.Model):
    _name = 'nha.kho'

    name = fields.Char(string='Nhà kho')
    add = fields.Char(string='Địa chỉ')
    date_create = fields.Date(string='Ngày tạo', default=datetime.today())