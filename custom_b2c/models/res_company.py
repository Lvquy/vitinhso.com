# -*- coding: utf-8 -*-


from datetime import datetime

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = ['res.company']

    logo_report = fields.Binary(string='Logo Cty For Email')
