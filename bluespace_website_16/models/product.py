from odoo import api, fields, models, _
import datetime
import calendar
from dateutil import relativedelta
from odoo.http import request
from datetime import timedelta
import holidays


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    deposit_amount = fields.Float("Deposit Amount")
    service_charge = fields.Float("Service Charge")
    is_office = fields.Boolean(string="Is Office?", default=False)


    def compute_available_qty(self):
        all_products = self.search([])
        for product in all_products:
            product.is_available = False
            order_ids = self.env['sale.order'].sudo().search([('state', 'in', ['send', 'sale', 'done','sent']), ('stage_category', '!=', 'closed')])
            own_product_ids = order_ids.mapped('order_line').mapped('product_template_id').filtered(lambda p: p.product_category not in ('office','boardroom'))
            deposite_product_id = self.env['product.product'].search([
                                ('default_code', '=', 'RENTAL_DEPOSIT')
                            ], limit=1)
            recurring_product = self.env['product.template'].search([('name','=', 'Recurring'),('recurring_invoice','=', True)], limit=1)
            if product.id not in own_product_ids.ids or product.id == deposite_product_id.id or product.id == recurring_product.id:
                product.is_available = True

    # def _compute_available(self):
    #     for product in self:
    #         product.is_available = False
    #         order_ids = self.env['sale.order'].sudo().search([('state', 'in', ['send', 'sale', 'done','sent']), ('stage_category', '!=', 'closed')])
    #         own_product_ids = order_ids.mapped('order_line').mapped('product_template_id').filtered(lambda p: p.product_category not in ('office','boardroom'))
    #         deposite_product_id = request.env.ref('bluespace_website_16.rental_deposite')
    #         recurring_product = self.env['product.template'].search([('name','=', 'Recurring'),('recurring_invoice','=', True)], limit=1)
    #         if product.id not in own_product_ids.ids or product.id == deposite_product_id.id or product.id == recurring_product.id:
    #             product.is_available = True

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_deposit_amount = fields.Monetary(string="Deposit Amount", store=True, compute='_compute_deposit_amounts')
    total_service_charge = fields.Monetary(string="Service Charge", store=True, compute='_compute_service_charge')

    @api.depends('order_line.total_deposit_amount')
    def _compute_deposit_amounts(self):
        for order in self:
            deposit_amount = 0.0
            for line in order.order_line:
                deposit_amount += line.total_deposit_amount
            order.update({
                'total_deposit_amount': deposit_amount,
            })

    @api.depends('order_line.total_service_charge')
    def _compute_service_charge(self):
        for order in self:
            service_charge = 0.0
            for line in order.order_line:
                if line.total_service_charge:
                    service_charge = line.total_service_charge
            order.update({
                'total_service_charge': service_charge,
            })

    def _prepare_order_line_values(
        self, product_id, quantity, start_date=None, end_date=None, **kwargs
    ):
        values = super()._prepare_order_line_values(product_id, quantity, **kwargs)
        product = self.env['product.product'].browse(product_id)
        values.update({'total_deposit_amount' : product.deposit_amount, 'total_service_charge' : product.service_charge})
        return values

    def get_rental_product(self):
        deposite_product_id = self.env['product.product'].search([
                                ('default_code', '=', 'RENTAL_DEPOSIT')
                            ], limit=1)
        return deposite_product_id

    def get_service_product(self):
        service_product_id = self.env['product.product'].search([
                                ('default_code', '=', 'RENTAL_SERVICE_CHARGE')
                            ], limit=1)
        return service_product_id

    def compute_product_service_charge(self, product, start_date):
        if product:
            product_tmpl_id = product.product_tmpl_id
            if start_date.day == 1 :
                amt = product_tmpl_id.service_charge
            elif start_date.day <= self.env.company.date_of_invoice :
                last_dt = start_date.replace(day = calendar.monthrange(start_date.year, start_date.month)[1])
                amt = product_tmpl_id.service_charge*12/365*((last_dt - start_date).days + 1)
            else:
                last_dt = start_date.replace(day = calendar.monthrange(start_date.year, start_date.month)[1])
                amt = product_tmpl_id.service_charge + (product_tmpl_id.service_charge*12/365*((last_dt - start_date).days + 1))
            return amt

    def compute_product_deposit(self, product):
        if product:
            product_tmpl_id = product.product_tmpl_id
            amt = product_tmpl_id.deposit_amount
            return amt


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    total_deposit_amount = fields.Monetary(
        string="Deposit Amount",
        compute='_compute_amount',
        store=True, precompute=True)
    
    total_service_charge = fields.Monetary(
        string="Service Charge",
        compute='_compute_amount',
        store=True, precompute=True)


    def compute_total_deposit_amount(self, amt):
        line = self.order_id.order_line.filtered(lambda p: p.product_id.product_category in ['1_storage_unit', '4_parking'])
        if line:
            product_tmpl_id = line.product_id.product_tmpl_id
            last_dt = line.start_date.replace(day = calendar.monthrange(line.start_date.year,line. start_date.month)[1])
            amt = line.product_id.deposit_amount + product_tmpl_id.service_charge*12/365*((last_dt - line.start_date).days + 1)
        return amt

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        
        for line in self:
            taxes = line.tax_id
            if line.order_id and line.order_id.fiscal_position_id:
                taxes = line.order_id.fiscal_position_id.map_tax(taxes, product=line.product_id, partner=line.order_id.partner_id)

            # tax_results = self.env['account.tax']._compute_taxes([line._convert_to_tax_base_line_dict()])
            # totals = list(tax_results['totals'].values())[0]
            # amount_untaxed = totals['amount_untaxed']
            # amount_tax = totals['amount_tax']

            res = taxes.compute_all(
                price_unit=line.price_unit,
                currency=line.order_id.currency_id,
                quantity=line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_id,
            )

            amount_untaxed = res.get('total_excluded', 0.0)
            amount_included = res.get('total_included', 0.0)
            # The tax amount is the difference (or directly from tax lines)
            amount_tax = amount_included - amount_untaxed

            # Or sum from `res['taxes']` (each tax detail)
            # amount_tax = sum(t.get('amount', 0.0) for t in res.get('taxes', []))

            # 3. Com

            # total_service_charge = line.order_id.get_service_product().lst_price if line.order_id.get_service_product().lst_price else line.product_id.service_charge

            total_service_charge = 0.0
            # You need to recalc it per your logic:
            if line.order_id.get_service_product():
                total_service_charge = line.order_id.get_service_product().list_price
            else:
                total_service_charge = line.product_id.service_charge or 0.0

            # line.update({
            #     'price_subtotal': amount_untaxed,
            #     'price_tax': amount_tax,
            #     'price_total': amount_untaxed + amount_tax,
            #     'total_deposit_amount': (line.product_id.deposit_amount + line.product_id.service_charge)*1.15,
            #     'total_service_charge': total_service_charge,
            # })
            # if self.env.context.get('import_file', False) and not self.env.user.user_has_groups('account.group_account_manager'):
            #     line.tax_id.invalidate_recordset(['invoice_repartition_line_ids'])

            line_vals = {
                'price_subtotal': amount_untaxed,
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax,
                'total_deposit_amount': (line.product_id.deposit_amount + line.product_id.service_charge) * 1.15,
                'total_service_charge': total_service_charge,
            }

            # If you still need this invalidation logic (import file context)
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups('account.group_account_manager'):
                line.tax_id.invalidate_recordset(['invoice_repartition_line_ids'])

            line.update(line_vals)

