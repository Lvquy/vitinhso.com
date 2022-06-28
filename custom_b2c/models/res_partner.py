# -*- coding: utf-8 -*-



from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime

class Partner(models.Model):
    _inherit = ['res.partner']

    reward_points = fields.Integer('Điểm thưởng', readonly=True,track_visibility='onchange')
    date_cs_min  = fields.Date(string='Ngày chăm sóc gần nhất')
    nv_cs = fields.Many2one(comodel_name='res.users', string='Nhân viên chăm sóc gần nhất')
    date_cs_max  = fields.Date(string='Ngày cần chăm sóc tiếp theo')
    status_cs = fields.Selection([('0','Chưa chăm sóc'),('1','Đã chăm sóc'),('2','Cần chăm sóc ngay')],
                                 default='0',
                                 string='Trạng thái chăm sóc')
    is_cskh = fields.Boolean(string='Tới ngày CSKH', compute ='_compute_is_cskh')

    # get default -> error create new user
    # @api.model
    # def default_get(self, fields):
    #     vals = super(Partner, self).default_get(fields)
    #     VIETNAM = self.env['res.country'].search([('code','=','VN')],limit=1)
    #     vals['country_id'] = VIETNAM
    #     return vals

    @api.depends('date_cs_max')
    def _compute_is_cskh(self):
        for rec in self:
            is_cskh = False
            if rec.date_cs_max:
                today = datetime.today()
                if today.day >= rec.date_cs_max.day and today.month >= rec.date_cs_max.month and today.year >= rec.date_cs_max.year:
                    is_cskh = True
            rec.is_cskh = is_cskh

    def create_user_profile(self):
        User = self.env['res.users']
        UserProfile = self.env['user.profile']

        U = UserProfile.create({
            'name': self.name,
            'email': self.email,
            'img': self.image_1920,
            'reward_points': self.reward_points,
            'otp': '',

        })
        LOGIN = User.create({
            'name':self.name,
            'partner_id': self.id,
            'login':self.email,
            'user_profile':U.id,
        })
        U.write({'login':LOGIN.id})
        self.reward_points = 0

class cskh(models.Model):
    _name = 'cskh'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    date_recall = fields.Date(string='Ngày chăm sóc khách hàng',track_visibility='onchange', default=datetime.today(), required=True)
    date_next = fields.Date(string='Ngày chăm sóc tiếp theo',track_visibility='onchange', required=True)
    status_recall = fields.Selection([('0','Chưa chăm sóc'),('1','Đã chăm sóc')],
                                     string='Trạng thái chăm sóc',
                                     readonly=True,
                                     default='0',track_visibility='onchange')
    nv_cham_soc = fields.Many2one(comodel_name='res.users', string='Nhân viên chăm sóc', readonly=True,
                                  track_visibility='onchange')
    khach_hang_list = fields.One2many(comodel_name='line.cskh',inverse_name='ref_kh', string='Khách hàng')
    limit_kh = fields.Integer(string='Số lượng khách hàng muốn chăm sóc', required = True)

    def confirm(self):
        for rec in self:
            rec.status_recall = '1'
            rec.nv_cham_soc = rec.env.user
            for kh in rec.khach_hang_list:
                kh.khach_hang.nv_cs = rec.env.user
                kh.khach_hang.date_cs_min = datetime.today()
                kh.khach_hang.date_cs_max = rec.date_next
                kh.khach_hang.status_cs = '1'
    def update_date_cs(self):
        for rec in self:
            KH = rec.env['res.partner'].search([])
            for i in KH:

                today = datetime.today().strftime('%Y-%m-%d')
                if i.date_cs_max == False:
                    i.date_cs_max  = datetime.today()
                date_max = i.date_cs_max.strftime('%Y-%m-%d')
                if date_max <= today:
                    print(date_max, today)
                    i.status_cs = '2'
    def get_line_kh(self):
        self.update_date_cs()
        for rec in self:
            domain=['|',('status_cs','=','0'),('status_cs','=','2')]
            KH = rec.env['res.partner'].search(domain, limit =rec.limit_kh)
            for i in KH:
                rec.env['line.cskh'].create({
                    'khach_hang': i.id,
                    'ref_kh': rec.id,
                })


class LineCSKH(models.Model):
    _name = 'line.cskh'

    khach_hang = fields.Many2one(comodel_name='res.partner', string='Khách hàng',
                                 domain=['|',('status_cs','=','0'),('status_cs','=','2')], required=True)
    phone = fields.Char(string='Điện thoại', related='khach_hang.phone')
    status_cs = fields.Selection(string='Trạng thái chăm sóc', related='khach_hang.status_cs')
    nv_cs = fields.Many2one(string='Nhân viên chăm sóc gần nhất', related='khach_hang.nv_cs')
    ref_kh = fields.Many2one(comodel_name='cskh', string='Khách hàng')
    note = fields.Text(string='Note')

