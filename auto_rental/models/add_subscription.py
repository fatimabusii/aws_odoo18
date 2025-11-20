from dateutil.relativedelta import relativedelta

from odoo import _, fields, models, Command, api
from odoo.addons.web.controllers.utils import clean_action
from odoo.exceptions import UserError, ValidationError
from odoo.tools.date_utils import get_timedelta
from odoo.tools import format_date
from odoo.osv import expression
from odoo.tools.float_utils import float_is_zero
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_recurring_rental = fields.Boolean(
        string='Is Recurring Rental?',
    )
    existing_order = fields.Boolean('Existing Order') #Added on 13-11-24

    # def get_test_custom_date(self):
    #     notification_test_date = self.env['test.date'].search([], limit=1)
    #     if notification_test_date:
    #         return notification_test_date.test_date
    #     return fields.Date.today()

    def _recurring_invoice_domain(self, extra_domain=None):
        if not extra_domain:
            extra_domain = []
        current_date = fields.Date.today()
        # test_date = self.get_test_custom_date()

        # if test_date.day == 20:
        #     current_date = test_date

        temp = current_date + get_timedelta(1, 'month')
        search_domain = [('is_batch', '=', False),
                         ('is_invoice_cron', '=', False),
                         ('is_subscription', '=', True),
                         ('subscription_state', '!=', '7_upsell'),
                         ('state', 'in', ['sale', 'done']), # allow to close done subscription at the beginning of the invoicing cron
                         ('payment_exception', '=', False),
                         ('partner_id.create_invoice_flag', '=', False),
                         '|', '&', '&', ('next_invoice_date', '<=', current_date), ('is_specific_move', '=', True), ('end_date', '>=', temp), ('end_date', '=', False)]

                         # ('stage_category', '=', 'progress')]

        search_domain2 = [('is_batch', '=', False),
                         ('is_invoice_cron', '=', False),
                         ('is_subscription', '=', True),
                         ('subscription_state', '!=', '7_upsell'),
                         ('state', 'in', ['sale', 'done']), # allow to close done subscription at the beginning of the invoicing cron
                         ('payment_exception', '=', False),
                         ('partner_id.create_invoice_flag', '=', False),
                         ('next_invoice_date', '<=', current_date), ('is_flexible', '=', True), ('notice_given', '=', False)]

        search_domain = expression.OR([search_domain, search_domain2])
        if extra_domain:
            search_domain = expression.AND([search_domain, extra_domain])
        return search_domain


    def _get_invoiceable_lines(self, final=False):
        date_from = fields.Date.today()

        # test_date = self.get_test_custom_date()
        # if test_date.day == 20:
        #     date_from = test_date

        res = super()._get_invoiceable_lines(final=final)
        res = res.filtered(lambda l: l.is_rental or l.order_id.subscription_state == '7_upsell')
        automatic_invoice = self.env.context.get('recurring_automatic')

        invoiceable_line_ids = []
        downpayment_line_ids = []
        pending_section = None

        #Added on 13-11-24 for existing order import
        existing_orders = self.filtered(lambda x: x.existing_order)
        new_orders = self.filtered(lambda x: not x.existing_order)

        #For new orders
        for line in new_orders.order_line: #self.order_line
            if line.display_type == 'line_section':
                # Only add section if one of its lines is invoiceable
                pending_section = line
                continue

            time_condition = line.order_id.next_invoice_date and line.order_id.next_invoice_date <= date_from and line.order_id.start_date and line.order_id.start_date <= date_from
            line_condition = time_condition or not automatic_invoice # automatic mode force the invoice when line are not null
            line_to_invoice = False

            service_product_id = self.env['product.product'].search([
                                ('default_code', '=', 'RENTAL_SERVICE_CHARGE')
                            ], limit=1)

            if line in res:
                # Line was already marked as to be invoiced
                line_to_invoice = True
            elif line.order_id.subscription_state == '7_upsell':
                # Super() already select everything that is needed for upsells
                line_to_invoice = False
            elif line.display_type or line.is_rental:
                # Avoid invoicing section/notes or lines starting in the future or not starting at all
                line_to_invoice = False
            elif line_condition and line.product_id.invoice_policy == 'order' and line.order_id.state == 'sale':
                # Invoice due lines
                line_to_invoice = True
            elif line_condition and line.product_id.invoice_policy == 'delivery' and (not float_is_zero(line.qty_delivered, precision_rounding=line.product_id.uom_id.rounding)):
                line_to_invoice = True

            if line_condition and line.product_id.id == service_product_id.id:
                line_to_invoice = True

            product = self.env['product.product'].search([('name','=', 'Recurring'),('recurring_invoice','=', True)], limit=1)
            if line_condition and line.product_id.id == product.id and not line.order_id.team_id.is_website and line.order_id.invoice_count == 0:
                line_to_invoice = False

            #Added for the extra line add for recurring
            deposite_product_id = self.env['product.product'].search([
                                ('default_code', '=', 'RENTAL_DEPOSIT')
                            ], limit=1)
            if line_condition and line.product_id.product_category not in ['1_storage_unit', '2_office', '3_boardroom', '4_parking'] and \
                line.product_id.id != service_product_id.id and line.product_id.id != product.id and \
                line.product_id.id != deposite_product_id.id:
                line_to_invoice = True

            if line_to_invoice:
                if line.is_downpayment:
                    # downpayment line must be kept at the end in its dedicated section
                    downpayment_line_ids.append(line.id)
                    continue
                if pending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = False
                invoiceable_line_ids.append(line.id)

        #Added on 13-11-24 creating only recurring invoice for existing orders
        for line in existing_orders.order_line:
            if line.display_type == 'line_section':
                # Only add section if one of its lines is invoiceable
                pending_section = line
                continue

            time_condition = line.order_id.next_invoice_date and line.order_id.next_invoice_date <= date_from and line.order_id.start_date and line.order_id.start_date <= date_from
            line_condition = time_condition or not automatic_invoice # automatic mode force the invoice when line are not null
            line_to_invoice = False

            service_product_id = self.env['product.product'].search([
                                ('default_code', '=', 'RENTAL_SERVICE_CHARGE')
                            ], limit=1)
            if line_condition and line.product_id.id == service_product_id.id:
                line_to_invoice = True

            product = self.env['product.product'].search([('name','=', 'Recurring'),('recurring_invoice','=', True)], limit=1)
            if line_condition and line.product_id.id == product.id and not line.order_id.team_id.is_website:
                line_to_invoice = True

            #Added for the extra line add for recurring
            deposite_product_id = self.env['product.product'].search([
                                ('default_code', '=', 'RENTAL_DEPOSIT')
                            ], limit=1)
            if line_condition and line.product_id.product_category not in ['1_storage_unit', '2_office', '3_boardroom', '4_parking'] and \
                line.product_id.id != service_product_id.id and line.product_id.id != product.id and \
                line.product_id.id != deposite_product_id.id:
                line_to_invoice = True

            if line_to_invoice:
                if line.is_downpayment:
                    # downpayment line must be kept at the end in its dedicated section
                    downpayment_line_ids.append(line.id)
                    continue
                if pending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = False
                invoiceable_line_ids.append(line.id)

        return self.env["sale.order.line"].browse(invoiceable_line_ids + downpayment_line_ids)

    # use end_date standard field in case there is fixed time period
    # def _create_recurring_invoice(self, automatic=False, batch_size=1000):
    #     search_domain = self._recurring_invoice_domain()
    #     all_subscriptions = self.search(search_domain, limit=batch_size + 1)
    #     _logger.info("all_subscriptions===================== %s",all_subscriptions)

    #     if self and len(self) == 1 and self.id not in all_subscriptions.ids and self.env.context.get('manually_invoice_create', False):
    #         all_subscriptions += self

    #     for subscription in all_subscriptions:
    #         lines = subscription.order_line.filtered(lambda x: x.is_rental and x.qty_delivered == 0)
    #         line1 = subscription.order_line.filtered(lambda x: x.product_id.id == subscription.recurring_invoice_line_ids.product_id)
    #         lines += line1

    #         for line in lines:
    #             if line.qty_delivered == 0:
    #                 line.qty_delivered = 1
    #             if line.price_unit == 0:
    #                 line.price_unit = line.price_to_set_subscrition
    #             if line.product_id.id == subscription.recurring_invoice_line_ids.product_id:
    #                 if subscription.team_id.is_website:
    #                     line.price_unit = line.price_to_set_subscrition
    #                 else:
    #                     if subscription.invoice_count > 0:
    #                         line.price_unit = line.price_to_set_subscrition
    #     invoices = super()._create_recurring_invoice(automatic, batch_size)
    #     invoices.transaction_ids = [(6, 0, [])]
    #     _logger.info("invoices>>>>>>>>>>>>>>>>>>>>>>>>> %s",invoices)
    #     sales_order = invoices.mapped('invoice_line_ids').mapped('sale_line_ids').filtered(lambda x: x.is_recurring_rental and x.qty_delivered == 1).mapped('order_id')
    #     if sales_order:
    #         for sale in sales_order:
    #             lines = sale.order_line.filtered(lambda x: x.is_rental)
    #             # lines[0].return_date = sale.next_invoice_date
                
    #             lang_code = sale.partner_id.lang
    #             new_date = self._next_recur_date(lines[0].return_date)
    #             default_next_invoice_date = new_date + get_timedelta(sale.duration_days,
    #                                                                          sale.plan_id.billing_period_unit or 'day')
    #             next_invoice_date = default_next_invoice_date - relativedelta(days=1)
    #             lines[0].return_date = next_invoice_date
    #             sale._compute_rental_status()
    #     return invoices
    def _create_recurring_invoice(self, automatic=False, batch_size=1000):
        search_domain = self._recurring_invoice_domain()
        all_subscriptions = self.search(search_domain, limit=batch_size + 1)
        _logger.info("all_subscriptions===================== %s", all_subscriptions)

        if self and len(self) == 1 and self.id not in all_subscriptions.ids and self.env.context.get('manually_invoice_create', False):
            all_subscriptions |= self

        for subscription in all_subscriptions:
            # Rental lines
            rental_lines = subscription.order_line.filtered(lambda l: l.is_rental and l.qty_delivered == 0)

            # Subscription lines (if recurring_invoice_line_ids exists)
            if hasattr(subscription, 'recurring_invoice_line_ids') and subscription.recurring_invoice_line_ids:
                subscription_lines = subscription.order_line.filtered(
                    lambda l: l.product_id in subscription.recurring_invoice_line_ids.mapped('product_id')
                )
            else:
                subscription_lines = self.env['sale.order.line']

            lines = rental_lines | subscription_lines

            for line in lines:
                if line.qty_delivered == 0:
                    line.qty_delivered = 1
                if line.price_unit == 0:
                    line.price_unit = line.price_to_set_subscrition
                if hasattr(subscription, 'recurring_invoice_line_ids') and subscription.recurring_invoice_line_ids:
                    if line.product_id in subscription.recurring_invoice_line_ids.mapped('product_id'):
                        if subscription.team_id.is_website:
                            line.price_unit = line.price_to_set_subscrition
                        else:
                            if subscription.invoice_count > 0:
                                if line.price_unit != line.total_service_charge:
                                    line.price_unit = line.total_service_charge
                                else:                             
                                    line.price_unit = line.price_to_set_subscrition
                                
                            

        invoices = super()._create_recurring_invoice(automatic, batch_size)
        invoices.transaction_ids = [(6, 0, [])]
        _logger.info("invoices>>>>>>>>>>>>>>>>>>>>>>>>> %s", invoices)

        sales_order = invoices.mapped('invoice_line_ids').mapped('sale_line_ids').filtered(
            lambda l: l.is_recurring_rental and l.qty_delivered == 1
        ).mapped('order_id')

        for sale in sales_order:
            rental_lines = sale.order_line.filtered(lambda l: l.is_rental)
            if not rental_lines:
                continue
            lang_code = sale.partner_id.lang
            new_date = self._next_recur_date(rental_lines[0].return_date)
            default_next_invoice_date = new_date + get_timedelta(
                sale.duration_days, sale.plan_id.billing_period_unit or 'day'
            )
            next_invoice_date = default_next_invoice_date - relativedelta(days=1)
            rental_lines[0].return_date = next_invoice_date
            sale._compute_rental_status()

        return invoices


    # def _create_invoices(self, grouped=False, final=False, date=None):
    #     invoices = super()._create_invoices(grouped=grouped, final=final, date=date)
    #     for order in self:
    #         line1 = order.order_line.filtered(lambda x: x.product_id.id == order.recurring_invoice_line_ids.product_id)
    #         if line1 and not order.is_website and order.invoice_count > 0:
    #             line1.price_unit = line1.price_to_set_subscrition
    #         inv_date = order._next_recur_date(order.next_invoice_date)
    #         if inv_date:
    #             invoices.invoice_date = inv_date
    #     return invoices
    def _create_invoices(self, grouped=False, final=False, date=None):
        invoices = super()._create_invoices(grouped=grouped, final=final, date=date)
        
        for order in self:
            # Only process rental/subscription orders
            if hasattr(order, 'recurring_invoice_line_ids') and order.recurring_invoice_line_ids:
                line1 = order.order_line.filtered(
                    lambda x: x.product_id in order.recurring_invoice_line_ids.mapped('product_id')
                )
                if line1 and not order.is_website and order.invoice_count > 0:
                    for l in line1:
                        if l.price_unit != l.total_service_charge:
                            l.price_unit = l.total_service_charge
                        else:
                            l.price_unit = l.price_to_set_subscrition

            # Compute next invoice date if available
            if hasattr(order, '_next_recur_date'):
                inv_date = order._next_recur_date(getattr(order, 'next_invoice_date', None))
                if inv_date:
                    invoices.invoice_date = inv_date

        return invoices

    def _create_invoices(self, grouped=False, final=False, date=None):
        # _logger.info("="*80)
        # _logger.info("_CREATE_INVOICES START")
        # _logger.info("grouped=%s, final=%s, date=%s", grouped, final, date)
        # _logger.info("Context: %s", self.env.context)
        # _logger.info("Orders to invoice: %s", self.ids)
        
        invoices = super()._create_invoices(grouped=grouped, final=final, date=date)
        # _logger.info("Invoices created by super(): %s", invoices.ids if invoices else None)
        
        for order in self:
            # _logger.info("-" * 60)
            # _logger.info("Processing order ID=%s, Name=%s", order.id, order.name)
            # _logger.info("Order.is_website=%s, Order.invoice_count=%s", order.is_website, order.invoice_count)
            
            service_product = order.get_service_product()
            # _logger.info("Service product ID=%s, Name=%s", 
                        # service_product.id if service_product else None,
                        # service_product.name if service_product else None)
            
            line1 = order.order_line.filtered(lambda x: x.product_id.id == order.get_service_product().id)
            
            if line1:
                # _logger.info(">>> SERVICE LINE FOUND: Line ID=%s", line1.id)
                # _logger.info("BEFORE CHANGE:")
                # _logger.info("  line1.price_unit = %.2f", line1.price_unit)
                # _logger.info("  line1.price_to_set_subscrition = %.2f", line1.price_to_set_subscrition)
                # _logger.info("  line1.total_service_charge = %.2f", line1.total_service_charge)
                
                if line1 and not order.is_website and order.invoice_count > 0:
                    # _logger.info(">>> CONDITION MET: Will update price_unit")
                    # _logger.info("    Condition breakdown:")
                    # _logger.info("      line1 exists: %s", bool(line1))
                    # _logger.info("      not order.is_website: %s", not order.is_website)
                    # _logger.info("      order.invoice_count > 0: %s (%s)", order.invoice_count > 0, order.invoice_count)
                    
                    # _logger.info(">>> UPDATING: line1.price_unit = line1.price_to_set_subscrition (%.2f)", 
                    #             line1.price_to_set_subscrition)
                    # line1.price_unit = line1.price_to_set_subscrition

                    if line1.price_unit != line1.total_service_charge:
                        # _logger.info(">>> MISMATCH DETECTED:")
                        # _logger.info("    price_unit (%.2f) != total_service_charge (%.2f)", 
                        #             line1.price_unit, line1.total_service_charge)
                        # _logger.info(">>> UPDATING: line1.price_unit = line1.total_service_charge (%.2f)", 
                        #             line1.total_service_charge)
                        line1.price_unit = line1.total_service_charge
                    # else:
                    #     _logger.info(">>> NO UPDATE NEEDED: price_unit already matches total_service_charge (%.2f)", 
                    #             line1.total_service_charge)
                    
                    # _logger.info("AFTER CHANGE:")
                    # _logger.info("  line1.price_unit = %.2f", line1.price_unit)
                    # _logger.info("  line1.price_to_set_subscrition = %.2f", line1.price_to_set_subscrition)
                    # _logger.info("  line1.total_service_charge = %.2f", line1.total_service_charge)
                # else:
                #     _logger.info(">>> CONDITION NOT MET: Will NOT update price_unit")
                #     _logger.info("    Condition breakdown:")
                #     _logger.info("      line1 exists: %s", bool(line1))
                #     _logger.info("      not order.is_website: %s", not order.is_website)
                #     _logger.info("      order.invoice_count > 0: %s (%s)", order.invoice_count > 0, order.invoice_count)
            # else:
            #     _logger.info(">>> NO SERVICE LINE FOUND for this order")
            
            inv_date = order._next_recur_date(order.next_invoice_date)
            # _logger.info("Next recur date calculation:")
            # _logger.info("  order.next_invoice_date = %s", order.next_invoice_date)
            # _logger.info("  Calculated inv_date = %s", inv_date)
            
            if inv_date:
                # _logger.info(">>> Setting invoices.invoice_date to %s", inv_date)
                invoices.invoice_date = inv_date
            # else:
            #     _logger.info(">>> NOT setting invoice_date (inv_date is None/False)")
        
        # _logger.info("Returning invoices: %s", invoices.ids if invoices else None)
        # _logger.info("_CREATE_INVOICES END")
        # _logger.info("="*80)
        return invoices


    def _update_next_invoice_date(self):
        for order in self:
            if not order.is_subscription:
                continue

            # ignore change date if first invoice
            if len(order.invoice_ids.ids) <=1:
                continue
            last_invoice_date = order.next_invoice_date or order.start_date
            if last_invoice_date:
                order.next_invoice_date = last_invoice_date + get_timedelta(order.duration_days, order.plan_id.billing_period_unit or 'day')

    def action_confirm(self):
        is_office_boardroom_product = self.order_line.mapped('product_id').filtered(lambda x: x.is_office or x.is_boardroom)
        if self.is_recurring_rental: # and not is_office_boardroom_product:
            product = self.env['product.product'].search([('name','=', 'Recurring'),('recurring_invoice','=', True)], limit=1)
            if product:
                order_lines = self.order_line.filtered(lambda x: x.is_rental)
                monthly_recurrency = self.env['sale.temporal.recurrence'].search([('unit','=','month')], limit=1)
                rental_monthly_pricing = 0
                if order_lines[0].product_id.product_pricing_ids:
                    if order_lines[0].product_id.product_pricing_ids.filtered(lambda x: x.sudo().plan_id.id == monthly_recurrency.id):
                        rental_monthly_pricing = order_lines[0].product_id.product_pricing_ids.filtered(lambda x: x.sudo().plan_id.id == monthly_recurrency.id).price

                so_line=self.env['sale.order.line'].create({'name': product.name,
                                                'order_id': self.id,
                                                'product_id': product.id,
                                                'product_uom_qty': 1,
                                                'product_uom': product.uom_id.id,
                                                # 'price_unit': rental_monthly_pricing
                                                'price_to_set_subscrition': rental_monthly_pricing,
                                                'sequence': 3,
                                                })

                so_line.price_unit = 0#rental_monthly_pricing
                if monthly_recurrency:
                    self.plan_id = monthly_recurrency.id

                so_line.price_unit = 0#rental_monthly_pricing

                if order_lines[0].product_id.product_category in ['1_storage_unit', '2_office', '3_boardroom', '4_parking']:
                    service_line = self.order_line.filtered(lambda x: x.product_id.id == self.recurring_invoice_line_ids.product_id)
                    service_line.price_to_set_subscrition = order_lines[0].product_id.service_charge

                if order_lines[0].product_id.product_category == '1_storage_unit':
                    fpos = self.fiscal_position_id or self.fiscal_position_id._get_fiscal_position(self.partner_id)
                    product_taxes = order_lines[0].product_id.sudo().taxes_id.filtered(lambda tax: tax.company_id == self.company_id)
                    taxes = fpos.map_tax(product_taxes)
                    so_line.tax_id = [x.id for x in taxes]

        res= super(SaleOrder, self.with_context(mail_auto_subscribe_no_notify=False, mail_notify_force_send=False,force_send=False)).action_confirm()

        order_lines = self.order_line.filtered(lambda x: x.is_rental)
        if order_lines:

            day_of_invoice = self.company_id.date_of_invoice
            start_date =order_lines[0].start_date

            if int(start_date.strftime("%d")) >= day_of_invoice:
                new_date = start_date + get_timedelta(1, 'month')
                temp = new_date.replace(day=day_of_invoice)
                self.next_invoice_date = temp
            if int(start_date.strftime("%d")) < day_of_invoice:
                temp = start_date.replace(day=day_of_invoice)
                self.next_invoice_date = temp
        return res

    def _next_recur_date(self, start_date):
        # If no start_date is provided, use the earliest rental product start date
        if not start_date:
            rental_lines = self.order_line.filtered(lambda l: l.is_rental and l.start_date)
            if rental_lines:
                start_date = min(rental_lines.mapped('start_date'))
                _logger.info("No start_date provided, using earliest rental product start date: %s", start_date)
            else:
                _logger.warning("No start_date and no rental product start date available — cannot compute next recurrence.")
                return

        new_date = start_date + get_timedelta(1, 'month')
        temp = new_date.replace(day=1)
        return temp

    def _next_recur_date_same(self, start_date):
        # If no start_date is provided, use the earliest rental product start date
        if not start_date:
            rental_lines = self.order_line.filtered(lambda l: l.is_rental and l.start_date)
            if rental_lines:
                start_date = min(rental_lines.mapped('start_date'))
                _logger.info("No start_date provided, using earliest rental product start date: %s", start_date)
            else:
                _logger.warning("No start_date and no rental product start date available — cannot compute next recurrence.")
                return
        day_of_invoice = self.company_id.date_of_invoice
        if int(start_date.strftime("%d")) < int(day_of_invoice):
            return start_date.replace(day=day_of_invoice)
        return start_date + get_timedelta(1, 'month')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_to_set_subscrition = fields.Float(
        string='Hold value of subscription',
    )

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        res = super()._prepare_invoice_line(**optional_values)
        if self.display_type:
            return res
        elif self.is_rental or self.order_id.subscription_state == '7_upsell':
            _logger.info("Processing order line: %s (Product: %s)", self.id, self.product_id.name)
            _logger.info("Subscription state: %s", self.order_id.subscription_state)
    
            # product_desc = self.product_id.get_product_multiline_description_sale() + self._get_sale_order_line_multiline_description_variants()
            # product_desc = f"{self.order_id.order_line.product_id.get_product_multiline_description_sale() or ''}{self._get_sale_order_line_multiline_description_variants()}"
            order_products = self.order_id.order_line.mapped('product_id')
            _logger.info("All products in order_line: %s", [(p.id, p.name) for p in order_products])

            try:
                rental_lines = self.order_id.order_line.filtered(lambda l: l.is_rental)

                for rental_line in rental_lines:
                    product = rental_line.product_id
                    product_desc = f"{product.get_product_multiline_description_sale() or ''}{rental_line._get_sale_order_line_multiline_description_variants()}"
                    _logger.info("Processing rental line: %s (Product: %s)", rental_line.id, product.name)

                # product_desc = f"{self.order_id.order_line.product_id.get_product_multiline_description_sale() or ''}{self._get_sale_order_line_multiline_description_variants()}"
            except ValueError as e:
                _logger.error("Expected singleton error on order_line.product_id: %s", order_products)
                raise e
    
            account_id = False
            # Added on 14-11-24
            all_order_lines = self.order_id.mapped('order_line')
            _logger.info("All order lines and their products/categories:")
            for line in all_order_lines:
                category = getattr(line.product_id, 'categ_id', False)
                _logger.info(
                    "Order line ID: %s, Product: %s, Category: %s, Type: %s",
                    line.id,
                    line.product_id.name,
                    category.name if hasattr(category, 'name') else category,
                    line.product_id.type
                )
            product_category_list = ['1_storage_unit', '2_office', '3_boardroom', '4_parking', 'Rental']
            order_line_id = self.order_id.mapped('order_line').filtered(lambda x: x.product_id.categ_id.name in product_category_list and x.product_id.type == 'consu')
            _logger.info("Filtered order_line_id for product categories: %s", [(l.id, l.product_id.name) for l in order_line_id])

            if order_line_id:
                try:
                    if self.product_id.id != order_line_id.product_id.id:
                        rental_lines = self.order_id.order_line.filtered(lambda l: l.is_rental)

                        for rental_line in rental_lines:
                            product = rental_line.product_id
                            product_desc = f"{product.get_product_multiline_description_sale() or ''}{rental_line._get_sale_order_line_multiline_description_variants()}"
                            _logger.info("Processing rental line: %s (Product: %s)", rental_line.id, product.name)

                        # product_desc = f"{order_line_id.product_id.get_product_multiline_description_sale() or ''}{self._get_sale_order_line_multiline_description_variants()}"
                        account_id = order_line_id.product_id.property_account_income_id
                except ValueError as e:
                    _logger.error("Expected singleton error on order_line_id.product_id: %s", order_line_id.mapped('product_id'))
                    raise e
            # if self.product_id.id != order_line_id.product_id.id:
            #     # product_desc = order_line_id.product_id.get_product_multiline_description_sale() + self._get_sale_order_line_multiline_description_variants()
            #     product_desc = f"{order_line_id.product_id.get_product_multiline_description_sale() or ''}{self._get_sale_order_line_multiline_description_variants()}"

            #     account_id = order_line_id.product_id.property_account_income_id
            _logger.info("Duration days: %s", self.order_id.duration_days)
            _logger.info("Billing period unit: %s", self.order_id.plan_id.billing_period_unit or 'day')
            _logger.info("Plan ID: %s, Plan Name: %s", self.order_id.plan_id.id, self.order_id.plan_id.name)

            description = _("%(product)s - %(duration)d %(unit)s",
                            product=product_desc,
                            duration=round(self.order_id.duration_days),
                            unit=self.order_id.plan_id.billing_period_unit or 'day')
            lang_code = self.order_id.partner_id.lang
            flag = False
            if self.order_id.subscription_state == '7_upsell':
                # We start at the beginning of the upsell as it's a part of recurrence
                new_period_start = self.order_id.start_date or fields.Datetime.today()
                new_period_start2 = new_period_start
            else:
                # We need to invoice the next period: last_invoice_date will be today once this invoice is created. We use get_timedelta to avoid gaps
                # We always use next_invoice_date as the recurrence are synchronized with the invoicing periods.
                # Next invoice date is required and is equal to start_date at the creation of a subscription
                # new_period_start = self.order_id.next_invoice_date
                new_period_start = self.order_id._next_recur_date_same(self.order_id.next_invoice_date)
                new_period_start2 = self.order_id._next_recur_date(self.order_id.next_invoice_date)

            format_start = format_date(self.env, new_period_start2, lang_code=lang_code)

            parent_order_id = self.order_id.id
            if self.order_id.subscription_state == '7_upsell':
                # remove 1 day as normal people thinks in terms of inclusive ranges.
                next_invoice_date = self.order_id.next_invoice_date - relativedelta(days=1)
                next_invoice_date2 = next_invoice_date
                parent_order_id = self.order_id.subscription_id.id
            else:
                _logger.info("Duration days: %s", self.order_id.duration_days)
                _logger.info("Billing period unit: %s", self.order_id.plan_id.billing_period_unit or 'day')
                _logger.info("Plan ID: %s, Plan Name: %s", self.order_id.plan_id.id, self.order_id.plan_id.name)

                default_next_invoice_date2 = new_period_start2 + get_timedelta(self.order_id.duration_days,
                                                                                 self.order_id.plan_id.billing_period_unit or 'day')
                next_invoice_date2 = default_next_invoice_date2 - relativedelta(days=1)

            format_invoice = format_date(self.env, next_invoice_date2, lang_code=lang_code)
            description += _("\n%s to %s", format_start, format_invoice)

            qty_to_invoice = self._get_subscription_qty_to_invoice(last_invoiced_date=new_period_start2,
                                                                   next_invoice_date=next_invoice_date2)
            subscription_end_date = next_invoice_date2
            res['quantity'] = qty_to_invoice.get(self.id, 0.0)

            res.update({
                'name': description,
                # 'subscription_start_date': new_period_start2,
                # 'subscription_end_date': subscription_end_date,
                'subscription_id': parent_order_id,
                # 'dummy_subscription_end_date': new_period_start,
            })

            if account_id:
                res.update({'account_id': account_id.id})
        elif self.order_id.is_subscription:
            # This is needed in case we only need to invoice this line
            res.update({
                'subscription_id': self.order_id.id,
            })

            service_product_id = self.env['product.product'].search([
                                ('default_code', '=', 'RENTAL_SERVICE_CHARGE')
                            ], limit=1)
            service_line_id = self.order_id.order_line.filtered(lambda p: p.product_id.id == service_product_id.id)

            if service_line_id:
                res.update({
                    'quantity' : 1,
                })
                # Added on 13-11-24
                # if self.order_id.existing_order:
                #     res.update({'price_unit': service_line_id.price_to_set_subscrition})
        return res

    #Added on 13-11-24 for existing order run
    def _get_protected_fields(self):
        res = super(SaleOrderLine, self)._get_protected_fields()
        if self.order_id.existing_order:
            res = [
                'product_id', 'name', 'product_uom', 'product_uom_qty',
                'tax_id', 'analytic_distribution'
            ]
        return res

