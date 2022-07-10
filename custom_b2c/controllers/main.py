# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.addons.website.controllers.main import Home
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import QueryURL
from odoo.http import Response
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing


class Home(Home,Response):


    @http.route('/', type='http', auth="public", website=True, sitemap=True)
    def index(self, **kw):
        res = super(Home, self).index()
        CP = request.env['co.phan']
        UserProfile = request.env['user.profile'].search([])

        price_cp = (request.env['ir.config_parameter'].get_param('custom_b2c.price_unit_cp') or 0)
        total_cp = request.env['ir.config_parameter'].get_param('custom_b2c.total_cp') or 0
        cp_phathanh = CP.search_count([]) or 0
        total_points = 0
        toal_price_up_cp = request.env['ir.config_parameter'].get_param('custom_b2c.loi_nhuan_ban_hang') or 0
        for i in UserProfile:
            total_points += i.reward_points

        return request.render('custom_b2c.custom_field_to_home', {
           'price_cp': price_cp,'total_cp':total_cp,'cp_phathanh':cp_phathanh,
            'total_points':total_points,'toal_price_up_cp':toal_price_up_cp
       })
        # return res

class WebsiteSaleCustom(WebsiteSale):

    def _get_country_related_render_values(self, kw, render_values):
        '''
        This method provides fields related to the country to render the website sale form
        '''
        values = render_values['checkout']
        mode = render_values['mode']
        order = render_values['website_sale_order']

        def_country_id = request.env['res.country'].search([('code', '=', 'VN')], limit=1)
        # def_country_id = order.partner_id.country_id
        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.env['res.country'].search([('code', '=', 'VN')], limit=1)
        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(
            int(values['country_id']))
        country = country and country.exists() or def_country_id

        res = {
            'country': country,
            'country_states': country.get_website_sale_states(mode=mode[1]),
            'countries': country.get_website_sale_countries(mode=mode[1]),
        }
        return res

    @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    def shop_payment_validate(self, transaction_id=None, sale_order_id=None, **post):

        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        if transaction_id:
            tx = request.env['payment.transaction'].sudo().browse(transaction_id)
            assert tx in order.transaction_ids()

        elif order:
            tx = order.get_portal_last_transaction()
        else:
            tx = None

        if not order or (order.amount_total and not tx):
            return request.redirect('/shop')

        if order and not order.amount_total and not tx:
            order.with_context(send_email=True).action_confirm()
            return request.redirect(order.get_portal_url())

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == 'draft':
            return request.redirect('/shop')

        PaymentPostProcessing.remove_transactions(tx)
        order.write({'pay_method': tx.acquirer_id.id})
        return request.redirect('/shop/confirmation')
