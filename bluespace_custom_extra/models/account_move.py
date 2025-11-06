# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res= super(AccountMove, self).action_post()
        if self.partner_id:
            self.message_unsubscribe(partner_ids=[self.partner_id.id])
        return res