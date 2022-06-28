# -*- coding: utf-8 -*-


from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import UserError



class ThiCong(models.Model):
    _name = 'thi.cong'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Phiếu thi công công trình'

    @api.model
    def create(self, vals):
        if vals.get('ma_phieu', ('New') == ('New')):
            vals['ma_phieu'] = self.env['ir.sequence'].next_by_code('maphieu.code') or ('New')
            res = super(ThiCong, self).create(vals)
            return res

    ngay_batdau = fields.Date(string='Ngày bắt đầu', required=True, track_visibility='onchange',default=datetime.today())
    name = fields.Char(string='Tên Công Trình', track_visibility='onchange', required=True)
    customer = fields.Many2one(comodel_name='res.partner',string='Đối tác', required=True)
    vatlieu = fields.One2many(comodel_name='line.vatlieu', inverse_name='ref_vatlieu', string='Vật liệu thi công ')
    nhansu_thicong = fields.One2many(comodel_name='nhansu.thicong', inverse_name='cong_trinh', required=True, string='Nhân sự thi công')
    thoi_gian_hoanthanh = fields.Date(string='Thời gian dự kiến hoàn thành',required=True, track_visibility='onchange')
    tong_thu = fields.Integer(string='Tổng thu', track_visibility='onchange',required=True)
    truong_nhom = fields.Many2one(comodel_name='hr.employee', string='Trưởng nhóm phụ trách',required=True,
                                  help='Phải cấu hình địa chỉ Partner tương ứng',
                                  track_visibility='onchange')
    state = fields.Selection([('0', 'Nháp'), ('1', 'Đã xác nhận'), ('2', 'Đã hoàn thành'), ('3', 'Đã Hủy')],
                             string='Trạng thái', default='0', track_visibility='onchange')
    ma_phieu = fields.Char(string='Mã phiếu', required=True, copy=False, readonly=True, index=True,
                           default=lambda self: ('New'))
    note = fields.Text(string='Note')
    location_id = fields.Many2one(comodel_name='stock.location', string='Lấy tại kho',required=True)
    stock_picking_type = fields.Many2one(comodel_name='stock.picking.type',string='Kiểu phiếu',required=True)
    delivery_count = fields.Integer(string='Phiếu xuất kho')
    ctag_thicong = fields.Selection([('1','Danh mục 1...'),('2','Danh mục 2...'),('3','Danh mục 3...')],string='Danh mục')
    loi_nhuan = fields.Integer(string='Lợi nhuận',compute='get_loi_nhuan')
    chi_phi = fields.Integer(string='Chi phí vật liệu', compute='get_chiphi', readonly=True)
    chi_phi_khac = fields.Integer(string='Chi phí khác')
    total_chiphi = fields.Integer(string='Tổng chi phí', compute='get_total_chiphi')
    tam_ung = fields.One2many(comodel_name='tam.ung', inverse_name='cong_trinh', string='Tạm ứng')

    @api.onchange('chi_phi_khac','vat_lieu','chi_phi')
    def get_total_chiphi(self):
        for rec in self:
            rec.total_chiphi = rec.chi_phi_khac+rec.chi_phi

    @api.onchange('vatlieu')
    def get_chiphi(self):
        for rec in self:
            total = 0
            if rec.vatlieu:

                for i in rec.vatlieu:
                    total += i.gia_ban*i.so_luong
            rec.chi_phi = total

    @api.onchange('total_chiphi','tong_thu')
    def get_loi_nhuan(self):
        for rec in self:
            rec.loi_nhuan = rec.tong_thu - rec.total_chiphi


    @api.onchange('location_id')
    def depend_location(self):
        self.stock_picking_type =  self.env['stock.picking.type'].search(['&',('code','=','outgoing'),('default_location_src_id','=',self.location_id.id)],limit=1)

    def confirm(self):
        self.state = '1'
        Stock = self.env['stock.picking']
        vals = {
            'partner_id': self.truong_nhom.address_home_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_id.id,
            'picking_type_id': self.stock_picking_type.id,
            'origin': self.ma_phieu,
            'move_ids_without_package': [(0,0,{
                                            'product_id': line.name,
                                            'product_uom_qty': line.so_luong,
                                            'name': 'new',
                                            'product_uom': line.name.uom_id,
                                            'location_id': self.location_id.id,
                                            'location_dest_id': self.location_id.id,
                                            'state': 'assigned',
                                    })for line in self.vatlieu]
        }
        Stock.create(vals)
        self.delivery_count =1

    def done(self):
        if self.state != '1':
            raise UserError('Vui lòng làm mới trình duyệt')
        self.state = '2'
        REPORT_B2C = self.env['report.b2c']
        REPORT_B2C.create({
            'ln_thi_cong': self.loi_nhuan
        })
        # trả vật liệu thừa về kho
        stock_picking_type = self.env['stock.picking.type'].search(
            [ ('code', '=', 'incoming')], limit=1)
        Stock = self.env['stock.picking']
        vals = {
            'partner_id': self.truong_nhom.address_home_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_id.id,
            'picking_type_id': stock_picking_type.id,
            'origin': self.ma_phieu,
            'move_ids_without_package': [(0, 0, {
                'product_id': line.name,
                'product_uom_qty': line.so_luong - line.so_luong_confirm,
                'name': 'new',
                'product_uom': line.name.uom_id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_id.id,
                'state': 'assigned',
            }) for line in self.vatlieu]
        }
        Stock.create(vals)
        self.delivery_count += 1
    def cancel(self):
        self.state = '3'

    # def action_view_delivery(self):
    #     return True


    def action_view_delivery(self, context=None):
        field_ids = self.env['stock.picking'].search([('origin','=',self.ma_phieu)]).ids
        domain = [('id', 'in', field_ids)]
        view_id_tree = self.env['ir.ui.view'].search([('name', '=', "stock.picking.tree")])
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(view_id_tree[0].id, 'tree'), (False, 'form')],
            'view_id ref="module_name.tree_view"': '',
            'target': 'current',
            'domain': domain,
        }

