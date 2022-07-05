# -*- coding:utf-8 -*-
from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import UserError

class KhieuNaiGopY(models.Model):
    _name = 'khieu.nai'
    _description = 'Khiếu nại góp ý của thành viên'
    _rec_name = 'name'


    name = fields.Char(string='Tiêu đề')
    content = fields.Html(string='Ý kiến đóng góp/ Khiếu nại')
    date_create = fields.Date(string='Ngày tạo đơn', default=datetime.today())
    user_create = fields.Many2one(comodel_name='res.users', string='Người khiếu nại',
                                  readonly=True,
                                  default=lambda self: self.env.user, compute='onchange_an_danh')
    email = fields.Char('Email',related='user_create.login')
    phone = fields.Char('Phone', related='user_create.mobile')
    an_danh = fields.Boolean(string='Ẩn danh', default=False)
    state = fields.Selection([('0','Nháp'),('1','Đã gửi')],string='Trạng thái', default='0')

    @api.depends('an_danh')
    def onchange_an_danh(self):
        for rec in self:
            if rec.an_danh is True:
                rec.user_create = False
            else: rec.user_create = rec.env.user
    def confirm(self):
        for rec in self:
            if rec.state == '0':
                rec.state = '1'
            else:raise UserError("Làm mới trình duyệt")
