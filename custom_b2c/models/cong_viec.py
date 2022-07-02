# -*- coding: utf-8 -*-



from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import UserError

class CongViec(models.Model):
    _name = 'cong.viec'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'ten_cv'


    date_create = fields.Date(string='Ngày tạo công việc', default=datetime.today(),track_visibility = 'onchange')
    ten_cv = fields.Char(string='Tên công việc',track_visibility = 'onchange')
    note = fields.Html(string='Mô tả công việc')
    nhan_su = fields.Many2many(string='Nhân viên phụ trách', comodel_name='res.users',track_visibility = 'onchange')
    state = fields.Selection([('0','Nháp'),('1','Xác nhận'),('2','Đã hoàn thành'),('3','Đã hủy')],string='Trạng thái',
                             default='0',track_visibility = 'onchange')
    thuoc_kho = fields.Many2one(comodel_name='nha.kho', string='Thuộc kho', required=True)
    price = fields.Integer(string='Giá trị công việc')

    def access_rule_user(self):
        for rec in self:
            for i in rec.nhan_su:
                i.write({'cong_viec': [(4, rec.id)]})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }
    def unaccess_rule_user(self):
        for rec in self:
            for i in rec.nhan_su:
                i.write({'cong_viec': [(3, rec.id)]})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }

    def confirm(self):
        for rec in self:
            rec.state ='1'
    def done(self):
        for rec in self:
            if rec.state == '1':
                rec.state ='2'
                for i in rec.nhan_su:
                    i.user_profile.wallet_balance += rec.price
            else: raise UserError('Làm mới trình duyệt')
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
