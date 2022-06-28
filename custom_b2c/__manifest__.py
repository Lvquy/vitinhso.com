# -*- coding: utf-8 -*-
#############################################################################
#
#   Author: Lv Quy 
#
#############################################################################

{
    'name': 'custom_b2c',
    'version': '1',
    'category': '',
    'live_test_url': 'https://youtube.com',
    'summary': 'Custom module sale',
    'author': 'Lv Quy',
    'company': '',
    'website': 'https://#',
    'depends': ['sale', 'base_setup', 'hr', 'web', 'product','contacts','mrp'],
    'data': [
        'data/sequence.xml',
        'data/default_data.xml',
        'data/mail_template.xml',
        'data/cron_job.xml',
        # security
        'security/custom_b2c_security.xml',
        'security/ir.model.access.csv',
        # security end
        'views/search.xml',
        'views/set_price.xml',
        'views/stock_picking_form_custom.xml',
        'views/res_partner.xml',
        'views/product_template.xml',
        'views/ke_hang.xml',
        'views/product_product.xml',
        # 'views/res_config_setting.xml',
        'views/chi_phi_kho.xml',
        'views/employee_stock.xml',
        'views/product_qty_on_hand.xml',
        'views/thicong_views.xml',
        'views/line_vatlieu.xml',
        'views/co_phan_views.xml',
        'views/giao_dich_cp_views.xml',
        'views/user_profile_views.xml',
        'views/res_users_views.xml',
        'views/dau_tu_views.xml',
        'views/sale_views_custom.xml',
        'views/tiet_kiem_views.xml',
        'views/tai_san_views.xml',
        'views/san_xuat.xml',
        'views/cong_viec.xml',
        'views/hr_employee.xml',
        'views/user_profile_trans_views.xml',
        'views/cskh.xml',
        'views/custom_footer.xml',
        'views/warehouse_quantity.xml',
        'views/blog.xml',
        'views/partner.xml',
        'winzard/report_b2c.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'custom_b2c/static/src/css/style.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
}