# class Pricelist(models.Model):
#     _inherit = "product.pricelist"

#     def _compute_hours(self, product, delta):
#         current_total_price = 0
#         per_hr = 0
#         per_half_day = 0
#         per_day = 0
#         per_week = 0
#         total_days = self.env.context.get('days')
#         for price in product.product_pricing_ids:
#             if price.recurrence_id.unit == 'hour' and price.recurrence_id.duration == 1:
#                 per_hr = price.price
#             if price.recurrence_id.unit == 'hour' and price.recurrence_id.duration == 4:
#                 per_half_day = price.price
#             if price.recurrence_id.unit == 'day':
#                 per_day = price.price
#             if price.recurrence_id.unit == 'week':
#                 per_week = price.price
#         if delta.hours < 4 and not delta.days:
#             current_total_price = delta.hours * per_hr
#             if delta.minutes:
#                 tt = ((delta.minutes/60) * per_hr)
#                 current_total_price += ((delta.minutes/60) * per_hr)
#         elif delta.hours >= 4 and delta.hours < 9 and not delta.days:
#             current_total_price = per_half_day
#         elif delta.hours >= 9 and not total_days:
#             current_total_price = per_day
#         elif (delta.hours >= 9 and not total_days) or (total_days and total_days < 5):
#             dd = total_days
#             if self.env.context.get('holiday_count'):
#                 dd -= self.env.context.get('holiday_count')
#             if self.env.context.get('weekend_count'):
#                 dd -= self.env.context.get('weekend_count')
#             current_total_price = per_day * dd
#             if delta.hours >= 9:
#                 current_total_price += per_day
#             if delta.hours >= 4 and delta.hours < 9:
#                 current_total_price += per_half_day
#             if delta.hours < 4:
#                 current_total_price += delta.hours * per_hr
#                 if delta.minutes:
#                     current_total_price += ((delta.minutes/60) * per_hr)
#         elif total_days >= 5 :
#             dd = total_days
#             if self.env.context.get('holiday_count'):
#                 dd -= self.env.context.get('holiday_count')
#             if self.env.context.get('weekend_count'):
#                 dd -= self.env.context.get('weekend_count')
#             week = int(dd / 5)
#             days = int(dd % 5)
#             current_total_price = per_week * week
#             current_total_price += (per_day * days)
#             if delta.hours >= 9:
#                 current_total_price += per_day
#             if delta.hours >= 4 and delta.hours < 9:
#                 current_total_price += per_half_day
#             if delta.hours < 4:
#                 current_total_price += delta.hours * per_hr
#                 if delta.minutes:
#                     current_total_price += ((delta.minutes/60) * per_hr)
#         return current_total_price
    



    # def _compute_price_rule(
    #     self, products, qty, uom=None, date=False, start_date=None, end_date=None, duration=None,
    #     unit=None, **kwargs
    # ):
    #     """ Override to handle the temporal product price

    #     Note that this implementation can be done deeper in the base price method of pricelist item
    #     or the product price compute method.
    #     """
    #     self.ensure_one()

    #     if not products:
    #         return {}

    #     if not date:
    #         date = fields.Datetime.now()

    #     results = {}
    #     if self._enable_temporal_price(start_date, end_date, duration, unit):
    #         temporal_products = products.filtered('is_temporal')
    #         Pricing = self.env['product.pricing']
    #         for product in temporal_products:
    
    #             current_total_price = product.list_price
    #             if start_date:
    #                 if start_date.day==31 or start_date.day == 1:
    #                     current_total_price = product.list_price
    #                 elif start_date.day + 1 <=self.env.company.date_of_invoice:
    #                     mv_dt=start_date.replace(day = calendar.monthrange(start_date.year, start_date.month)[1])
    #                     extra_day=mv_dt-start_date
    #                     no_of_extra_day=extra_day.days
    #                     first_month_rent=product.one_day_rent * no_of_extra_day
    #                     current_total_price=first_month_rent
    #                 else:
    #                     mv_dt=start_date.replace(day = calendar.monthrange(start_date.year, start_date.month)[1])
    #                     extra_day=mv_dt-start_date
    #                     no_of_extra_day=extra_day.days
    #                     first_month_rent=product.one_day_rent * no_of_extra_day
    #                     next_month_first_date=end_date.replace(day=1)
    #                     next_month_rent=product.product_pricing_ids.filtered(lambda s:s.recurrence_id.unit == 'month')
    #                     price = 0
    #                     if next_month_rent:
    #                         price = next_month_rent.price
    #                     current_total_price=first_month_rent + price
    #             results[product.id] = current_total_price, False
    #     # price_computed_products = self.env[products._name].browse(results.keys())
    #     # return {
    #     #     **results,
    #     #     **super()._compute_price_rule(
    #     #         products - price_computed_products, qty, uom=uom, date=date, **kwargs),
    #     # }
    #     remaining_products = products.filtered(lambda p: p.id not in results)
    #     super_results = {}
    #     if remaining_products:
    #         super_results = super()._compute_price_rule(remaining_products, qty, uom=uom, date=date, **kwargs)
    #     results.update(super_results)
    #     return results