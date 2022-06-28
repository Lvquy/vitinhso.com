# -*- coding: utf-8 -*-



from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import UserError

class Dautu(models.Model):
    _name = 'dau.tu'
    _description = 'Danh mục đầu tư'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string='Tên gói đầu tư', required=True)
    thoi_han = fields.Selection([('1','1 tháng'),('3','3 tháng'),('6','6 tháng'),('12','12 tháng')],
                                string='Thời gian đầu tư', default='1', help='Thời hạn đầu tư tính từ ngày đóng',
                                required=True, track_visibility='onchange')
    start_date = fields.Datetime(string='Ngày mở',required=True, track_visibility = 'onchange', default=datetime.today())
    close_date = fields.Datetime(string='Ngày đóng dự kiến',required=True,track_visibility = 'onchange')

    lai_suat = fields.Integer(string='Lãi suất (%)',required=True,track_visibility = 'onchange')
    code_dautu = fields.Char(string='Mã gói đầu tư',track_visibility = 'onchange', readonly=True,
                             default=lambda self: ('New'))
    state = fields.Selection([('0','Nháp'),('1','Đang nhận cổ đông'),('2','Đã đóng (Đang đầu tư)'),('3','Hoàn thành đầu tư')],
                             string='Trạng thái gói đầu tư',track_visibility = 'onchange', default='0')
    share_holder = fields.One2many(comodel_name='line.dautu',inverse_name='ref_dautu',string='Cổ đông tham gia',
                                   track_visibility = 'onchange', ondelete="cascade" )
    catg_dautu = fields.Selection([('0','Tiền số'),('1','Bất động sản')],string='Danh mục đầu tư',
                                  default='0', required=True, track_visibility = 'onchange')
    gia_trungbinh = fields.Float(string='Giá trung bình', compute='get_gia_tb',track_visibility = 'onchange')
    gia_ban = fields.Float(string='Giá bán',track_visibility = 'onchange')
    lenh_dautu = fields.One2many(comodel_name='line.log', inverse_name='ref_dautu',string='Lệnh đầu tư')
    total_cp = fields.Integer(string='Tổng cổ phần',compute='get_total_cp')
    gia_tri = fields.Integer(string='Tương đương(VNĐ)', compute='get_total_gt')
    to_usd = fields.Float(string='Tương đương(USD)')
    lai_lo = fields.Float(string='Lãi/Lỗ', compute='get_lai_lo')
    chung_tu = fields.Html(string='Hình ảnh chứng từ liên quan')
    done_date = fields.Datetime(string='Ngày hoàn thành đầu tư')
    so_tien_lai = fields.Integer(string='Số tiền mặt lãi (vnđ)')

    @api.onchange('gia_trungbinh','gia_ban')
    def get_lai_lo(self):
        for rec in self:
            rec.lai_lo = rec.gia_ban - rec.gia_trungbinh

    @api.onchange('total_cp')
    def get_total_gt(self):
        for rec in self:
            gia_cp = rec.env['ir.config_parameter'].sudo().get_param('custom_b2c.price_unit_cp')
            rec.gia_tri = rec.total_cp*gia_cp

    @api.onchange('share_holder')
    def get_total_cp(self):
        for rec in self:
            if rec.share_holder:
                for l in rec.share_holder:
                    rec.total_cp += l.sl_dautu
            else:
                rec.total_cp = 0


    @api.onchange('lenh_dautu')
    def get_gia_tb(self):
        Tong = 0
        sl = 0

        for line in self.lenh_dautu:
            if line.state == '1':
                Tong += line.gia_mua*line.so_luong
                sl += line.so_luong
        if sl >0:
            self.gia_trungbinh = Tong/sl
        else:
            self.gia_trungbinh =0
    @api.model
    def create(self, vals):
        if vals.get('code_dautu', ('New') == ('New')):
            vals['code_dautu'] = self.env['ir.sequence'].next_by_code('dautu.code') or ('New')
            res = super(Dautu, self).create(vals)
        return res

    def action_1(self):
        if self.state not in '0':
            raise UserError("Vui lòng làm mới trình duyệt")
        # state = đang nhận cổ đông
        self.state = '1'
    def action_2(self):
        if self.state not in '1':
            raise UserError("Vui lòng làm mới trình duyệt")
        # state = đã đóng (đang tiến hành đầu tư)
        self.state = '2'

        for rec in self.share_holder:
            domain = ['&',('status', '=', '6'),('of_user','=',rec.share_holder.id)]
            CP = self.env['co.phan'].search(domain,limit=rec.sl_dautu)
            for l in CP:
                l.status = '2'


    def action_3(self):
        if self.state not in '2':
            raise UserError("Vui lòng làm mới trình duyệt")
        # state = hoàn thành chu kỳ đầu tư
        # nhận cp gốc
        for rec in self.share_holder:
            domain = ['&',('status', '=', '2'),('of_user','=',rec.share_holder.id)]
            domain_lai = [('status', '=', '0')]
            CP = self.env['co.phan'].search(domain,limit=rec.sl_dautu)
            for l in CP:
                l.status = '1'

            # nhận lãi
            rec.share_holder.wallet_balance += rec.lai_cp
        self.state = '3'
        self.done_date = datetime.today()
        REPORT_B2C = self.env['report.b2c']
        REPORT_B2C.create({
            'ln_dautu': self.so_tien_lai
        })


    def joined(self):
        return {
            'name': ('Đầu tư cổ phần'),
            'type': 'ir.actions.act_window',
            'res_model': 'line.dautu',
            'view_mode': 'form',
            'target': 'new',
        }

    def cancel_join(self):
        if self.state not in '1':
            raise UserError("Vui lòng làm mới trình duyệt")
        Curent_user = self.env.user.user_profile
        id_dautu = self.id
        domain_1 = [('of_user','=',Curent_user.id),('status','=','6')]

        domain = ['&', ('share_holder', '=', Curent_user.id), ('ref_dautu', '=', id_dautu)]
        id_dautu_for_user = self.env['line.dautu'].search(domain)
        cp_wait = self.env['co.phan'].search(domain_1, limit=id_dautu_for_user.sl_dautu)
        for l in cp_wait:
            l.status ='1'
        id_dautu_for_user.unlink()

    @api.onchange('share_holder')
    def _check_double_line(self):
        for order in self.share_holder:
            line = self.share_holder.filtered(lambda l: l.share_holder == order.share_holder)
            if len(line) > 1:
                raise UserError('Bạn đã tham gia rồi')
                break

