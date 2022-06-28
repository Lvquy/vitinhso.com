# -*- coding: utf-8 -*-



from odoo import api, fields, models
from datetime import datetime

class CoPhan(models.Model):
    _name = 'co.phan'
    _description = 'Cổ phần CTY'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    id_cp = fields.Char(string='ID cổ phần', readonly=True, default=lambda self: ('New'))
    status = fields.Selection([('0','New'),('1','Đang sẵn sàng'),('2','Đang đầu tư'),
                               ('3','Đang tiết kiệm'),('4','Đang khóa'),('5','Đã hủy'),('6','Đang chờ')], string='Trạng thái cổ phần',
                               default='0',readonly=True, track_visibility = 'onchange')
    create_date = fields.Datetime(string='Thời điểm tạo',default=datetime.today(), readonly=True)
    of_user = fields.Many2one(comodel_name='user.profile', string='Sở hữu', track_visibility = 'onchange', readonly=False)
    of_create = fields.Many2one(comodel_name='phat.cp',string='Tên đợt phát hành', readonly=True, track_visibility = 'onchange')
    log_history = fields.One2many(comodel_name='log.cp', inverse_name='name', string='Lịch sử CP', readonly=True,ondelet="cascade")

    @api.model
    def create(self, vals):
        if vals.get('id_cp', ('New') == ('New')):
            vals['id_cp'] = self.env['ir.sequence'].next_by_code('cophan.code') or ('New')
            res = super(CoPhan, self).create(vals)
        return res


class PhatCP(models.Model):
    _name = 'phat.cp'
    _description = 'Phát hành cổ phần'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Tên đợt phát hành', required=True, track_visibility = 'onchange')
    create_date = fields.Datetime(default=datetime.today(), string='Ngày phát hành', readonly=True)
    so_luong_cp = fields.Integer(string='Số lượng cổ phần phát hành',default=0, track_visibility = 'onchange')
    state = fields.Selection([('0','Bản nháp'),('1','Đã xác nhận'),('2','Đã hủy')],string='Trạng thái', default='0', track_visibility = 'onchange')
    user_create = fields.Many2one(comodel_name='res.users',string='Người phát hành', readonly=True,
                                  default=lambda self: self.env.user, track_visibility = 'onchange')
    line_cp = fields.One2many(comodel_name='co.phan', inverse_name='of_create', string='List Cổ phần')

    def confirm(self):
        self.state = '1'
        if self.so_luong_cp <=0:
            self.so_luong_cp =1
        for i in range(self.so_luong_cp):
            res = self.env['co.phan'].create({'of_create': self.id})
        return res
    def cancel(self):
        self.state = '2'


class LogCP(models.Model):
    _name = 'log.cp'
    _rec_name = 'name'

    date = fields.Datetime(string='Ngày giao dịch', default=datetime.today())
    from_user = fields.Many2one(comodel_name='user.profile', string='Từ User')
    to_user = fields.Many2one(comodel_name='user.profile', string='Đến User')
    code_giaodich = fields.Char(string='Mã chứng từ')
    name = fields.Many2one(comodel_name='co.phan', string='Name')

