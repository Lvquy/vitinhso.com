# -*- coding: utf-8 -*-


from odoo import api, fields, models
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression

class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    discount = fields.Float(string='Số % thưởng cho khách hàng')
    price_unit_cp = fields.Integer(string='Giá (vnđ) / 1 cổ phần')
    total_cp = fields.Integer(string='Tổng cung cổ phần')
    price_unit_r2cp = fields.Integer(string='Tỉ lệ đổi điểm / 1 cổ phần')
    lai_tk_1 = fields.Integer(string='Lãi gửi tiết kiệm 1 tháng (nhập %)')
    lai_tk_3 = fields.Integer(string='Lãi gửi tiết kiệm 3 tháng (nhập %)')
    lai_tk_6 = fields.Integer(string='Lãi gửi tiết kiệm 6 tháng (nhập %)')
    lai_tk_12 = fields.Integer(string='Lãi gửi tiết kiệm 12 tháng (nhập %)')
    lai_tk_18 = fields.Integer(string='Lãi gửi tiết kiệm 18 tháng (nhập %)')
    lai_tk_24 = fields.Integer(string='Lãi gửi tiết kiệm 24 tháng (nhập %)')
    lai_tk_36 = fields.Integer(string='Lãi gửi tiết kiệm 36 tháng (nhập %)')
    doi_cp = fields.Boolean(string='Cho phép đổi điểm lấy cổ phần', default=False)
    phi_giao_dich = fields.Integer(string='Phí giao dịch (%)')

    @api.model
    def set_values(self):

        ICP =  self.env['ir.config_parameter'].sudo()
        ICP.set_param('custom_b2c.discount',self.discount)
        ICP.set_param('custom_b2c.price_unit_cp',self.price_unit_cp)
        ICP.set_param('custom_b2c.price_unit_r2cp',self.price_unit_r2cp)
        ICP.set_param('custom_b2c.lai_tk_36',self.lai_tk_36)
        ICP.set_param('custom_b2c.lai_tk_24',self.lai_tk_24)
        ICP.set_param('custom_b2c.lai_tk_18',self.lai_tk_18)
        ICP.set_param('custom_b2c.lai_tk_12',self.lai_tk_12)
        ICP.set_param('custom_b2c.lai_tk_6',self.lai_tk_6)
        ICP.set_param('custom_b2c.lai_tk_3',self.lai_tk_3)
        ICP.set_param('custom_b2c.lai_tk_1',self.lai_tk_1)
        ICP.set_param('custom_b2c.doi_cp',self.doi_cp)
        ICP.set_param('custom_b2c.phi_giao_dich',self.phi_giao_dich)
        ICP.set_param('custom_b2c.total_cp',self.total_cp)
        super(ResConfigSetting,self).set_values()

    @api.model
    def get_values(self):
        ICP = self.env['ir.config_parameter'].sudo()
        res = super(ResConfigSetting,self).get_values()
        res['discount'] = ICP.get_param('custom_b2c.discount', default=0)
        res['price_unit_cp'] = int(ICP.get_param('custom_b2c.price_unit_cp', default=0))
        res['price_unit_r2cp'] = int(ICP.get_param('custom_b2c.price_unit_r2cp', default=0))
        res['lai_tk_1'] = int(ICP.get_param('custom_b2c.lai_tk_1', default=0))
        res['lai_tk_3'] = int(ICP.get_param('custom_b2c.lai_tk_3', default=0))
        res['lai_tk_6'] = int(ICP.get_param('custom_b2c.lai_tk_6', default=0))
        res['lai_tk_12'] = int(ICP.get_param('custom_b2c.lai_tk_12', default=0))
        res['lai_tk_18'] = int(ICP.get_param('custom_b2c.lai_tk_18', default=0))
        res['lai_tk_24'] = int(ICP.get_param('custom_b2c.lai_tk_24', default=0))
        res['lai_tk_36'] = int(ICP.get_param('custom_b2c.lai_tk_36', default=0))
        res['doi_cp'] = ICP.get_param('custom_b2c.doi_cp', default=0)
        res['phi_giao_dich'] = ICP.get_param('custom_b2c.phi_giao_dich', default=0)
        res['total_cp'] = ICP.get_param('custom_b2c.total_cp', default=0)
        return res
