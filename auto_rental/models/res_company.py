# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class ResCompany(models.Model):
    _inherit = "res.company"

    date_of_invoice = fields.Integer(default=20, required=True)
    unit_days = fields.Integer(default=7, required=True)
