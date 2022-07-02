# -*- coding: utf-8 -*-
from odoo import models, fields

class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    is_wallet_vts = fields.Boolean(default=False, string='Là vi tính số')