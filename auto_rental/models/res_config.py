# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    date_of_invoice = fields.Integer(related="company_id.date_of_invoice",
        string='Date Of Invoice', readonly=False
    )
    order_message = fields.Text(string="Order Message for Office/Boardroom")

    user_email = fields.Char(string="To Email")
    salesperson_email = fields.Char(string="Salesperson Email")
    unit_days = fields.Integer(related="company_id.unit_days", string='Days of Available Unit', readonly=False)

    def set_values(self):
        res = super(ResConfigSettings,self).set_values()
        set_value = self.env['ir.config_parameter'].sudo()
        set_value.set_param('auto_rental.user_email',self.user_email)
        set_value.set_param('auto_rental.salesperson_email',self.salesperson_email)
        set_value.set_param('auto_rental.order_message',self.order_message)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings,self).get_values()
        set_value = self.env['ir.config_parameter'].sudo()
        user_email = set_value.get_param('auto_rental.user_email')
        order_message = set_value.get_param('auto_rental.order_message')
        salesperson_email = set_value.get_param('auto_rental.salesperson_email')
        res.update(user_email = user_email, order_message=order_message, salesperson_email=salesperson_email)
        return res
