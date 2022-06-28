# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import datetime

class MRPBOM(models.Model):
    _inherit = 'mrp.bom'

    chi_phi = fields.Integer(string='Chi phí sản xuất')


    @api.onchange('bom_line_ids')
    def _compute_chi_phi(self):
        for rec in self:
            rec.chi_phi = 0
            for line in rec.bom_line_ids:
                rec.chi_phi += int(line.product_qty*line.cost)

class MRPBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    cost = fields.Float(string='Đơn giá vốn',related='product_id.standard_price')

class MRPProduct(models.Model):
    _inherit = 'mrp.production'

    chi_phi = fields.Integer(string='Chi phí sản xuất',compute='_compute_chi_phi')
    nhan_cong = fields.Many2many(comodel_name='hr.employee', string='Nhân công')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Gia công ngoài')
    tam_ung = fields.One2many(comodel_name='sx.tam.ung', inverse_name='san_xuat', string='Tạm ứng')

    @api.onchange('bom_id','product_qty')
    def _compute_chi_phi(self):
        for rec in self:
            rec.chi_phi = int(rec.product_qty*rec.bom_id.chi_phi)

class SXLineUng(models.Model):
    _name = 'sx.tam.ung'

    date_create = fields.Date(string='Ngày ứng', readonly=True, default=datetime.today())
    nguoi_ung = fields.Many2one(comodel_name='hr.employee', string='Người nhận tiền')
    so_tien = fields.Integer(string='Số tiền')
    state = fields.Selection([('0','Nháp'),('1','Đã xác nhận'),('2','Hủy')],string='Trạng thái', default='0')
    san_xuat = fields.Many2one(comodel_name='mrp.production', string='Công trình')
    note = fields.Text(string='Note')

    def confirm(self):
        for rec in self:
            rec.state ='1'
    def cancel(self):
        for rec in self:
            rec.state = '2'