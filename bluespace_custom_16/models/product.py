from odoo import models, fields, api, _
from datetime import datetime,timedelta,date
import calendar
from odoo.http import request
from dateutil import relativedelta
from odoo import http
from odoo.http import request
import pytz
import holidays
# from odoo.addons.website_sale_renting.models.product_template import ProductTemplate

from odoo.exceptions import UserError

# def _get_default_renting_dates1(
#         self, start_date, end_date, only_template, website, duration, unit
#     ):
#     """ Get default renting dates to help user

#     :param datetime start_date: a start_date which is directly returned if defined
#     :param datetime end_date: a end_date which is directly returned if defined
#     :param bool only_template: whether only the template information are needed, in this case,
#                                there will be no need to give the default renting dates.
#     :param Website website: the website currently browsed by the user
#     :param int duration: the duration expressed in int, in the unit given
#     :param string unit: The duration unit, which can be 'hour', 'day', 'week' or 'month'
#     """
#     if start_date and end_date and start_date >= end_date:
#         raise UserError(_("Please choose a return date that is after the pickup date."))

#     if start_date or end_date or only_template:
#         return start_date, end_date

#     if website and request:
#         sol_rental = website.sale_get_order().order_line.filtered('is_rental')[:1]
#         if sol_rental:
#             end_date = max(
#                 sol_rental.return_date,
#                 self._get_default_end_date(sol_rental.start_date, duration, unit)
#             )
#             return sol_rental.start_date, end_date

#     default_date = self._get_default_start_date()
#     return default_date, self._get_default_end_date(default_date, duration, unit)

# ProductTemplate._get_default_renting_dates = _get_default_renting_dates1

