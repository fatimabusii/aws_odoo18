# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = "res.company"

    sale_note = fields.Text(string="Sales Note", default="Are you struggling booking a unit, Please call our sales consultants (021 222 4444) ")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_note = fields.Boolean(string="Booking Note")
    sale_note = fields.Text(string='Sales Note', related="company_id.sale_note")

    @api.onchange('sale_note')
    def onchange_sale_note(self):
        for record in self:
            if self.sale_note:
                self.env.company.sale_note = record.sale_note
