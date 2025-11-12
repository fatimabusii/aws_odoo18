from odoo import _, fields, models, Command, api
import logging
_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = 'res.partner'

    create_invoice_flag = fields.Boolean(compute='_compute_create_invoice_flag', string="Multi-Order Customer", store=True)

    @api.depends('sale_order_ids', 'sale_order_count', 'sale_order_ids.subscription_state', 'sale_order_ids.state')
    def _compute_create_invoice_flag(self):
        for partner in self:
            all_orders = self.env['sale.order'].search_count([('partner_id', '=', partner.id), ('state', 'in', ['sale', 'done']), ('subscription_state', '!=', '6_churn')])
            if all_orders > 1:
                partner.create_invoice_flag = True
            else:
                partner.create_invoice_flag = False