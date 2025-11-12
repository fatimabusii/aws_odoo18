from odoo import _, fields, models, Command
from odoo.addons.web.controllers.utils import clean_action
from odoo.exceptions import UserError

class BankRecWidget(models.Model):
    _inherit = "bank.rec.widget"

    is_sales_validated = fields.Boolean(
        string='Is Sales Validated?',
        default=False,
        compute='_compute_sales_status'
    )

    def _compute_sales_status(self):
        for rec in self:
            rec.is_sales_validated = False
            if rec.matched_sale_order_ids:
                if rec.matched_sale_order_ids[0].mapped('state') == 'sale':
                    rec.is_sales_validated = True

    def button_auto_validate_sales_order(self):
        self.ensure_one()
        if self.matched_sale_order_ids:
            sale_order_id = self.matched_sale_order_ids[0]
            if sale_order_id:
                sale = sale_order_id._origin
                if sale.state in ('draft','sent'):
                    # sales confirm
                    sale.action_confirm()
                    if not sale.invoice_ids:
                        # create invoice
                        #sale._force_lines_to_invoice_policy_order()
                        invoices = sale.with_context(
                            raise_if_nothing_to_invoice=False
                        )._create_invoices()
                        # post invoice
                        for invoice in invoices:
                            invoice.action_post()

                        self.is_sales_validated = True
                        self._action_trigger_matching_rules()
                        self.next_action_todo = {'type': 'reset_form'}
                else:
                    raise UserError(_('Sales Order already validated.'))