# Added by Nikita for change the order Date of Next invoice after create manually invoice
class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _create_invoices(self, sale_orders):
        for subscription in sale_orders:
            if subscription.is_subscription:
                # Rental lines
                rental_lines = subscription.order_line.filtered(lambda l: l.is_rental and l.qty_delivered == 0)

                # Subscription lines (only if recurring_invoice_line_ids exists)
                if hasattr(subscription, 'recurring_invoice_line_ids') and subscription.recurring_invoice_line_ids:
                    subscription_lines = subscription.order_line.filtered(
                        lambda l: l.product_id in subscription.recurring_invoice_line_ids.mapped('product_id')
                    )
                else:
                    subscription_lines = self.env['sale.order.line']  # empty recordset

                # Combine safely
                lines = rental_lines | subscription_lines

                # Process each line
                for line in lines:
                    if line.qty_delivered == 0:
                        line.qty_delivered = 1
                    if line.price_unit == 0:
                        line.price_unit = line.price_to_set_subscrition
                    if hasattr(subscription, 'recurring_invoice_line_ids') and subscription.recurring_invoice_line_ids:
                        if line.product_id in subscription.recurring_invoice_line_ids.mapped('product_id'):
                            if subscription.team_id.is_website:
                                line.price_unit = line.price_to_set_subscrition
                            else:
                                if subscription.invoice_count > 0:
                                    line.price_unit = line.price_to_set_subscrition

        # Call super to create invoices
        res = super(SaleAdvancePaymentInv, self)._create_invoices(sale_orders)

        # Update next invoice dates for rental lines
        for sale in sale_orders:
            rental_lines = sale.order_line.filtered(lambda l: l.is_rental)
            if not rental_lines:
                _logger.warning("No rental lines found for sale order %s", sale.name)
                continue

            lang_code = sale.partner_id.lang
            new_date = sale._next_recur_date(rental_lines[0].return_date)
            default_next_invoice_date = new_date + get_timedelta(
                sale.duration_days, sale.plan_id.billing_period_unit or 'day'
            )
            next_invoice_date = default_next_invoice_date - relativedelta(days=1)
            rental_lines[0].return_date = next_invoice_date
            sale._compute_rental_status()
            sale._update_next_invoice_date()

        return res


    # def _create_invoices(self, sale_orders):
    #     for subscription in sale_orders:
    #         if subscription.is_subscription:
    #             lines = subscription.order_line.filtered(lambda x: x.is_rental and x.qty_delivered == 0)
    #             line1 = subscription.order_line.filtered(lambda x: x.product_id.id == subscription.recurring_invoice_line_ids.product_id)
    #             lines += line1

    #             for line in lines:
    #                 if line.qty_delivered == 0:
    #                     line.qty_delivered = 1
    #                 if line.price_unit == 0:
    #                     line.price_unit = line.price_to_set_subscrition
    #                 if line.product_id.id == subscription.recurring_invoice_line_ids.product_id:
    #                     if subscription.team_id.is_website:
    #                         line.price_unit = line.price_to_set_subscrition
    #                     else:
    #                         if subscription.invoice_count > 0:
    #                             line.price_unit = line.price_to_set_subscrition

    #     res = super(SaleAdvancePaymentInv, self)._create_invoices(sale_orders)

    #     for sale in sale_orders:
    #         lines = sale.order_line.filtered(lambda x: x.is_rental)
    #         if not lines:
    #             _logger.warning("No rental lines found for sale order %s", sale.name)
    #             continue  # skip this sale order


    #         lang_code = sale.partner_id.lang
    #         new_date = sale._next_recur_date(lines[0].return_date)
    #         default_next_invoice_date = new_date + get_timedelta(sale.duration_days,
    #                                                                      sale.plan_id.billing_period_unit or 'day')
    #         next_invoice_date = default_next_invoice_date - relativedelta(days=1)
    #         lines[0].return_date = next_invoice_date
    #         sale._compute_rental_status()
    #         sale._update_next_invoice_date()
    #     return res