# -*- coding: utf-8 -*-



from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import *


class GiaoDichCoPhan(models.Model):
    _name = 'giaodich.cp'
    _description = 'Giao dịch cổ phần'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def get_default_price(self):
        default = int(self.env['ir.config_parameter'].sudo().get_param('custom_b2c.price_unit_cp') or 0)
        return default

    @api.onchange('price_unit', 'qty')
    def get_price_total(self):
        for rec in self:
            rec._check_qty()
            rec.price_total = rec.price_unit*rec.qty

    code = fields.Char(readonly=True, default=lambda self: ('New'), string='Mã giao dịch')
    state = fields.Selection([('0','Nháp'),('1','Đang bán'),('2','Đang giao dịch'),('3','GD thành công'),('4','GD thất bại'),('5','Đã hủy')],
                             string='Trạng thái',default='0',track_visibility='onchange')
    create_date = fields.Datetime(string='Ngày tạo lệnh', default=datetime.today(),readonly=True)
    user_create = fields.Many2one(comodel_name='user.profile', string='Người tạo lệnh', default=lambda self: self.env.user.user_profile, readonly=True)
    note = fields.Text(string='Note')
    price_unit = fields.Integer(string='Đơn giá/1 Cổ phần(vnđ)',track_visibility='onchange', default=get_default_price)
    price_total = fields.Integer(string='Tổng tiền', compute='get_price_total',track_visibility='onchange')
    qty = fields.Integer(string='Số lượng cổ phần giao dịch', default=0,track_visibility='onchange')
    cus_order = fields.Many2one(comodel_name='user.profile',string='Người mua', readonly=True,track_visibility='onchange')
    pur_order = fields.Many2one(comodel_name='user.profile',string='Người bán', readonly=True,track_visibility='onchange')
    chung_tu = fields.Binary(string='Chứng từ',track_visibility='onchange')
    tras_date = fields.Datetime(string='Ngày giao dịch', readonly=True)
    user_confirm = fields.Many2one(comodel_name='res.users', string='Người bảo lãnh', readonly=True)
    phi_giao_dich = fields.Integer(string='Phí giao dịch (% Tổng bill)', help='Phí giao dịch theo % tổng bill',compute='get_phigd')
    total_bill = fields.Integer(string='Tổng bill phải trả', compute='get_total_bill')
    type_gd = fields.Selection([('sale','Bán'),('purchase','Mua')],string='Kiểu giao dịch', default='sale', required=True)

    @api.onchange('price_total','phi_giao_dich')
    def get_total_bill(self):
        for rec in self:
            rec.total_bill = rec.price_total + rec.phi_giao_dich

    def get_phigd(self):
        for rec in self:
            PHI = rec.env['ir.config_parameter'].sudo().get_param('custom_b2c.phi_giao_dich')
            rec.phi_giao_dich = (PHI*rec.price_total)*0.01


    def get_admin_bank_num(self):
        domain = [('is_adm_cty','=',True)]
        ADMIN = self.env['user.profile'].search(domain,limit=1).bank_id
        for rec in ADMIN:
            return  rec.bank_no
    def get_admin_bank_name(self):
        domain = [('is_adm_cty','=',True)]
        ADMIN = self.env['user.profile'].search(domain,limit=1).bank_id
        for rec in ADMIN:
            return  rec.name
    def get_admin_bank_user(self):
        domain = [('is_adm_cty','=',True)]
        ADMIN = self.env['user.profile'].search(domain,limit=1).bank_id
        for rec in ADMIN:
            return  rec.user_bank


    bank_num = fields.Char(string='Số tài khoản', readonly=True, default=get_admin_bank_num)
    bank_name = fields.Char(string='Tên ngân hàng', readonly=True,default=get_admin_bank_name)
    bank_user = fields.Char(string='Chủ tài khoản', readonly=True, default=get_admin_bank_user)


    def get_admin_bank_num(self):
        domain = [('is_adm_cty','=',True)]
        ADMIN = self.env['user.profile'].search(domain,limit=1).bank_id
        for rec in ADMIN:
            self.bank_user = rec.user_bank
            self.bank_name = rec.name
            self.bank_num = rec.bank_no


    def _check_qty(self):
        if self.qty <=0:
            self.qty = 1

    @api.model
    def create(self, vals):
        if vals.get('code', ('New') == ('New')):
            vals['code'] = self.env['ir.sequence'].next_by_code('giaodichcp.code') or ('New')
            res = super(GiaoDichCoPhan, self).create(vals)
        return res

    def action_sale(self):
        self._check_qty()
        if self.user_create:
            CP = self.env['co.phan'].search_count(['&',('of_user','=',self.user_create.id),('status','=','1')])
            if self.qty > CP:
                self.qty = CP
                # raise UserError('Bạn chỉ có %s số lượng cổ phần' %CP)
                notification = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': ('Thông báo'),
                        'message': 'Cổ phần bạn đang có là: %s' %CP,
                        'type': 'warning',  # types: success,warning,danger,info
                        'next': {'type': 'ir.actions.act_window_close'},
                        'sticky': False,  # True/False will display for few seconds if false
                    },
                }
                return notification
        else:
            # raise UserError('Chưa thiết lập tài khoản giao dịch cho tài khoản này \n liên hệ người quản trị để biết thêm.')
            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': ('Thông báo'),
                    'message': 'Chưa thiết lập tài khoản giao dịch cho tài khoản này \n liên hệ người quản trị để biết thêm.',
                    'type': 'warning',  # types: success,warning,danger,info
                    'next': {'type': 'ir.actions.act_window_close'},
                    'sticky': False,  # True/False will display for few seconds if false
                },
            }
            return notification
        self.state = '1'

    def action_confirm_sale(self):
        # xác nhận mua cổ phần này
        for rec in self:
            if rec.state not in ('1'):
                raise UserError('Vui lòng làm mới trình duyệt')
            if rec.env.user.user_profile:
                Curren_user = rec.env.user.user_profile
                if rec.type_gd == 'sale':
                    rec.cus_order = Curren_user.id
                else:
                    rec.pur_order = Curren_user.id
                rec.state='2'
            else:
                notification = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': ('Thông báo'),
                        'message': 'Chưa thiết lập tài khoản giao dịch cho tài khoản này \n liên hệ người quản trị để biết thêm.',
                        'type': 'warning',  # types: success,warning,danger,info
                        'next': {'type': 'ir.actions.act_window_close'},
                        'sticky': False,  # True/False will display for few seconds if false
                    },
                }
                return notification

    def action_cancel(self):
        if self.state not in ('0','1'):
            raise UserError('Vui lòng làm mới trình duyệt')
        self.state = '5'

    def action_tras_true(self):
        # xác nhận giao dịch thành công
        CP = self.env['co.phan'].search_count([('of_user', '=', self.user_create.id)])
        if self.qty > CP:
            raise UserError('Số lượng cổ phần hiện có chỉ còn %s' % CP)
        else:
            self.user_confirm = self.env.user.id
            CP = self.env['co.phan'].search([('of_user', '=', self.user_create.id)], limit=self.qty)
            if self.type_gd == 'sale':
                # lệnh bán
                for rec in CP:
                    rec.write({'of_user': self.cus_order.id,
                               'status':'1'})
                    self.env['log.cp'].create({
                        'name': rec.id,
                        'code_giaodich': self.code,
                        'from_user': self.user_create.id,
                        'to_user': self.cus_order.id
                    })
            else:
                # lệnh mua
                for rec in CP:
                    rec.write({'of_user': self.pur_order.id,
                               'status':'1'})
                    self.env['log.cp'].create({
                        'name': rec.id,
                        'code_giaodich': self.code,
                        'from_user': self.user_create.id,
                        'to_user': self.pur_order.id
                    })
            self.state = '3'
            self.tras_date = datetime.today()

            REPORT_B2C = self.env['report.b2c']
            REPORT_B2C.create({
                'ln_phi_giao_dich_cp': self.phi_giao_dich
            })


    def action_tras_false(self):
        if self.state not in '3':
            raise UserError('Làm mới trình duyệt')
        self.state = '4'





