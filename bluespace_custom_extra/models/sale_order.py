# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res= super(SaleOrder, self).action_confirm()
        if self.partner_id:
            self.message_unsubscribe(partner_ids=[self.partner_id.id])
        return res