# -*- coding: utf-8 -*-


from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import UserError


class HR(models.Model):
    _inherit = 'hr.employee'

    cmnd_front = fields.Image(string='CMND mặt trước')
    cmnd_back = fields.Image(string='CMND mặt sau')
    other_doc1 = fields.Binary(string='Giấy tờ khác 1')
    other_doc2 = fields.Binary(string='Giấy tờ khác 2')
    other_doc3 = fields.Binary(string='Giấy tờ khác 3')
    other_doc4 = fields.Binary(string='Giấy tờ khác 4')
    pdf_doc = fields.Binary(string='PDF Scan')
    ngay_nghi = fields.One2many(comodel_name='ngay.nghi', inverse_name='nhanvien')
    ung_tien = fields.One2many(comodel_name='ung.luong', inverse_name='nguoi_ung')
    bao_cao_cv = fields.One2many(comodel_name='baocao.cv', inverse_name='nhan_vien',
                                 string='Báo cáo công việc hàng ngày')
    phep_nghi = fields.Date(string='Ngày nghỉ đặc biệt')
    thuoc_kho = fields.Many2one(comodel_name='nha.kho', string='Kho làm việc', store=True)


class NgayNghi(models.Model):
    _name = 'ngay.nghi'
    _rec_name = 'nhanvien'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Quản lý ngày nghỉ nhân viên'

    @api.model
    def create(self, vals):
        if vals.get('ma_phieu', ('New') == ('New')):
            vals['ma_phieu'] = self.env['ir.sequence'].next_by_code('phepnghi.code') or ('New')
            res = super(NgayNghi, self).create(vals)
            return res

    def _get_default_ly_do(self):
        result = """
        <div>
            <h1 class="text-center">Lý do xin nghỉ</h1>
            <ul>
                <li><h3>....</h3></li>
            <ul/>
        </div>"""
        return result

    ma_phieu = fields.Char(string='Mã phiếu', readonly=True)
    nhanvien = fields.Many2one(comodel_name='hr.employee', string='Nhân viên', track_visibility='onchange')
    ngay_viet_don = fields.Date(string='Ngày viết đơn', default=datetime.today(), readonly=True)
    ngay_xin_nghi = fields.Date(string='Ngày xin nghỉ', track_visibility='onchange')
    nghi_toi_ngay = fields.Date(string='Nghỉ tới ngày', track_visibility='onchange')
    ly_do = fields.Html(string='Lý do', default=_get_default_ly_do, track_visibility='onchange')
    state = fields.Selection([('0', 'Mới tạo'), ('1', 'Cho nghỉ'), ('2', 'Không cho nghỉ')], string='Trạng thái đơn',
                             default='0', track_visibility='onchange')
    pdf = fields.Binary(string='Chứng từ')
    thuoc_kho = fields.Many2one(comodel_name='nha.kho', related='nhanvien.thuoc_kho', store=True)

    def confirm(self):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ('Thông báo'),
                'message': 'Đã xác nhận cho nghỉ',
                'type': 'success',  # types: success,warning,danger,info
                'next': {'type': 'ir.actions.act_window_close'},
                'sticky': False,  # True/False will display for few seconds if false
            },
        }
        self.write({'state': '1'})
        return notification

    def cancel(self):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ('Thông báo'),
                'message': 'Đã xác nhận không cho nghỉ',
                'type': 'danger',  # types: success,warning,danger,info
                'next': {'type': 'ir.actions.act_window_close'},
                'sticky': False,  # True/False will display for few seconds if false
            },
        }
        self.write({'state': '2'})
        return notification

    def unlink(self):
        for record in self:
            if record.state in ('1', '2'):
                raise UserError('Không được xóa ở trạng thái này')
        else:
            for rec in self:
                return super(NgayNghi, rec).unlink()


class UngLuong(models.Model):
    _name = 'ung.luong'
    _description = 'ứng lương'

    date_create = fields.Date(string='Ngày làm đơn', readonly=True, default=datetime.today())
    date_confirm = fields.Date(string='Ngày duyệt đơn', readonly=True)
    nguoi_ung = fields.Many2one(comodel_name='hr.employee', string='Người nhận')
    so_tien = fields.Integer(string='Số tiền ứng')
    status = fields.Selection([('0', 'Nháp'), ('1', 'Xác nhận'), ('2', 'Từ chối',)], string='Trạng thái đơn',
                              default='0')
    nguoi_xacnhan = fields.Many2one(comodel_name='res.users', string='Tài khoản xác nhận', readonly=True)

    def confirm(self):
        if self.status != '0':
            raise UserError('Làm mới trình duyệt')
        self.status = '1'
        self.nguoi_xacnhan = self.env.user
        self.date_confirm = datetime.today()

    def cancel(self):
        if self.status != '0':
            raise UserError('Làm mới trình duyệt')
        self.status = '2'
        self.date_confirm = datetime.today()
