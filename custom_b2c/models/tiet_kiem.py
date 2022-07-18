# -*- coding: utf-8 -*-


from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError


class TietKiem(models.Model):
    _name = 'tiet.kiem'
    _date_name = 'Gửi tiết kiệm cổ phần'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'state desc,end_date desc'
    _rec_name = 'code'

    code = fields.Char(string='Mã chứng từ', default=lambda self: ('New'), readonly=True)
    user_tk = fields.Many2one(comodel_name='user.profile', string='Người gửi',
                              default=lambda self: self.env.user.user_profile.id, readonly=True)
    ky_han = fields.Selection([('1', '1 tháng'), ('3', '3 tháng'), ('6', '6 tháng'), ('12', '12 tháng'),
                               ('18', '18 tháng'), ('24', '24 tháng'), ('36', '36 tháng')],
                              string='Kỳ hạn gửi', required=True, track_visibility='onchange')
    lai_suat = fields.Integer(string='Lãi suất (%)',
                              help='Nhập phần trăm lãi suất ví dụ 5% thì điền số 5',
                              required=True, track_visibility='onchange', readonly=True, compute='change_lai_suat'
                              )
    sl_cophan = fields.Integer(string='Số lượng cổ phần gửi', required=True, track_visibility='onchange')
    gia_cp = fields.Integer(string='Giá cổ phần', compute="_compute_gia_cp")
    thanh_vnd = fields.Integer(string='Quy đổi ra VNĐ', compute="_compute_thanh_vnd")
    note = fields.Text(string='Note')
    state = fields.Selection([('0', 'Nháp'), ('1', 'Đang gửi'), ('2', 'Đã thanh toán hợp đồng'), ('3', 'Đã hủy')],
                             string='Trạng thái', default='0')

    start_date = fields.Date(string='Ngày xác nhận gửi', default=datetime.today(), required=True)
    end_date = fields.Date(string='Ngày đáo hạn')
    log_tra_lai = fields.One2many(comodel_name='line.tralai', inverse_name='ref_tietkiem', string='Nhật ký trả lãi',
                                  readonly=True)
    cp_lai = fields.Integer(string='Lãi nhận được (vnđ)', compute='get_lai')
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.company)

    def _compute_gia_cp(self):
        for rec in self:
            rec.gia_cp = float(rec.env['ir.config_parameter'].sudo().get_param('custom_b2c.price_unit_cp'))

    @api.onchange('sl_cophan', 'gia_cp')
    def _compute_thanh_vnd(self):
        for rec in self:
            rec.thanh_vnd = int(rec.sl_cophan * rec.gia_cp)

    @api.onchange('lai_suat', 'ky_han', 'sl_cophan')
    def get_lai(self):
        for rec in self:
            rec.cp_lai = int((rec.lai_suat * rec.thanh_vnd) * 0.01)

    def _check_cp(self):
        CP = self.user_tk.total_cp_ready
        if self.sl_cophan > CP:
            raise UserError("Số lượng cổ phần bạn không đủ")

    def send_email(self):
        for rec in self:
            template_id = rec.env.ref('custom_b2c.mail_template_tiet_kiem').id
            template = rec.env['mail.template'].browse(template_id)
            template.send_mail(rec.id, force_send=True)

    def action_1(self):
        self._check_cp()
        if self.state not in ('0'):
            raise UserError("Vui lòng làm mới trình duyệt")
        self.start_date = datetime.today()
        self.send_email()
        self.state = '1'
        domain = ['&', ('status', '=', '1'), ('of_user', '=', self.user_tk.id)]
        CP = self.env['co.phan'].search(domain, limit=self.sl_cophan)
        for rec in CP:
            rec.status = '3'
            self.env['log.cp'].create({
                'name': rec.id,
                'code_giaodich': ('gửi tiết kiệm', self.code),
            })

    def action_2(self):
        today = datetime.today().date()
        end_date = self.end_date
        delta = (today - end_date)
        day = int(delta.days)
        if day >= 0:
            if self.state not in ('1'):
                raise UserError("Vui lòng làm mới trình duyệt")
            self.state = '2'
            domain = ['&', ('status', '=', '3'), ('of_user', '=', self.user_tk.id)]
            CP = self.env['co.phan'].search(domain, limit=self.sl_cophan)
            for rec in CP:
                rec.status = '1'
                self.env['log.cp'].create({
                    'name': rec.id,
                    'code_giaodich': ('thanh toán tiết kiệm', self.code),
                })
            # nhận lãi
            self.user_tk.wallet_balance += self.cp_lai
            for rec in self:
                rec.env['line.tralai'].create({
                    'ngay_tra': datetime.today(),
                    'nguoi_thu_huong': rec.user_tk.id,
                    'ref_tietkiem': rec.id,
                    'cp_lai': rec.cp_lai,
                    'state': '1',

                })
        else:
            # chưa tới ngày đáo hạn
            if self.state not in ('1'):
                raise UserError("Vui lòng làm mới trình duyệt")
            self.state = '2'
            domain = ['&', ('status', '=', '3'), ('of_user', '=', self.user_tk.id)]
            CP = self.env['co.phan'].search(domain, limit=self.sl_cophan)
            for rec in CP:
                rec.status = '1'
                self.env['log.cp'].create({
                    'name': rec.id,
                    'code_giaodich': ('thanh toán tiết kiệm', self.code),
                })
            for rec in self:
                rec.env['line.tralai'].create({
                    'ngay_tra': datetime.today(),
                    'nguoi_thu_huong': rec.user_tk.id,
                    'ref_tietkiem': rec.id,
                    'cp_lai': 0,
                    'state': '1',

                })

    def action_3(self):
        if self.state not in ('0'):
            raise UserError("Vui lòng làm mới trình duyệt")
        self.state = '3'

    @api.model
    def create(self, vals):
        global res
        if vals.get('code', ('New') == ('New')):
            vals['code'] = self.env['ir.sequence'].next_by_code('tietkiem.code') or ('New')
            res = super(TietKiem, self).create(vals)
        return res

    @api.onchange('ky_han')
    def change_lai_suat(self):
        for rec in self:
            lai_1 = int(rec.env['ir.config_parameter'].sudo().get_param('custom_b2c.lai_tk_1'))
            lai_3 = int(rec.env['ir.config_parameter'].sudo().get_param('custom_b2c.lai_tk_3'))
            lai_6 = int(rec.env['ir.config_parameter'].sudo().get_param('custom_b2c.lai_tk_6'))
            lai_12 = int(rec.env['ir.config_parameter'].sudo().get_param('custom_b2c.lai_tk_12'))
            lai_18 = int(rec.env['ir.config_parameter'].sudo().get_param('custom_b2c.lai_tk_18'))
            lai_24 = int(rec.env['ir.config_parameter'].sudo().get_param('custom_b2c.lai_tk_24'))
            lai_36 = int(rec.env['ir.config_parameter'].sudo().get_param('custom_b2c.lai_tk_36'))

            i = int(rec.ky_han)
            switcher = {
                1: lai_1,
                3: lai_3,
                6: lai_6,
                12: lai_12,
                18: lai_18,
                24: lai_24,
                36: lai_36
            }
            rec.lai_suat = switcher.get(i)