class Products(models.Model):
    _inherit = 'product.template'
   
    one_day_rent=fields.Float('One Day Rent', default=1.0,digits='Product Price',
        help="Price at which the product is sold to customers.",compute="_compute_one_day_rent"
    )
    is_office = fields.Boolean(string="Is Office?", default=False)
    is_boardroom = fields.Boolean(string="Is Boardroom?", default=False)
    available_now = fields.Boolean('Available', default=True)
    
    @api.depends('list_price')
    def _compute_one_day_rent(self):
        for product in self:
            product.one_day_rent=(product.list_price*12)/365

    def _compute_hours(self, product, delta):
        current_total_price = 0
        per_hr = 0
        per_half_day = 0
        per_day = 0
        per_week = 0
        total_days = self.env.context.get('days')
        for price in product.product_pricing_ids:
            if price.plan_id.unit == 'hour' and price.plan_id.duration == 1:
                per_hr = price.price
            if price.plan_id.unit == 'hour' and price.plan_id.duration == 4:
                per_half_day = price.price
            if price.plan_id.unit == 'day':
                per_day = price.price
            if price.plan_id.unit == 'week':
                per_week = price.price
        if delta.hours < 4 and not total_days:
            current_total_price = delta.hours * per_hr
            if delta.minutes:
                tt = ((delta.minutes/60) * per_hr)
                current_total_price += ((delta.minutes/60) * per_hr)
        elif delta.hours >= 4 and delta.hours < 9 and not total_days:
            current_total_price = per_half_day
        elif delta.hours >= 9 and not total_days:
            current_total_price = per_day
        elif (delta.hours >= 9 and not total_days) or (total_days < 5):
            dd = total_days
            if self.env.context.get('holiday_count'):
                dd -= self.env.context.get('holiday_count')
            if self.env.context.get('weekend_count'):
                dd -= self.env.context.get('weekend_count')
            current_total_price = per_day * dd
            if delta.hours >= 9:
                current_total_price += per_day
            if delta.hours >= 4 and delta.hours < 9:
                current_total_price += per_half_day
            if delta.hours < 4:
                current_total_price += delta.hours * per_hr
                if delta.minutes:
                    current_total_price += ((delta.minutes/60) * per_hr)
        elif total_days >= 5 :
            dd = total_days
            if self.env.context.get('holiday_count'):
                dd -= self.env.context.get('holiday_count')
            if self.env.context.get('weekend_count'):
                dd -= self.env.context.get('weekend_count')

            week = int(dd / 5)
            days = int(dd % 5)
            current_total_price = per_week * week
            current_total_price += (per_day * days)
            if delta.hours >= 9:
                current_total_price += per_day
            if delta.hours >= 4 and delta.hours < 9:
                current_total_price += per_half_day
            if delta.hours < 4:
                current_total_price += delta.hours * per_hr
                if delta.minutes:
                    current_total_price += ((delta.minutes/60) * per_hr)
        return current_total_price

    # def _get_combination_info(
    #     self, combination=False, product_id=False, add_qty=1, pricelist=False,
    #     parent_combination=False, only_template=False
    # ):
    #     self.ensure_one()

    #     res = super()._get_combination_info(
    #         combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
    #         parent_combination=parent_combination, only_template=only_template
    #     )


    #     if self.rent_ok:
    #         if self.env.context.get('website_id'):
    #             website = self.env['website'].get_current_website()
    #             pricelist = pricelist or website._get_current_pricelist()
    #         else:
    #             website = False
    #     current_total_price=0.0
        
    #     month_duration = ''
    #     m1 = 0
    #     d1 = 0
    #     res['month_days']=''
    #     res['free_office_msg']=''
    #     move_in_date=request.session.get('start_date')
    #     move_out_date=request.session.get('end_date')
    #     t=request.httprequest.args.getlist('move_out_date')
    #     if move_in_date:
    #         move_in_date=datetime.strptime(request.session.get('start_date'), '%m/%d/%Y').date()
    #     if move_out_date:
    #         move_out_date=datetime.strptime(request.session.get('end_date'), '%m/%d/%Y').date()
    #     start_date = self.env.context.get('start_date') or move_in_date
    #     end_date = move_out_date if move_out_date else self.env.context.get('end_date') 
    #     product = self.env['product.product'].browse(res['product_id'])
    #     quantity = self.env.context.get('quantity', add_qty)
    #     no_of_extra_day=0

    #     user_tz = self.env.context.get('tz') or 'UTC'
    #     #cat_id = self.env.ref('bluespace_website_16.product_category_office')
    #     if user_tz and (start_date or end_date) and (product.is_office or product.is_boardroom):
    #         start1 = pytz.utc.localize(start_date)
    #         start1 = start1.astimezone(pytz.timezone(user_tz))
    #         end1 = pytz.utc.localize(end_date)
    #         end1 = end1.astimezone(pytz.timezone(user_tz))
    #         delta = relativedelta.relativedelta(end1, start1)
    #         sa_holidays = holidays.SouthAfrica()
    #         holiday_count = len(sa_holidays[start1.date(): end1.date()])
    #         weekend_count = 0
    #         d = end1 - start1
    #         for i in range(d.days+1):
    #             day = start1 + timedelta(days=i)
    #             if(day.weekday()>4):
    #                 weekend_count = weekend_count + 1
    #         current_total_price = self.with_context(holiday_count=holiday_count,weekend_count=weekend_count,days=d.days)._compute_hours(product, delta)
    #         if d.days:
    #             dd = d.days + 1 - weekend_count - holiday_count
    #             week = int(dd / 5)
    #             days = int(dd % 5)
    #             if week:
    #                 res['month_days'] = str(week) + ' Week(s) ' + str(days) + ' Days ' + str(delta.hours) + ' Hours ' + str(delta.minutes) + ' Minutes'
    #             else:
    #                 res['month_days'] = str(days) + ' Days ' + str(delta.hours) + ' Hours ' + str(delta.minutes) + ' Minutes'
    #         else:
    #             res['month_days'] = str(delta.hours) + ' Hours ' + str(delta.minutes) + ' Minutes'
    #         res['current_rental_price'] = res['price'] = current_total_price
            
    #         if request.session.get('uid'):
    #             uid = request.session.get('uid')
    #             part_id = self.env['res.users'].sudo().browse(uid).mapped('partner_id')
    #             sol_ids = self.env['sale.order.line'].sudo().search([('order_id.partner_id', '=', part_id.id), ('product_id.product_category', '=', '1_storage_unit'), ('order_id.subscription_state', '!=', '6_churn'), ('state', 'not in', ['draft', 'cancel'])])
    #             flag = False
    #             for line in sol_ids:
    #                 if start1.date() >= line.start_date.date() and line.return_date.date() >= start1.date():
    #                     flag = True
    #             if part_id.free_office and flag:
    #                 if not d.days and delta.hours < 2 or (delta.hours == 2 and delta.minutes == 0):
    #                     if product.is_boardroom:
    #                         res['free_office_msg'] = 'You are eligible for 2 hrs free boardroom booking. Please contact sales person to book the boardroom.'
    #                     else:
    #                         res['free_office_msg'] = 'You are eligible for 2 hrs free office booking. Please contact sales person to book the office.'
    #                     res['current_rental_price'] = res['price'] = 0
    #                 else:
    #                     remain_hours = delta + timedelta(hours=-2)
    #                     current_total_price = self.with_context(holiday_count=holiday_count,weekend_count=weekend_count,days=d.days)._compute_hours(product, remain_hours)
    #                     res['free_office_msg'] = 'You are eligible for 2hr free office/boardroom.' #So you can only pay for ' + str(remain_hours.hours) + ' Hours and ' + str(remain_hours.minutes) +' minutes.'
    #                     res['current_rental_price'] = res['price'] = current_total_price
    #     else:
    #         if start_date:
    #             start_date = start_date + timedelta(days=1)
    #             end_date = end_date + timedelta(days=1)
    #             delta = relativedelta.relativedelta(end_date, start_date)
    #             if start_date.day==1:
    #                 current_total_price = product.list_price
    #                 if delta.months and delta.months !=1:
    #                     delta.months=delta.months+1
    #                 else:
    #                     delta.months=1
    #                 no_of_extra_day=0
    #             elif start_date.day <= 20:
    #                 if start_date.day == 20 :
    #                     delta.months=delta.months - 1
    #                 mv_dt=start_date.replace(day = calendar.monthrange(start_date.year, start_date.month)[1])
    #                 extra_day=mv_dt-start_date
    #                 no_of_extra_day=extra_day.days + 1
    #                 first_month_rent=product.one_day_rent * no_of_extra_day
    #                 current_total_price=first_month_rent
    #             elif start_date.day==30 or start_date.day==31:
    #                 if start_date.month == date.today().month:
    #                     delta.months=delta.months
    #                 else:
    #                     delta.months=delta.months
    #                 mv_dt=start_date.replace(day = calendar.monthrange(start_date.year, start_date.month)[1])
    #                 extra_day=mv_dt-start_date
    #                 no_of_extra_day=extra_day.days + 1
    #                 first_month_rent=product.one_day_rent * no_of_extra_day
    #                 next_month_first_date=end_date.replace(day=1)
    #                 next_month_rent=pricelist._get_product_price(
    #                     product or self, quantity, start_date=next_month_first_date, end_date=end_date
    #                 )
    #                 current_total_price=first_month_rent+next_month_rent
    #             else:
    #                 mv_dt=start_date.replace(day = calendar.monthrange(start_date.year, start_date.month)[1])
    #                 extra_day=mv_dt-start_date
    #                 no_of_extra_day=extra_day.days + 1
    #                 first_month_rent=product.one_day_rent * no_of_extra_day
    #                 next_month_first_date=end_date.replace(day=1)
    #                 next_month_rent=pricelist._get_product_price(
    #                     product or self, quantity, start_date=next_month_first_date, end_date=end_date
    #                 )
    #                 current_total_price=first_month_rent+next_month_rent
    #             res['current_rental_price'] = res['price'] = current_total_price
    #             res['month_days'] = str(delta.months) + ' Months ' + str(no_of_extra_day) + ' Days'
    #     return res

    def _get_product_category(self):
        cat_id = self.env.ref('bluespace_website_16_new.product_category_office')
        return cat_id.id

class ProductProduct(models.Model):
    _inherit = 'product.product'

    one_day_rent=fields.Float('One Day Rent', default=1.0,digits='Product Price',
        help="Price at which the product is sold to customers.",compute="_compute_one_day_rent"
    )
    available_now = fields.Boolean('Available', default=True)

    @api.depends('lst_price')
    def _compute_one_day_rent(self):
        for product in self:
            product.one_day_rent=(product.lst_price*12)/365

    def _get_product_category(self):
        cat_id = self.env.ref('bluespace_website_16_new.product_category_office')
        return cat_id.id

