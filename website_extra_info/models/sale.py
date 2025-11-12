# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    unit_used_for_text = fields.Char(string="Unit used for text")
    other_info_unit = fields.Char(string="Other unit info")
    other_info_description = fields.Text(string="Other unit description")

    what_content_text = fields.Char(string="What content text")
    other_info_what = fields.Char(string="Other content info")
    other_description = fields.Text(string="Other content description")

    what_activity_occur = fields.Char(string="What activity Occur")
    other_info_activity = fields.Char(string="Other activity info")
    activity_description = fields.Text(string="Other activity description")

    all_lease_agreement = fields.Boolean(string="I hereby confirm my acceptance of the lease agreement, and I authorise a credit check")