class TraLai(models.Model):
    _name = 'line.tralai'
    _description = 'Line Tra lai'

    ngay_tra = fields.Datetime(string='Ngày trả', default=datetime.today())
    cp_lai = fields.Integer(string='Số tiền lãi', compute='get_lai')
    nguoi_thu_huong = fields.Many2one(comodel_name='user.profile', readonly=True, string='Người thụ hưởng')
    ref_tietkiem = fields.Many2one(comodel_name='tiet.kiem', string='Name')
    state = fields.Selection([('0', 'Gửi yêu cầu'), ('1', 'Đã trả')], string='Trạng thái', default='0')

    def get_lai(self):
        self.cp_lai = int((self.ref_tietkiem.thanh_vnd * self.ref_tietkiem.lai_suat) * 0.01)


class CamCo(models.Model):
    _name = 'cam.co'
    _rec_name = 'code'
    _description = 'Cam co co phan'

    code = fields.Char(string='Mã phiếu', default=lambda self: ('New'), readonly=True)
    qty = fields.Integer(string='Số lượng cổ phần')
    thoi_gian = fields.Selection([('12', '12 Tháng'), ('24', '24 Tháng'), ('36', '36 Tháng')], string='Thời hạn cầm',
                                 default='12')
    gia_cp = fields.Integer(string='Giá cổ phần quy đổi hiện tại', readonly=True)
    so_tien = fields.Integer(string='Số tiền nhận được / Phải trả (VNĐ)', compute='compute_so_tien', readonly=True)
    nguoi_cam = fields.Many2one(comodel_name='res.users', string='Người cầm', default=lambda self: self.env.user,
                                readonly=True)
    state = fields.Selection([('0', 'Nháp'), ('1', 'Đã xác nhận'), ('2', 'Đã trả')], string='Trạng thái', default='0')
    ngay_cam = fields.Date(string='Ngày cầm cố', default=datetime.today())
    ngay_rut = fields.Date(string='Ngày rút cổ phần')

    @api.model
    def create(self, vals):
        global res
        if vals.get('code', ('New') == ('New')):
            vals['code'] = self.env['ir.sequence'].next_by_code('camco.code') or ('New')
            res = super(CamCo, self).create(vals)
        return res

    @api.onchange('qty')
    def compute_so_tien(self):
        for rec in self:
            rec.gia_cp = int(self.env['ir.config_parameter'].sudo().get_param('custom_b2c.price_unit_cp') or 0)
            rec.so_tien = rec.gia_cp * rec.qty

    def confirm(self):
        for rec in self:
            if rec.state == '0':
                rec.state = '1'
                if rec.nguoi_cam.user_profile.total_cp_ready >= rec.qty:
                    CP_READY_USER = rec.env['co.phan'].search(
                        ['&', ('status', '=', '1'), ('of_user', '=', rec.nguoi_cam.user_profile.id)], limit=rec.qty)
                    for cp in CP_READY_USER:
                        cp.status = '4'
                    rec.nguoi_cam.user_profile.wallet_balance += rec.so_tien
                else:
                    raise UserError('Số cổ phần sẵn sàng không đủ')
            else:
                raise UserError("Làm mới trình duyệt")

    def update_gia_cp(self):
        for rec in self:
            rec.gia_cp = int(self.env['ir.config_parameter'].sudo().get_param('custom_b2c.price_unit_cp') or 0)
            rec.so_tien = rec.gia_cp * rec.qty

    def done(self):
        # chuộc cổ phần
        for rec in self:
            rec.update_gia_cp()
            if rec.state == '1':
                rec.state = '2'
                rec.ngay_rut = datetime.today()
                wallet_balance = rec.nguoi_cam.user_profile.wallet_balance
                if wallet_balance >= rec.so_tien:
                    rec.nguoi_cam.user_profile.wallet_balance -= rec.so_tien
                    CP_LOCK_USER = rec.env['co.phan'].search(
                        ['&', ('status', '=', '4'), ('of_user', '=', rec.nguoi_cam.user_profile.id)], limit=rec.qty)
                    for cp in CP_LOCK_USER:
                        cp.status = '1'
                else:
                    raise UserError("Số tiền không đủ")
            else:
                raise UserError("Làm mới trình duyệt")