class LineVatlieu(models.Model):
    _name = 'line.vatlieu'

    name = fields.Many2one(comodel_name='product.product', string='Tên vật liệu')
    so_luong = fields.Integer(string='Số lượng tạm ứng')
    so_luong_confirm = fields.Integer(string='Số lượng sử dụng')
    gia_ban = fields.Float(string='Giá vật liệu')
    ref_vatlieu = fields.Many2one(comodel_name='thi.cong', string='Vật liệu thi công')

    @api.model
    def default_get(self, fields):
        res = super(LineVatlieu, self).default_get(fields)
        res['so_luong'] = 1
        return res
    @api.onchange('name')
    def onchange_product(self):
        for i in self:
            i.gia_ban = i.name.list_price

class LineUng(models.Model):
    _name = 'tam.ung'

    date_create = fields.Date(string='Ngày ứng', readonly=True, default=datetime.today())
    nguoi_ung = fields.Many2one(comodel_name='hr.employee', string='Người nhận tiền')
    so_tien = fields.Integer(string='Số tiền')
    state = fields.Selection([('0','Nháp'),('1','Đã xác nhận'),('2','Hủy')],string='Trạng thái', default='0')
    cong_trinh = fields.Many2one(comodel_name='thi.cong', string='Công trình')
    note = fields.Text(string='Note')

    def confirm(self):
        for rec in self:
            if rec.state != '0':
                raise UserError('Làm mới trình duyệt')
            rec.state = '1'

    def cancel(self):
        for rec in self:
            if rec.state != '0':
                raise UserError('Làm mới trình duyệt')
            rec.state = '2'

class NhanSuThiCong(models.Model):
    _name = 'nhansu.thicong'
    _rec_name = 'nhan_vien'

    nhan_vien = fields.Many2one(comodel_name='hr.employee', string='Nhân viên')
    phong_ban = fields.Many2one(comodel_name='hr.department',string='Phòng ban', related='nhan_vien.department_id')
    mobile = fields.Char(string='Mobile' , related='nhan_vien.mobile_phone')
    tien_luong = fields.Integer(string='Tiền lương/ Ngày', compute='get_luong')
    cong_trinh = fields.Many2one(comodel_name='thi.cong', string='Công trình')

    def get_luong(self):
        for rec in self:
            hop_dong = rec.env['hr.contract'].search(['&',('employee_id','=',rec.nhan_vien.id),('state','=','open')],limit=1)
            LUONG = hop_dong.wage/30
            rec.tien_luong = int(LUONG)