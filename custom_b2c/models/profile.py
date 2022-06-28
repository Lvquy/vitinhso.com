# -*- coding: utf-8 -*-


from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
import random


class UserProfile(models.Model):
    _name = 'user.profile'
    _description = 'Profile Users'
    _rec_name = 'name'

    name = fields.Char(string='Name')
    gender = fields.Selection([('male', 'Nam'), ('femel', 'Nữ'), ('other', 'Khác')], string='Giới tính')
    birthday = fields.Date(string='Ngày sinh')
    email = fields.Char(string='Email')
    mobile = fields.Char(string='Mobile')
    img = fields.Binary(string='Ảnh đại diện')
    reward_points = fields.Integer(string='Điểm thưởng', readonly=True)
    wallet = fields.Char(string='Ví cá nhân', default=lambda self: ('New'))
    wallet_balance = fields.Integer(string='Số dư (VNĐ)', readonly=True)
    co_phan = fields.Many2many(comodel_name='co.phan', string='Cổ phần', compute='get_cp')
    kyc_status = fields.Selection([('0', 'Chưa kyc'), ('1', 'Đã kyc')], string='Trạng thái kyc', default='0')
    bank_id = fields.One2many(comodel_name='line.bank', inverse_name='of_user', string='Tài khoản ngân hàng')
    login = fields.Many2one(comodel_name='res.users', string='Tài khoản đăng nhập', readonly=True)
    is_adm_cty = fields.Boolean(string='Là tài khoản CTY', default=False, readonly=False)
    total_cp = fields.Integer(string='Tổng cổ phần hiện có', compute='get_total_cp')
    total_cp_tk = fields.Integer(string='Cổ phần đang tiết kiệm', compute='get_total_cp_tk')
    total_cp_dt = fields.Integer(string='Cổ phần đang đầu tư', compute='get_total_cp_dt')
    total_cp_lock = fields.Integer(string='Cổ phần đang bị khóa', compute='get_total_cp_lock')
    total_cp_ready = fields.Integer(string='Cổ phần đang sẵn sàng', compute='get_total_cp_ready')
    total_cp_wait = fields.Integer(string='Cổ phần đang chờ', compute='get_total_cp_wait')
    reward_cp = fields.One2many(comodel_name='line.reward2cp', inverse_name='name', string='Đổi điểm lấy cổ phần')
    chuyen_points = fields.One2many(comodel_name='trans.points', inverse_name='account_self', string='Chuyển điểm', readonly=True)
    lock_edit = fields.Boolean(string='Khóa sửa thông tin',default=False, readonly=True)
    otp = fields.Char(string='Mã OTP xác thực')
    otp_save = fields.Char(string='OTP SYSTEM', default=random.randrange(100000, 999999))

    def action_lock_edit(self):
        for rec in self:
            rec.lock_edit = True
            rec.otp = ' '
            rec.otp_save = random.randrange(100000, 999999)
    def unlock_edit(self):
        for rec in self:
            if rec.otp == rec.otp_save:
                rec.lock_edit = False
                rec.otp = ' '
            else:
                notification = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': ('Thông báo'),
                        'message': 'Lỗi, sai mã OTP',
                        'type': 'success',  # types: success,warning,danger,info
                        'next': {'type': 'ir.actions.act_window_close'},
                        'sticky': False,  # True/False will display for few seconds if false
                    },
                }
                return notification

    def send_otp(self):
        otp = random.randrange(100000, 999999)
        for rec in self:
            rec.otp = ' '
            rec.otp_save = otp
            template_id = rec.env.ref('custom_b2c.mail_template_b2c_otp_edit_profile1').id
            template = rec.env['mail.template'].browse(template_id)
            template.send_mail(rec.id, force_send=True)
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ('Thông báo'),
                'message': 'Đã gửi mã OTP vào email',
                'type': 'success',  # types: success,warning,danger,info
                'next': {'type': 'ir.actions.act_window_close'},
                'sticky': False,  # True/False will display for few seconds if false
            },
        }
        return notification

    def get_total_cp(self):
        for rec in self:
            count = int(len(rec.co_phan))
            rec.total_cp = count

    def get_total_cp_dt(self):
        for rec in self:
            domain = ['&', ('of_user', '=', rec.id), ('status', '=', '2')]
            rec.total_cp_dt = int(rec.env['co.phan'].search_count(domain))

    def get_total_cp_tk(self):
        for rec in self:
            domain = ['&', ('of_user', '=', rec.id), ('status', '=', '3')]
            rec.total_cp_tk = int(rec.env['co.phan'].search_count(domain))

    def get_total_cp_lock(self):
        for rec in self:
            domain = ['&', ('of_user', '=', rec.id), ('status', '=', '4')]
            rec.total_cp_lock = int(rec.env['co.phan'].search_count(domain))

    def get_total_cp_ready(self):
        for rec in self:
            domain = ['&', ('of_user', '=', rec.id), ('status', '=', '1')]
            rec.total_cp_ready = int(rec.env['co.phan'].search_count(domain))

    def get_total_cp_wait(self):
        for rec in self:
            domain = ['&', ('of_user', '=', rec.id), ('status', '=', '6')]
            rec.total_cp_wait = int(rec.env['co.phan'].search_count(domain))

    def get_cp(self):
        for rec in self:
            domain = ('of_user', '=', rec.id)
            rec.co_phan = rec.env['co.phan'].search([domain])

    @api.model
    def create(self, vals):
        if vals.get('wallet', ('New') == ('New')):
            vals['wallet'] = self.env['ir.sequence'].next_by_code('wallet.code') or ('New')
            res = super(UserProfile, self).create(vals)
        return res

    def reward2cp(self):
        check_setting = self.env['ir.config_parameter'].sudo().get_param('custom_b2c.doi_cp')
        if check_setting:
            return {
                'name': ('Đổi điểm lấy cổ phần'),
                'type': 'ir.actions.act_window',
                'res_model': 'line.reward2cp',
                'view_mode': 'form',
                'target': 'new',
            }
        else:
            raise UserError('Công ty đang đóng chức năng này \n Liên hệ admin để được biết thêm')


