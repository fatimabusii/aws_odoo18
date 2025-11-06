from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    no_of_visitors = fields.Integer("No of Visitors")
    ofc_visitors = fields.One2many('office.visitors', 'sale_id', string="visitors")

class OfficeVisitors(models.Model):
    _name = 'office.visitors'
    _description = "Visitors"

    name = fields.Char(string="Name")
    cell_phone = fields.Char(string="Cell Phone Number")
    sale_id = fields.Many2one('sale.order', string="Sales Order")   