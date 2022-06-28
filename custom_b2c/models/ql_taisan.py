# -*- coding: utf-8 -*-



from odoo import api, fields, models
from datetime import datetime

class TaiSan(models.Model):
    _name = 'tai.san'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'id_taisan'


    name = fields.Char(string='Tên tài sản',track_visibility = 'onchange')
    status = fields.Selection([('0','New'),('1','Đang sử dụng'),('2','Đã Hủy')],string='Trạng thái tài sản', default='0'
                              ,track_visibility = 'onchange')
    id_taisan = fields.Char(string='ID tài sản', default=lambda self: ('New'),track_visibility = 'onchange',readonly=True)
    gia_tri = fields.Integer(string='Giá trị tài sản',track_visibility = 'onchange')
    date_use = fields.Date(string='Ngày giao tài sản',track_visibility = 'onchange')
    of_user = fields.Many2one(comodel_name='hr.employee', string='Người đang bảo quản',track_visibility = 'onchange',readonly=True)
    note = fields.Char(string='Note')
    phieu_bangiao = fields.One2many(comodel_name='sudung.ts', inverse_name='tai_san',string='Phiếu bàn giao tài sản')
    tinh_trang = fields.Char(string='Tình trạng')
    bao_hanh = fields.Date(string='Bảo hành tới')

    @api.model
    def create(self, vals):
        if vals.get('id_taisan', ('New') == ('New')):
            vals['id_taisan'] = self.env['ir.sequence'].next_by_code('taisan.code') or ('New')
            res = super(TaiSan, self).create(vals)
        return res

    def cancel(self):
        for rec in self:
            rec.of_user = False
            rec.status = '2'

class SDTaisan(models.Model):
    _name = 'sudung.ts'



    date_create = fields.Date(string='Ngày tạo phiếu', default=datetime.today(),readonly=True)
    tai_san = fields.Many2one(comodel_name='tai.san', string='Tài sản')
    date_use = fields.Date(string='Ngày nhận tài sản', default=datetime.today())
    of_user = fields.Many2one(comodel_name='hr.employee', string='Người nhận')
    status = fields.Selection([('0','Nháp'),('1','Đã xác nhận')],string='Trạng thái',readonly=True)
    note = fields.Char(string='Note')

    def confirm(self):
        self.status = '1'
        TS = self.env['tai.san'].browse(self.tai_san.id)
        TS.of_user = self.of_user
        TS.date_use = self.date_use
        TS.status = '1'