class LineBank(models.Model):
    _name = 'line.bank'

    name = fields.Char(string='Tên ngân hàng', required=True)
    bank_no = fields.Char(string='Số tài khoản', required=True)
    user_bank = fields.Char(string='Chủ tài khoản', required=True)
    of_user = fields.Many2one(comodel_name='user.profile', string='Chủ tài khoản')


class LineReward2CP(models.Model):
    _name = 'line.reward2cp'

    @api.onchange('qty_cp')
    def get_value_price(self):
        default = int(self.env['ir.config_parameter'].sudo().get_param('custom_b2c.price_unit_r2cp'))
        self.price_unit = default

    date = fields.Datetime(string='Ngày đổi', default=datetime.today(), readonly=True)
    qty_cp = fields.Integer(string='Số lượng cổ phần qui đổi', required=True)
    price_unit = fields.Integer(string='Tỉ lệ quy đổi điểm / 1 cổ phần', required=True, compute=get_value_price)
    total_reward = fields.Integer(string='Số điểm cần phải trả', compute='get_total', readonly=True)
    name = fields.Many2one(comodel_name='user.profile', string='Tài khoản đổi', readonly=True)
    status = fields.Selection([('0', 'Nháp'), ('1', 'Đã đổi'), ('2', 'Hủy')], string='Trạng thái', default='0')

    @api.onchange('qty_cp', 'price_unit')
    def get_total(self):
        for rec in self:
            rec.total_reward = rec.price_unit * rec.qty_cp

    def confirm_1(self):
        CP_ALL = self.env['co.phan'].search_count([('status', '=', '0')])
        if self.qty_cp > CP_ALL:
            raise UserError('Số lượng cổ phần cty không đủ, liên hệ với admin để được tư vấn thêm')

        Points = self.env.user.user_profile.reward_points
        if self.total_reward > Points:
            raise UserError('Số điểm không đủ để đổi!')
        else:
            self.env.user.user_profile.reward_points -= self.total_reward
            self.status = '1'
            CP = self.env['co.phan'].search([('status', '=', '0')], limit=self.qty_cp)
            for rec in CP:
                # rec.of_user = rec.env.user.user_profile.id
                # rec.status = '1'
                rec.write({'of_user': rec.env.user.user_profile.id,
                           'status': '1'})
                self.env['log.cp'].create({
                    'name': rec.id,
                    'code_giaodich': 'Đổi điểm lấy cổ phần',
                    'to_user': rec.env.user.user_profile.id
                })

    def confirm_2(self):
        for rec in self:
            rec.status = '2'