class LineDautu(models.Model):
    _name = 'line.dautu'

    share_holder = fields.Many2one(comodel_name='user.profile', string='Người đầu tư')
    sl_dautu = fields.Integer(string='Số lượng cổ phần đầu tư')
    join_date = fields.Datetime(stirng='Ngày tham gia', default=datetime.today(),readonly=True)
    ref_dautu = fields.Many2one(comodel_name='dau.tu',string='Đầu tư ID')
    cp2_vnd =fields.Integer(string='Quy ra VNĐ', compute='_compute_cp2_vnd')
    lai_cp = fields.Integer(string='Lãi nhận được (vnđ)', compute='get_lai')


    @api.onchange('sl_dautu')
    def _compute_cp2_vnd(self):
        for rec in self:
            gia_cp = int(rec.env['ir.config_parameter'].sudo().get_param('custom_b2c.price_unit_cp'))
            rec.cp2_vnd = gia_cp*rec.sl_dautu

    @api.onchange('sl_dautu','share_holder')
    def get_lai(self):
        for rec in self:
            rec.lai_cp = int((rec.cp2_vnd*rec.ref_dautu.lai_suat)*0.01)
    def _check_cp_ready(self):
        Curent_user = self.env.user.user_profile
        domain = ['&', ('of_user', '=', Curent_user.id), ('status', '=', '1')]
        cp_ready = int(self.env['co.phan'].search_count(domain))
        if self.sl_dautu > cp_ready:
            raise UserError('Số lượng cổ phần sẵn sàng không đủ!')


    def _check_double_line(self):
        Curent_user = self.env.user.user_profile
        id_dautu = self.env.context.get('active_ids', [])
        domain = ['&',('share_holder','=',Curent_user.id),('ref_dautu','=',id_dautu)]
        id_dautu_for_user = self.search(domain)
        count = len(id_dautu_for_user)
        if count > 0:
            raise UserError('Bạn đã tham gia rồi!')

    def confirm(self):

        if self.sl_dautu <=0:
            raise UserError('Số lượng tối thiểu là 1 cổ phần')
        self._check_double_line()
        self._check_cp_ready()
        Curent_user = self.env.user.user_profile
        self.share_holder = Curent_user.id
        self.ref_dautu = self.env.context.get('active_ids', [])[0]

        domain = ['&',('of_user','=',Curent_user.id),('status', '=', '1')]
        CP = self.env['co.phan'].search(domain,limit=self.sl_dautu)
        for rec in CP:
            rec.status = '6'

class LineLog(models.Model):
    _name = 'line.log'
    _description = 'Chi tiết các lệnh đầu tư '

    img = fields.Binary(string='Hình ảnh')
    date = fields.Datetime(string='Ngày tạo lệnh', default=datetime.today())
    so_tien = fields.Float(string='Số tiền(USD)', compute='get_price')
    so_luong = fields.Float(string='Số lượng', required=True)
    gia_mua = fields.Float(string='Giá mua(USD)', required=True)
    state = fields.Selection([('0','Nháp'),('1','Đã xác nhận'),('2','Hủy')],string='Trạng thái lệnh',default='0')
    ref_dautu = fields.Many2one(comodel_name='dau.tu', string='Lệnh đầu tư')

    def confirm(self):
        self.state = '1'
    def cancel(self):
        self.state = '2'

    @api.depends('gia_mua','so_luong')
    def get_price(self):
        for rec in self:
            rec.so_tien = rec.so_luong*rec.gia_mua

    def unlink(self):
        for record in self:
            if record.state in ('1'):
                raise UserError('Không được xóa ở trạng thái này')
        else:
            for rec in self:
                return super(LineLog, rec).unlink()



