# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import fields, models, api
from odoo.tools.sql import column_exists, create_column
from collections import defaultdict


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    dummy_subscription_end_date = fields.Date(
        string="Dummy Subscription Revenue End Date", readonly=True
    )

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _post(self, soft=True):
        posted_moves = super()._post(soft=soft)
        for move in posted_moves:
            if not move.invoice_line_ids.subscription_id or move.move_type != 'out_invoice':
                continue
            aml_by_subscription = defaultdict(lambda: self.env['account.move.line'])
            for aml in move.invoice_line_ids:
                aml_by_subscription[aml.subscription_id] |= aml
            for subscription, aml in aml_by_subscription.items():
                sale_order = aml.sale_line_ids.order_id
                if subscription != sale_order:
                    # we are invoicing an upsell
                    continue
                # Normally, only one period_end should exist
                end_dates = [ed for ed in aml.mapped('dummy_subscription_end_date') if ed]
                if end_dates and max(end_dates) :
                    subscription.next_invoice_date = max(end_dates)
                    # subscription._update_next_invoice_date()
        return posted_moves
