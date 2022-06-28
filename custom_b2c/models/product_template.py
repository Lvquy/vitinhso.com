# -*- coding: utf-8 -*-



from odoo import api, fields, models


class SetPrice(models.Model):
    _name = 'set.price'

    price = fields.Integer(string='UP/Down Discount')
    type = fields.Selection([('1','Số tiền'),('2','Phần trăm')],string='Kiểu', default='2')
    cost_sale = fields.Selection([('1','Theo giá vốn'),('2','Theo giá bán hiện tại')],string='Kiểu', default='1')

    def up_price(self):
        ProductTemplate = self.env['product.product']

        selected_ids = self.env.context.get('active_ids', [])
        selected_records = ProductTemplate.browse(selected_ids)
        if self.cost_sale == '1':
            if self.type == '1':
                for i in selected_records:
                    i.list_price = i.standard_price + self.price
            if self.type == '2':
                for i in selected_records:
                    i.list_price = i.standard_price + self.price*0.01*i.standard_price
        if self.cost_sale == '2':
            if self.type == '1':
                for i in selected_records:
                    i.list_price = i.list_price + self.price
            if self.type == '2':
                for i in selected_records:
                    i.list_price = i.list_price + self.price*0.01*i.list_price


    def down_price(self):
        ProductProduct= self.env['product.product']

        selected_ids = self.env.context.get('active_ids', [])
        selected_records = ProductProduct.browse(selected_ids)
        if self.cost_sale == '1':
            if self.type == '1':
                for i in selected_records:
                    i.list_price = i.standard_price -  self.price
            if self.type == '2':
                for i in selected_records:
                    i.list_price = i.standard_price -  self.price*0.01*i.standard_price
        if self.cost_sale == '2':
            if self.type == '1':
                for i in selected_records:
                    i.list_price = i.list_price -  self.price
            if self.type == '2':
                for i in selected_records:
                    i.list_price = i.list_price -  self.price*0.01*i.list_price

class KeHang(models.Model):
    _name = 'ke.hang'

    name = fields.Char(string='Tên kệ hàng')
    description = fields.Text(string='Mô tả kệ hàng ')
    of_stock = fields.Many2one(comodel_name='stock.warehouse', string='Thuộc kho')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hide = fields.Boolean(string='Hide', default=True, compute="get_user")

    @api.depends('hide')
    def get_user(self):

        user_crnt = self._uid

        res_user = self.env['res.users'].search([('id', '=', user_crnt)])

        if res_user.has_group('custom_b2c.group_ql'):
            self.hide = False
        else:
            self.hide = True


    warehouse_quantity = fields.Char(compute='_get_warehouse_quantity', string='Quantity per warehouse')
    def _get_warehouse_quantity(self):
        for record in self:
            warehouse_quantity_text = ''
            product_id = self.env['product.product'].sudo().search([('product_tmpl_id', '=', record.id)])
            if product_id:
                quant_ids = self.env['stock.quant'].sudo().search(
                    [('product_id', '=', product_id[0].id), ('location_id.usage', '=', 'internal')])
                t_warehouses = {}
                for quant in quant_ids:
                    if quant.location_id:
                        if quant.location_id not in t_warehouses:
                            t_warehouses.update({quant.location_id: 0})
                        t_warehouses[quant.location_id] += quant.quantity

                tt_warehouses = {}
                for location in t_warehouses:
                    warehouse = False
                    location1 = location
                    while (not warehouse and location1):
                        warehouse_id = self.env['stock.warehouse'].sudo().search([('lot_stock_id', '=', location1.id)])
                        if len(warehouse_id) > 0:
                            warehouse = True
                        else:
                            warehouse = False
                        location1 = location1.location_id
                    if warehouse_id:
                        if warehouse_id.name not in tt_warehouses:
                            tt_warehouses.update({warehouse_id.name: 0})
                        tt_warehouses[warehouse_id.name] += t_warehouses[location]

                for item in tt_warehouses:
                    if tt_warehouses[item] != 0:
                        warehouse_quantity_text = warehouse_quantity_text + ' ** ' + item + ': ' + str(
                            tt_warehouses[item])
                record.warehouse_quantity = warehouse_quantity_text