class NapRutTien(models.Model):
    _name = 'nap.rut.tien'

    code = fields.Char(string='Mã chứng từ', default=lambda self: ('New'), readonly=True)
    state = fields.Selection(
        [('0', 'Nháp'),('otp','Đã gửi mã OTP'), ('1', 'Xác nhận giao dịch'), ('2', 'Thành công'), ('3', 'Đã hủy')],
        string='Trạng thái', default='0')
    account = fields.Many2one(comodel_name='user.profile', string='Tài khoản', required=True,
                              default=lambda self: self.env.user.user_profile)
    self_account = fields.Many2one(comodel_name='user.profile', string='Người tạo',
                                   default=lambda  self: self.env.user.user_profile, readonly=True)
    wallet = fields.Char(string='Ví tài khoản giao dịch', store=True, related='account.wallet')
    sotien = fields.Integer(string='Số tiền')
    create_date = fields.Datetime(string='Ngày tạo đơn', default=datetime.today())
    note = fields.Text(string='Note')
    chung_tu = fields.Binary(string='Chứng từ')
    type_phieu = fields.Selection([('nap', 'Nạp tiền vào ví'), ('rut', 'Rút tiền mặt')], string='Kiểu phiếu',
                                  required=True, default='nap')
    otp = fields.Char(string='Mã OTP xác thực')
    otp_save = fields.Char(string='OTP SYSTEM', default=random.randrange(100000, 999999))

    def get_self(self):
        for rec in self:
            rec.account = rec.env.user.user_profile

    @api.onchange('type_phieu')
    def type_rut(self):
        for rec in self:
            if rec.type_phieu == 'rut':
                rec.account = rec.env.user.user_profile

    def send_otp(self):
        otp = random.randrange(100000, 999999)
        for rec in self:
            rec.otp_save = otp
            template_id = rec.env.ref('custom_b2c.mail_template_b2c_otp_nr_tien').id
            template = rec.env['mail.template'].browse(template_id)
            template.send_mail(rec.id, force_send=True)
            rec.state = 'otp'
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ('Thông báo'),
                'message': 'Đã gửi mã OTP vào email',
                'type': 'success',  # types: success,warning,danger,info
                'next': {'type': 'ir.actions.act_window_close'},
                'sticky': False,  # True/False will display for few seconds if false
            },
        }
        return notification

    def confirm(self):
        for rec in self:
            if rec.state != 'otp':
                raise UserError("Vui lòng làm mới trình duyệt")
            if rec.otp == rec.otp_save:
                rec.state = '1'
                notification = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': ('OTP Thông báo'),
                        'message': 'Xác thực thành công',
                        'type': 'success',  # types: success,warning,danger,info
                        'next': {'type': 'ir.actions.act_window_close'},
                        'sticky': False,  # True/False will display for few seconds if false
                    },
                }
                return notification
            else:
                notification = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': ('OTP Thông báo'),
                        'message': 'Sai mã OTP',
                        'type': 'warning',  # types: success,warning,danger,info
                        'next': {'type': 'ir.actions.act_window_close'},
                        'sticky': False,  # True/False will display for few seconds if false
                    },
                }
                return notification

    def done(self):
        # xác nhận giao dịch thành công
        for rec in self:
            if rec.state != '1':
                raise UserError('Làm mới trình duyệt')
            if rec.type_phieu == 'nap':
                user_profile = rec.env['user.profile'].search([('wallet', '=', rec.wallet)], limit=1)
                user_profile.wallet_balance += rec.sotien
            if rec.type_phieu == 'rut':
                user_profile = rec.env['user.profile'].search([('wallet', '=', rec.wallet)], limit=1)
                if user_profile.wallet_balance < rec.sotien:
                    raise UserError('Số dư không đủ')
                user_profile.wallet_balance -= rec.sotien
            rec.state = '2'

    def cancel(self):
        for rec in self:
            if rec.state == '2':
                raise UserError('Làm mới trình duyệt')
            rec.state = '3'

    @api.model
    def create(self, vals):
        if vals.get('code', ('New') == ('New')):
            vals['code'] = self.env['ir.sequence'].next_by_code('napruttien.code') or ('New')
            res = super(NapRutTien, self).create(vals)
            return res


