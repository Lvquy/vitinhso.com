# -*- coding: utf-8 -*-



from odoo import api, fields, models
from datetime import datetime


class Stock(models.Model):
    _inherit = 'stock.picking'
    _description = "Stock Custom"

    shipcode = fields.Char('Shipping Code', help='Shipping Code.')
    shiper = fields.Many2one(comodel_name='hr.employee', string='Shiper')
    shiping_fee = fields.Integer(string='Phí vận chuyển')

class StockWareHouse(models.Model):
    _name= 'chi.phikho'

    thue_matbang = fields.Integer(string='Mặt bằng /Tháng')
    tien_dien = fields.Integer(string='Tiền điện /Tháng')
    tien_nuoc = fields.Integer(string='Tiền nước /Tháng')
    tien_internet = fields.Integer(string='Tiền internet /Tháng')
    chi_phi_khac = fields.Integer(string='Chi phí khác')
    ngay_chot = fields.Date(string='Ngày lập hóa đơn', default=datetime.today())
    total = fields.Integer(string='Tổng tiền', compute='_compute_total')
    note = fields.Text(string='Note')
    stock = fields.Many2one(comodel_name='stock.warehouse',string='Tên Kho')
    employee = fields.Many2many(comodel_name='hr.employee', string='Nhân viên', compute='onchange_stock')
    state = fields.Selection([('0','Nháp'),('1','Đã xác nhận')],default='0', string='Trạng thái')

    @api.onchange('thue_matbang','tien_dien','tien_nuoc','tien_internet','chi_phi_khac')
    def _compute_total(self):
        for rec in self:
            rec.total = 0
            rec.total += rec.thue_matbang + rec.tien_dien + rec.tien_nuoc + rec.tien_internet + rec.chi_phi_khac

    @api.depends('stock')
    def onchange_stock(self):
        self.employee = self.stock.employee
    def confirm(self):
        for rec in self:
            rec.state ='1'

class Employee2Stock(models.Model):
    _inherit = 'stock.warehouse'

    employee = fields.Many2many(comodel_name='hr.employee', string='Nhân viên kho')