class TransferPoints(models.Model):
    _name = 'trans.points'

    date_create = fields.Datetime(string='Ngày tạo', default=datetime.today())
    account_thu_huong = fields.Many2one(comodel_name='user.profile', string='Tài khoản nhận', required=True)
    wallet = fields.Char(related='account_thu_huong.wallet', string='Ví cá nhân')
    account_self = fields.Many2one(comodel_name='user.profile', string='Tài khoản gửi',readonly=True,
                                   default=lambda self:self.env.user.user_profile)
    qty_points = fields.Integer(string='Số điểm')
    state = fields.Selection([('0', 'Nháp'),('otp','Đã gửi mã OTP'), ('1', 'Đã chuyển')], string='Trạng thái', default='0', readonly=True)
    otp = fields.Char(string='Mã OTP xác thực')
    otp_save = fields.Char(string='OTP SYSTEM', default=random.randrange(100000, 999999))
    note = fields.Text(string='Note')

    def send_otp(self):
        otp = random.randrange(100000, 999999)
        for rec in self:
            rec.otp_save = otp
            template_id = rec.env.ref('custom_b2c.mail_template_b2c_otp').id
            template = rec.env['mail.template'].browse(template_id)
            template.send_mail(rec.id, force_send=True)
            rec.state = 'otp'
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ('Thông báo'),
                'message': 'Đã gửi mã OTP vào email',
                'type': 'success',  # types: success,warning,danger,info
                'next': {'type': 'ir.actions.act_window_close'},
                'sticky': False,  # True/False will display for few seconds if false
            },
        }
        return notification

    def confirm(self):
        for rec in self:
            if rec.otp == rec.otp_save:
                Total_Wallet= rec.account_self.reward_points
                if rec.qty_points > Total_Wallet:
                    raise UserError('Số điểm không đủ')
                else:
                    rec.account_self.reward_points -= rec.qty_points
                    rec.account_thu_huong.reward_points += rec.qty_points
                rec.state = '1'
                rec.date_create = datetime.today()
            else:
                # raise UserError('Sai mã OTP')
                notification = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': ('OTP Thông báo'),
                        'message': 'Sai mã OTP',
                        'type': 'danger',  # types: success,warning,danger,info
                        'next': {'type': 'ir.actions.act_window_close'},
                        'sticky': False,  # True/False will display for few seconds if false
                    },
                }
                return notification

class TransWallet(models.Model):
    _name = 'trans.wallet'
    _description = 'chuyen tien'

    date_create = fields.Datetime(string='Ngày tạo', default=datetime.today())
    account_thu_huong = fields.Many2one(comodel_name='user.profile', string='Tài khoản nhận', required=True)
    wallet = fields.Char(related='account_thu_huong.wallet', string='Ví cá nhân')
    account_self = fields.Many2one(comodel_name='user.profile', string='Tài khoản gửi', required=True,
                                   default = lambda self: self.env.user.user_profile, readonly=True)
    qty_wallet = fields.Integer(string='Số tiền (vnđ)')
    state = fields.Selection([('0', 'Nháp'),('otp','Đã gửi mã OTP'), ('1', 'Đã chuyển')], string='Trạng thái', default='0', readonly=True)
    otp = fields.Char(string='Mã OTP xác thực')
    otp_save = fields.Char(string='OTP SYSTEM', default=random.randrange(100000, 999999))
    note = fields.Text(string='Note')

    def send_otp(self):
        otp = random.randrange(100000, 999999)
        for rec in self:
            rec.state = 'otp'
            rec.otp_save = otp
            template_id = rec.env.ref('custom_b2c.mail_template_b2c_otp_wallet').id
            template = rec.env['mail.template'].browse(template_id)
            template.send_mail(rec.id, force_send=True)
            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': ('OTP Thông báo'),
                    'message': 'Đã gửi mã OTP, kiểm tra email',
                    'type': 'success',  # types: success,warning,danger,info
                    'next': {'type': 'ir.actions.act_window_close'},
                    'sticky': False,  # True/False will display for few seconds if false
                },
            }
            return notification

    def confirm(self):
        for rec in self:
            if rec.otp == rec.otp_save:
                Total_wallet_balance = rec.account_self.wallet_balance
                if rec.qty_wallet > Total_wallet_balance:
                    raise UserError('Số dư không đủ')
                else:
                    rec.account_self.wallet_balance -= rec.qty_wallet
                    rec.account_thu_huong.wallet_balance += rec.qty_wallet
                rec.state = '1'
                notification = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': ('OTP Thông báo'),
                        'message': 'Thành công',
                        'type': 'success',  # types: success,warning,danger,info
                        'next': {'type': 'ir.actions.act_window_close'},
                        'sticky': False,  # True/False will display for few seconds if false
                    },
                }
                return notification
            else:
                # raise UserError('Sai mã OTP')
                notification = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': ('OTP Thông báo'),
                        'message': 'Sai mã OTP',
                        'type': 'warning',  # types: success,warning,danger,info
                        'next': {'type': 'ir.actions.act_window_close'},
                        'sticky': False,  # True/False will display for few seconds if false
                    },
                }
                return notification