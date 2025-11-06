# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import calendar
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date
from pytz import timezone, UTC
from odoo.tools import format_datetime, format_time
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
import pytz
import sys
import holidays
from odoo.http import request

from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

from odoo.tools.date_utils import get_timedelta
from dateutil.parser import parse
def parse_date(date):
    return date and parse(date).replace(tzinfo=None)

class SalesTeam(models.Model):
    _inherit = 'crm.team'

    is_website = fields.Boolean(string="Is Website")

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_flexible = fields.Boolean(string="Flexible(M2M)")
    is_specific_move = fields.Boolean(string="Specific move out")
    is_office_boardroom_order = fields.Boolean(string="Office Boardroom Order")
    ofc_visitors = fields.One2many('office.visitors', 'sale_id', string="visitors")
    no_of_visitors = fields.Integer("No of Visitors")
    free_office = fields.Boolean(string="Free Office")
    free_boardroom = fields.Boolean(string="Free Boardroom")
    is_notice_given = fields.Boolean('Is Notice Given')
    notice_given = fields.Boolean(string="Notice Given")
    notice_given_date = fields.Date(string="Notice Given Month-Year")
    is_paid = fields.Boolean(string='Is Paid?', compute='_update_payment_status',store=True)
    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'),
        ('12', 'December')], string="Notice Given Month-Year")
    year_id = fields.Many2one('year.year', string="Year")
    is_approved_order = fields.Boolean(string="Need Order Confirmation?")
    lease_confirm = fields.Boolean(string="Is Lease Confirm")
    is_website = fields.Boolean("Website Order", related="team_id.is_website", store=True)

    def action_lease_confirm(self):
        action = self.env['ir.actions.act_window']._for_xml_id('bluespace_custom_16.lease_confirm_wizard_action')
        ctx = dict(self.env.context)
        ctx.pop('active_id', None)
        ctx['active_ids'] = self.ids
        ctx['active_model'] = 'sale.order'
        ctx['is_office_boardroom_order'] = self.is_office_boardroom_order
        action['context'] = ctx
        return action

    @api.onchange('is_flexible')
    def _onchange_is_flexible(self):
        if self.is_flexible and self.is_specific_move and not self.team_id.is_website:
            self.is_specific_move = False

    @api.onchange('is_specific_move')
    def _onchange_is_specific_move(self):
        if self.is_specific_move and self.is_flexible and not self.team_id.is_website:
            self.is_flexible = False

    # def set_close(self):
    #     res = super(SaleOrder, self).set_close()
    #     if self.partner_id:
    #         self.message_subscribe(partner_ids=self.partner_id.ids)
    #     return res

    @api.model
    def _cron_eft_cancel_order(self):
        domain = [('state', '=', 'sent'), ('is_paid', '=', False)]
        sale_ids = self.sudo().search(domain)
        dd = self.env.company.unit_days
        cancel_date = fields.Date.today() + timedelta(days=dd)
        cancel_list = sale_ids.filtered(lambda x: (fields.Date.today() - x.date_order.date()).days > dd)
        cancel_list.write({'state': 'cancel'})

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if self.order_line:
            self = self.with_context(do_not_create_extra=True)
        if not default:
            default = {}

        sale_order = self.browse(self.id)

        # Initialize a list to store the new order lines
        new_order_lines = []
        product = self.env['product.product'].search([('name','=', 'Recurring'),('recurring_invoice','=', True)], limit=1)
        for line in sale_order.order_line:
            if line.product_id.id == product.id:
                continue
            new_order_lines.append((0, 0, line.copy_data()[0]))

        default['order_line'] = new_order_lines

        res = super(SaleOrder, self).copy(default)
        res.update({'is_flexible': self.is_flexible, 'is_specific_move': self.is_specific_move})
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super(SaleOrder, self).create(vals_list)
        deposite_product_id = self.env['product.product'].search([
                                ('default_code', '=', 'RENTAL_DEPOSIT')
                            ], limit=1)
        for line in res.order_line :
            if not line.product_id.recurring_invoice or line.product_id.id != deposite_product_id.id :
                if line.product_id.is_office or line.product_id.is_boardroom and res.team_id.is_website:
                    res.is_office_boardroom_order = True
                else:
                    if res.team_id.is_website:
                        res.is_office_boardroom_order = False
                    if line.start_date and not line.return_date and res.team_id.is_website:
                        res.is_flexible = True
                    if line.start_date and line.return_date and res.team_id.is_website:
                        res.is_specific_move = True
                res.is_rental_order = True
                res.is_recurring_rental = True
                if line.product_id.product_category in ['1_storage_unit', '2_office', '3_boardroom', '4_parking']:
                    line.is_rental = True
        return res

    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        for record in self:
            line_ids = record.order_line.filtered(lambda x: x.product_id.product_category in ['1_storage_unit', '2_office', '3_boardroom', '4_parking'])
            if len(line_ids) > 1 and not record.is_website:
                raise UserError('Not allow to more than one rental product! Create a new order!')
            if len(line_ids) == 1:
                line_ids.is_rental = True
                vals['is_rental_order'] = True
                vals['is_recurring_rental'] = True
        return result

    def _cron_process_given_notice(self):
        sale_ids = self.env['sale.order'].search([('is_notice_given', '=', True), ('notice_given', '=', False), ('state', 'not in', ['cancel', 'draft'])])
        for rec in sale_ids:
            #notiec_give_date = rec.end_date + relativedelta(months=-1)
            #notiec_give_date = notiec_give_date + relativedelta(days=1)
            if rec.end_date.replace(day=1) == fields.Date.today():
                rec.notice_given = True

    @api.onchange('month', 'year_id')
    def _onchange_notice_date(self):
        for rec in self:
            if rec.month and rec.year_id:
                if rec.date_order.year > int(rec.year_id.name):
                    raise UserError(_('Please select valid year.'))
                elif rec.date_order.year == int(rec.year_id.name) and rec.date_order.month >= int(rec.month):
                    raise UserError(_('Please select valid month and year.'))
                days = calendar.monthrange(int(rec.year_id.name), int(rec.month))[1]
                end_date = "{}/{}/{}".format(rec.month, days, rec.year_id.name)
                make_end_date = datetime.strptime(end_date, '%m/%d/%Y')
                rec.end_date = make_end_date


    @api.depends('invoice_ids','invoice_ids.payment_state')
    def _update_payment_status(self):
        for rec in self:
            rec.is_paid = False
            if rec.invoice_ids:
                if all(line.payment_state in ('paid','in_payment') for line in rec.invoice_ids.filtered(lambda x: x.move_type == 'out_invoice' and x.payment_state != 'reversed')):
                    rec.is_paid = True
                    p_ids = rec.mapped('order_line').mapped('product_template_id')
                    for p in p_ids:
                        if 'warehouse' in p.name.lower():
                            rec.partner_id.free_office = True
                            break
                        else:
                            rec.partner_id.free_office = False
                        p.is_available = False

    def get_message(self):
        order_message = ""
        order_message = self.env['ir.config_parameter'].sudo().get_param('auto_rental.order_message')
        return order_message

    def is_office_boardroom_product(self):
        for record in self:
            if record.order_line:
                is_office_filterd = record.order_line.mapped('product_id').filtered(lambda x: x.is_office)
                is_boardroom_filterd = record.order_line.mapped('product_id').filtered(lambda x: x.is_boardroom)
                if is_office_filterd:
                    is_office = all(product.is_office for product in record.order_line.mapped('product_id'))
                    return is_office
                if is_boardroom_filterd:
                    is_boardroom = all(product.is_boardroom for product in record.order_line.mapped('product_id'))
                    return is_boardroom
        return False


    def prepare_date_move_out(self, move_in_date):
        if move_in_date:
            if move_in_date.day <= 20:
                mv_dt=move_in_date.replace(day = calendar.monthrange(move_in_date.year, move_in_date.month)[1])
                return mv_dt
            else:
                date_after_month = move_in_date + relativedelta(months=1)
                mv_dt=date_after_month.replace(day = calendar.monthrange(date_after_month.year, date_after_month.month)[1])
                return mv_dt

    def get_month_dic(self):
        return {
            'January' : 1,
            'February' : 2,
            'March' : 3,
            'April' : 4,
            'May' : 5,
            'June' : 6,
            'July' : 7,
            'August' : 8,
            'September' : 9,
            'October' : 10,
            'November' : 11,
            'December' : 12,
        }

    def prepare_date_move_out_formate(self, move_out_date):
        if move_out_date:
            out_date_list = move_out_date.split(' ')
            if len(out_date_list) >=1:
                currunt_month = self.get_month_dic().get(out_date_list[0])
                currunt_year = out_date_list[1]
                days = calendar.monthrange(int(currunt_year), currunt_month)[1]
                end_date = "{}/{}/{}".format(currunt_month, days, currunt_year)
                move_out_date = datetime.strptime(end_date, '%m/%d/%Y')
                return move_out_date

    def _get_client_time(self, convet_date):
        from datetime import datetime
        atten_time = datetime.strptime(fields.Datetime.from_string(convet_date).strftime(DEFAULT_SERVER_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT)
        user_tz = self.env.context.get('tz')
        #local_tz = pytz.timezone(user_tz)
        local_tz = pytz.timezone('Asia/Kolkata')
        local_dt = local_tz.localize(atten_time, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        utc_dt = utc_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        convert_date = datetime.strptime(utc_dt, DEFAULT_SERVER_DATETIME_FORMAT)
        return convert_date

    # def _prepare_order_line_values(
    #     self, product_id, quantity, start_date=None, end_date=None, **kwargs
    # ):
    #     """Add corresponding pickup and return date to rental line"""
    #     values = super()._prepare_order_line_values(product_id, quantity, **kwargs)
    #     product = self.env['product.product'].browse(product_id)
    #     self.is_flexible = False
    #     self.is_specific_move = False
    #     self.is_office_boardroom_order = False
    #     user_tz = self.env.context.get('tz')
    #     #cat_id = self.env.ref('bluespace_website_16.product_category_office')

    #     if product.is_office:
    #         self.is_office_boardroom_order = True
    #     if product.is_boardroom:
    #         self.is_office_boardroom_order = True

    #     if (product.is_office or product.is_boardroom) and start_date:
    #         #start_date = self._get_client_time(start_date)
    #         #end_date = self._get_client_time(end_date)
    #         values.update({
    #                 'start_date': start_date,
    #                 'return_date': end_date,
    #                 'is_rental': True,
    #             })
    #         self.is_rental_order = True
    #         self.is_recurring_rental = True

    #         if 'no_of_visitors' in kwargs and kwargs.get('no_of_visitors'):
    #             self.no_of_visitors = int(kwargs.get('no_of_visitors'))
    #         return values
    #     else:
    #         move_in_date = datetime.strptime(kwargs.get('move_in_date'), '%m/%d/%Y')
    #         if product.rent_ok and start_date and end_date:
    #             end_date_kevin = self.prepare_date_move_out(move_in_date)
    #             if 'is_move_out_date' in kwargs and kwargs.get('is_move_out_date') and kwargs.get('move_out_date'):
    #                 # move_out_date = datetime.strptime(kwargs.get('move_out_date'), '%m/%d/%Y')
    #                 move_out_date = self.prepare_date_move_out_formate(kwargs.get('move_out_date'))
    #                 values.update({
    #                     'start_date': move_in_date,
    #                     'return_date': end_date_kevin if end_date_kevin else move_out_date,
    #                     'is_rental': True,
    #                 })
    #                 if end_date_kevin and move_out_date:
    #                     mv_dt=move_out_date.replace(day = calendar.monthrange(move_out_date.year, move_out_date.month)[1])
    #                     self.end_date = move_out_date
    #                     self.is_recurring_rental = True
    #                     self.is_specific_move = True
    #             if 'flexible_move_out' in kwargs and kwargs.get('flexible_move_out'):
    #                 values.update({
    #                     'start_date': move_in_date,
    #                     'return_date': end_date_kevin if end_date_kevin else move_out_date,
    #                     'is_rental': True,
    #                 })
    #                 self.is_flexible = True
    #                 mv_dt=end_date_kevin.replace(day = calendar.monthrange(end_date_kevin.year, end_date_kevin.month)[1])
    #                 if mv_dt:
    #                     self.end_date = mv_dt
    #             self.is_rental_order = True
    #             self.is_recurring_rental = True
    #     return values

    def _next_recur_date(self, start_date):
        res = super(SaleOrder, self)._next_recur_date(start_date)
        current_date = fields.Date.today()
        if type(res) == type(current_date):
            if res == current_date:
                wh_product_id = self.mapped('order_line').mapped('product_template_id')
                for p in wh_product_id:
                    if 'warehouse' in p.name.lower():
                        self.partner_id.free_office = True
                        break
        return res

    def _compute_type_name(self):
        other_orders = self.env['sale.order']
        for order in self:
            if not (order.is_subscription and order.state in ('sale', 'done')):
                other_orders |= order
                continue
            order.type_name = _('Confirmed Booking')

        super(SaleOrder, other_orders)._compute_type_name()

    def product_available(self, product_id, date1, sale_line_ids):
        not_avail = False
        if sale_line_ids:
            last_dt = False
            for line in sale_line_ids.filtered(lambda x: x.order_id.is_notice_given and x.order_id.is_flexible):
                dt1 = datetime.strptime("1 " + line.order_id.month+ " " + line.order_id.year_id.name, "%d %m %Y").date()
                last_dt = dt1.replace(day = calendar.monthrange(dt1.year, dt1.month)[1])
            for line in sale_line_ids.filtered(lambda x: x.order_id.is_specific_move):
                if not last_dt or (last_dt and line.order_id.end_date and last_dt < line.order_id.end_date):
                    last_dt = line.order_id.end_date
            if last_dt and date1.date() <= last_dt :
                not_avail = True
        return not_avail

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    allocated_hours = fields.Float("Allocated Time", compute='_compute_allocated_hours', store=True, readonly=False)

    @api.model
    def create(self, vals):
        if 'do_not_create_extra' in self.env.context:
            return super(SaleOrderLine, self).create(vals)
        # res = super(SaleOrderLine, self).create(vals)
        if vals.get('product_id',False):
            product_obj = self.env['product.product']
            product_id = product_obj.browse(vals['product_id'])
            order_id = vals.get('order_id',False)
            sale_order_id = self.env['sale.order'].browse(order_id)

            deposite_product_id = self.env['product.product'].search([
                                ('default_code', '=', 'RENTAL_DEPOSIT')
                            ], limit=1)
            deposit_in_order = sale_order_id.order_line.filtered(lambda x: x.product_id.id == deposite_product_id.id)
            service_product_id = self.env['product.product'].search([
                                ('default_code', '=', 'RENTAL_SERVICE_CHARGE')
                            ], limit=1)

            if product_id.product_category in ['1_storage_unit', '2_office', '3_boardroom', '4_parking'] and not sale_order_id.team_id.is_website:
                fpos = sale_order_id.fiscal_position_id or sale_order_id.fiscal_position_id._get_fiscal_position(sale_order_id.partner_id)
                product_taxes = deposite_product_id.sudo().taxes_id.filtered(lambda tax: tax.company_id == sale_order_id.company_id)
                taxes = fpos.map_tax(product_taxes)

                max_sequence = max(sale_order_id.order_line.mapped('sequence'), default=0)
                vals['sequence'] = 2

                date1 = vals.get('start_date', False)
                if date1:
                    if not isinstance(date1, str):
                        start_date = date1
                    else:
                        start_date = datetime.strptime(date1, "%Y-%m-%d %H:%M:%S")
                        
                    line_vals_deposit = {
                        'order_id': order_id,
                        'product_id': deposite_product_id.id,
                        'name': deposite_product_id.name,
                        'price_unit':(product_id.deposit_amount + product_id.service_charge)*1.15,
                        'product_uom_qty': 1,
                        'product_uom': deposite_product_id.uom_id.id,
                        'tax_id': [x.id for x in taxes],
                        'is_rental': False,
                        'sequence': 1,
                    }
                    line1 = self.env['sale.order.line'].sudo().create(line_vals_deposit)

                    if product_id.product_category in ['1_storage_unit', '2_office', '3_boardroom']:
                        total_service_charge = sale_order_id.compute_product_service_charge(product_id, start_date)
                        service_product_id.sudo().lst_price = total_service_charge

                        line_vals_service = {
                            'order_id': order_id,
                            'product_id': service_product_id.id,
                            'name': service_product_id.name,
                            'price_unit': total_service_charge,
                            'product_uom_qty': 1,
                            'product_uom': service_product_id.uom_id.id,
                            'is_rental': False,
                            'sequence': 4,
                        }
                        line2 = self.env['sale.order.line'].sudo().create(line_vals_service)
            else:
                if product_id.product_category not in ['1_storage_unit', '2_office', '3_boardroom', '4_parking'] \
                and not sale_order_id.is_website and product_id.rent_ok:
                    vals['is_rental'] = True
                else:
                    vals['is_rental'] = False

                rec_product = self.env['product.product'].search([('name','=', 'Recurring'),('recurring_invoice','=', True)], limit=1)

                if product_id.product_category not in ['1_storage_unit', '2_office', '3_boardroom', '4_parking'] \
                and not product_id.rent_ok and vals['product_id'] not in [deposite_product_id.id, service_product_id.id, rec_product.id]:
                    max_seq = max(sale_order_id.order_line.mapped('sequence'), default=0)
                    vals['sequence'] = max_seq + 1

        res = super(SaleOrderLine, self).create(vals)
        return res

    def write(self, vals):
        result = super(SaleOrderLine, self).write(vals)
        for record in self:
            deposite_product_id = self.env['product.product'].search([
                                ('default_code', '=', 'RENTAL_DEPOSIT')
                            ], limit=1)
            deposit_in_order = record.order_id.order_line.filtered(lambda x: x.product_id.id == deposite_product_id.id)
            service_product_id = self.env['product.product'].search([
                                ('default_code', '=', 'RENTAL_SERVICE_CHARGE')
                            ], limit=1)

            if record.product_id.product_category in ['1_storage_unit', '2_office', '3_boardroom', '4_parking'] \
            and not record.order_id.team_id.is_website:
                vals['is_rental'] = True
                date1 = vals.get('start_date', False)
                if not record.order_id.is_recurring_rental: #11-4-25
                    record.order_id.is_recurring_rental = True
                if date1 and not deposit_in_order:
                    if not isinstance(date1, str):
                        start_date = date1
                    else:
                        start_date = datetime.strptime(date1, "%Y-%m-%d %H:%M:%S")

                    fpos = record.order_id.fiscal_position_id or record.order_id.fiscal_position_id._get_fiscal_position(record.order_id.partner_id)
                    product_taxes = deposite_product_id.sudo().taxes_id.filtered(lambda tax: tax.company_id == record.order_id.company_id)
                    taxes = fpos.map_tax(product_taxes)

                    line_vals_deposit = {
                        'order_id': record.order_id.id,
                        'product_id': deposite_product_id.id,
                        'name': deposite_product_id.name,
                        'price_unit':(record.product_id.deposit_amount + record.product_id.service_charge)*1.15,
                        'product_uom_qty': 1,
                        'product_uom': deposite_product_id.uom_id.id,
                        'tax_id': [x.id for x in taxes],
                        'is_rental': False,
                        'sequence': 1,
                    }
                    line1 = self.env['sale.order.line'].sudo().create(line_vals_deposit)

                    if record.product_id.product_category in ['1_storage_unit', '2_office', '3_boardroom']:
                        total_service_charge = record.order_id.compute_product_service_charge(record.product_id, start_date)
                        service_product_id.sudo().lst_price = total_service_charge

                        line_vals_service = {
                            'order_id': record.order_id.id,
                            'product_id': service_product_id.id,
                            'name': service_product_id.name,
                            'price_unit': total_service_charge,
                            'product_uom_qty': 1,
                            'product_uom': service_product_id.uom_id.id,
                            'is_rental': False,
                            'sequence': 4,
                        }
                        line2 = self.env['sale.order.line'].sudo().create(line_vals_service)
            else:
                if record.product_id.product_category not in ['1_storage_unit', '2_office', '3_boardroom', '4_parking'] \
                and not record.order_id.team_id.is_website and record.product_id.rent_ok:
                    vals['is_rental'] = True
                else:
                    vals['is_rental'] = False

            # product = self.env['product.product'].search([('name','=', 'Recurring'),('recurring_invoice','=', True)], limit=1)
            # if vals.get('price_unit', False) and record.product_id.id == product.id and not record.order_id.team_id.is_website:
            #     if record.order_id.invoice_count == 0:
            #         record.price_unit = 0
            #         record.qty_delivered = 0

            # deposite_product_id = self.env.ref('bluespace_website_16.rental_deposite')
            # if record.product_id.id != deposite_product_id.id and not record.order_id.team_id.is_website:
            #     print("",record.order_id)
            # if record.order_id.is_office_boardroom_order and record.start_date and record.return_date and not record.order_id.team_id.is_website:
            #     diff = relativedelta(record.return_date, record.start_date) #record.return_date - record.start_date
            #     if diff.days == 0 and diff.hours == 0:
            #         raise UserError("Minimum booking is 1 hour.")
        return result

    def _compute_qty_delivered(self):
        super()._compute_qty_delivered()
        for sale_line in self:
            if sale_line.is_rental and not sale_line.order_id.team_id.is_website and sale_line.order_id.state in ['sale', 'done']:
                sale_line.qty_delivered = sale_line.product_uom_qty

    def compute_allocated_hours_for_existing(self):
        for slot in self:
            if slot.product_template_id.product_category in ('2_office', '3_boardroom'):
                slot.allocated_hours = slot._calculate_slot_duration()
            else:
                slot.allocated_hours = 0.0

    def _calculate_slot_duration(self):
        self.ensure_one()
        if self.product_template_id.product_category in ('2_office', '4_boardroom'):
            period = self.return_date - self.start_date
            if period:
                slot_duration = period.total_seconds() / 3600
                max_duration = (period.days + 1) * self.company_id.resource_calendar_id.hours_per_day
                if not max_duration or max_duration >= slot_duration:
                    return slot_duration
                return max_duration
        else:
            return 0

    @api.depends('start_date', 'return_date')
    def _compute_allocated_hours(self):
        for slot in self:
            if slot.product_template_id.product_category in ('2_office', '3_boardroom'):
                slot.allocated_hours = slot._calculate_slot_duration()
            else:
                slot.allocated_hours = 0.0

    # @api.depends('order_id.plan_id', 'product_id', 'product_uom', 'product_uom_qty')
    # def _compute_price_unit(self):
    #     res = super(SaleOrderLine, self)._compute_price_unit()
    #     deposite_product_id = self.env['product.product'].search([
    #                             ('default_code', '=', 'RENTAL_DEPOSIT')
    #                         ], limit=1)
    #     service_product_id = self.env['product.product'].search([
    #                             ('default_code', '=', 'RENTAL_SERVICE_CHARGE')
    #                         ], limit=1)
    #     for line in self:
    #         if line.product_id.id == deposite_product_id.id:
    #             line.price_unit = line.order_id.total_deposit_amount

    #         if line.product_id.id == service_product_id.id:
    #             line.price_unit = line.order_id.total_service_charge

    #         if line.product_id.id != deposite_product_id.id and line.product_id.id != service_product_id.id:
    #             if line.start_date:
    #                 line.price_unit = line.compute_line_price(line.product_id, line.start_date, line.return_date)
    #             else:
    #                 price = line._get_display_price()
    #                 # line.price_unit = line.product_id._get_tax_included_unit_price_from_price(
    #                 #     price,
    #                 #     line.currency_id or line.order_id.currency_id,
    #                 #     product_taxes=line.product_id.taxes_id.filtered(
    #                 #         lambda tax: tax.company_id == line.env.company
    #                 #     ),
    #                 #     fiscal_position=line.order_id.fiscal_position_id,
    #                 # )
    #                 line.price_unit = line.product_id._get_tax_included_unit_price_from_price(
    #                     price,
    #                     product_taxes=line.product_id.taxes_id.filtered(lambda tax: tax.company_id == line.env.company),
    #                     fiscal_position=line.order_id.fiscal_position_id,
    #                 )
    #     return res
    @api.depends('order_id.plan_id', 'product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        _logger.info("Starting _compute_price_unit for %d lines", len(self))
        
        res = super(SaleOrderLine, self)._compute_price_unit()

        deposite_product_id = self.env['product.product'].search([
            ('default_code', '=', 'RENTAL_DEPOSIT')
        ], limit=1)
        service_product_id = self.env['product.product'].search([
            ('default_code', '=', 'RENTAL_SERVICE_CHARGE')
        ], limit=1)

        _logger.info("Deposits product found: %s", deposite_product_id)
        _logger.info("Service product found: %s", service_product_id)

        for line in self:
            if not line.product_id:
                _logger.warning("Line %s has no product assigned, skipping price computation", line.id)
                continue

            _logger.info("Computing price for line %s with product %s", line.id, line.product_id.display_name)

            if line.product_id.id == deposite_product_id.id:
                line.price_unit = line.order_id.total_deposit_amount
                _logger.info("Line %s is deposit product, setting price_unit to %s", line.id, line.price_unit)

            elif line.product_id.id == service_product_id.id:
                line.price_unit = line.order_id.total_service_charge
                _logger.info("Line %s is service product, setting price_unit to %s", line.id, line.price_unit)

            else:
                if line.start_date:
                    line.price_unit = line.compute_line_price(line.product_id, line.start_date, line.return_date)
                    _logger.info(
                        "Line %s has start_date, computed price_unit via compute_line_price: %s",
                        line.id, line.price_unit
                    )
                else:
                    price = line._get_display_price()
                    if not line.product_id:
                        _logger.warning("Line %s has no product_id for tax-included price, skipping", line.id)
                        continue
                    line.price_unit = line.product_id._get_tax_included_unit_price_from_price(
                        price,
                        product_taxes=line.product_id.taxes_id.filtered(lambda tax: tax.company_id == line.env.company),
                        fiscal_position=line.order_id.fiscal_position_id,
                    )
                    _logger.info(
                        "Line %s computed price_unit via _get_tax_included_unit_price_from_price: %s",
                        line.id, line.price_unit
                    )
        return res


    def compute_line_price(self,  prd_id, start_date, end_date):
        price = 0
        # if prd_tmpl_id.product_category in ['2_office', '3_boardroom'] :
        #     start_date = start_date
        #     end_date = end_date or start_date
        #     delta = relativedelta(end_date, start_date)
        #     self.get_time_validation(prd_tmpl_id.id, start_date, end_date)
        #     if delta:
        #         sa_holidays = holidays.SouthAfrica()
        #         holiday_count = len(sa_holidays[start_date.date(): end_date.date()])
        #         weekend_count = 0
        #         d = end_date - start_date
        #         for i in range(d.days+1):
        #             day = start_date + timedelta(days=i)
        #             if(day.weekday()>4):
        #                 weekend_count = weekend_count + 1
        #         price = prd_tmpl_id.with_context(holiday_count=holiday_count,weekend_count=weekend_count,days=d.days)._compute_hours(self.product_template_id, delta)
        #         if request.session.get('uid'):
        #             uid = request.session.get('uid')
        #             part_id = self.env['res.users'].sudo().browse(uid).mapped('partner_id')
        #             sol_ids = self.sudo().search([('order_id.partner_id', '=', part_id.id), ('product_id.product_category', '=', '1_storage_unit'), ('order_id.stage_category', '!=', 'closed'), ('state', 'not in', ['draft', 'cancel'])])
        #             flag = False
        #             for line in sol_ids:
        #                 if start_date.date() >= line.start_date.date() and line.return_date.date() >= start_date.date():
        #                     flag = True

        #             if part_id.free_office and flag:
        #                 if not d.days and delta.hours < 2 or (delta.hours == 2 and delta.minutes == 0):
        #                     price = 0
        #                 else :
        #                     remain_hours = delta + timedelta(hours=-2)
        #                     price = prd_tmpl_id.with_context(holiday_count=holiday_count,weekend_count=weekend_count,days=d.days)._compute_hours(self.product_template_id, remain_hours)
        #         return price
        # else:
        if start_date:
            start_date = start_date
            end_date = end_date or start_date
            if start_date.day == 1 or start_date.day <=20:
                end_date = start_date.replace(day = calendar.monthrange(start_date.year, start_date.month)[1])
            else:
                date_after_month = start_date + relativedelta(months=1)
                end_date=date_after_month.replace(day = calendar.monthrange(date_after_month.year, date_after_month.month)[1])
            product = prd_id
            delta = relativedelta(end_date, start_date)
            quantity = 1
            if start_date.day==1:
                price = product.list_price
                if delta.months and delta.months !=1:
                    delta.months=delta.months+1
                else:
                    delta.months=1
                no_of_extra_day=0
            elif start_date.day <= 20:
                mv_dt=start_date.replace(day = calendar.monthrange(start_date.year, start_date.month)[1])
                extra_day=mv_dt-start_date
                no_of_extra_day=extra_day.days + 1
                first_month_rent=product.one_day_rent * no_of_extra_day
                price=first_month_rent
            elif start_date.day==30 or start_date.day==31:
                if start_date.month == date.today().month:
                    delta.months=delta.months
                else:
                    delta.months=delta.months+1
                mv_dt=start_date.replace(day = calendar.monthrange(start_date.year, start_date.month)[1])
                extra_day=mv_dt-start_date
                no_of_extra_day=extra_day.days + 1
                first_month_rent=product.one_day_rent * no_of_extra_day
                next_month_first_date=end_date.replace(day=1)
                next_month_rent=self.order_id.pricelist_id._get_product_price(
                    product, quantity, start_date=next_month_first_date, end_date=end_date
                )
                price=first_month_rent+next_month_rent
            else:
                mv_dt=start_date.replace(day = calendar.monthrange(start_date.year, start_date.month)[1])
                extra_day=mv_dt-start_date
                no_of_extra_day=extra_day.days + 1
                first_month_rent=product.one_day_rent * no_of_extra_day
                next_month_first_date=end_date.replace(day=1)
                next_month_rent=self.order_id.pricelist_id._get_product_price(
                    product, quantity, start_date=next_month_first_date, end_date=end_date
                )
                price=first_month_rent+next_month_rent
        return price

    def get_time_validation(self, prd_id, start_date, end_date):
        s_dt1 = start_date
        e_dt1 = end_date
        domain1 = [
            ('product_id', '=', prd_id),
            ('state', 'in', ['send', 'sale', 'done','sent']),
            ('order_id.subscription_state', '!=', '6_churn')
            ]
        sale_line_ids = self.sudo().search(domain1)
        if s_dt1:
            for sol in sale_line_ids:
                if sol.start_date.date() == s_dt1.date():
                    s_dt2 = sol.start_date
                    e_dt2 = sol.return_date
                    if s_dt2.time() <= s_dt1.time() and e_dt2.time() >= s_dt1.time():
                        if (s_dt2.time() <= s_dt1.time() and e_dt2.time() > s_dt1.time()):
                            raise UserError(_('You are not able to booking this slot. Please select another time.'))
                    elif (s_dt2.time() >= s_dt1.time() and e_dt1.time() >= e_dt2.time()):
                        raise UserError(_('You are not able to booking this slot. Please select another time.'))
                    elif (s_dt2.time() > s_dt1.time() and e_dt1.time() > s_dt2.time() and e_dt1.time() < e_dt2.time()):
                        raise UserError(_('You are not able to booking this slot. Please select another time.'))

    def get_date_validation(self, prd_id, start_date, end_date):
        s_dt1 = start_date and start_date.date()
        e_dt1 = end_date and end_date.date()
        domain1 = [
            ('product_id', '=', prd_id.id),
            ('state', 'in', ['send', 'sale', 'done','sent']),
            ('order_id.subscription_state', '!=', '6_churn')
            ]
        sale_line_ids = self.sudo().search(domain1)
        if s_dt1:
            for sol in sale_line_ids:
                s_dt2 = sol.start_date.date() if sol.start_date else False
                e_dt2 = sol.return_date.date() if sol.return_date else False
                if s_dt2 <= s_dt1 and e_dt2 >= s_dt1:
                    if (s_dt2 <= s_dt1 and e_dt2 > s_dt1):
                        raise UserError(_('You are not able to booking this period.'))
                elif (s_dt2 >= s_dt1 and e_dt1 >= e_dt2):
                    raise UserError(_('You are not able to booking this period.'))
                elif (s_dt2 > s_dt1 and e_dt1 > s_dt2 and e_dt1 < e_dt2):
                    raise UserError(_('You are not able to booking this period.'))

    def compute_return_date(self, start_date):
        return_date = start_date
        if start_date and start_date.day > self.env.company.date_of_invoice:
            mv_dt = start_date + get_timedelta(1, 'month')
            return_date = mv_dt.replace(day = calendar.monthrange(mv_dt.year, mv_dt.month)[1])
        else:
            return_date = start_date and start_date.replace(day = calendar.monthrange(start_date.year, start_date.month)[1])
        return return_date

    @api.onchange('start_date')
    def _onchange_start_date(self):
        price = 0
        start_date = self.start_date
        end_date = self.return_date or self.start_date
        # Commented for existing order
        # if start_date and start_date.date() < fields.date.today():
        #     raise UserError(_('You cannot book order for past date!'))
        if self.product_id:
            price = self.compute_line_price(self.product_id, start_date, end_date)
            if not self.order_id.is_website and self.product_id.product_category in ['1_storage_unit', '2_office', '3_boardroom', '4_parking']:
                return_date = self.compute_return_date(start_date)
                self.return_date = return_date
                self.get_date_validation(self.product_id, self.start_date, self.return_date)

        self.price_unit = price

    @api.onchange('return_date')
    def _onchange_return_date(self):
        price = 0
        start_date = self.start_date
        end_date = self.return_date
        if self.product_id:
            price = self.compute_line_price(self.product_id, start_date, end_date)
        self.price_unit = price
        # if self.product_template_id.product_category in ['1_storage_unit', '4_parking'] and not self.order_id.team_id.is_website and self.order_id.is_specific_move:
        #     self.order_id._origin.end_date = self.return_date.date()

        # if self.product_template_id.product_category in ['2_office', '3_boardroom'] and not self.order_id.team_id.is_website:
        #     self.get_time_validation(self.product_template_id.id, start_date, end_date)

        if not self.order_id.team_id.is_website and self.order_id.is_specific_move and self.return_date:
            self.order_id._origin.end_date = self.return_date.date()

    def _get_rental_order_line_description(self):
        tz = self._get_tz()
        #cat_id = self.env.ref('bluespace_website_16.product_category_office')
        if self.start_date and self.return_date\
           and self.start_date.replace(tzinfo=UTC).astimezone(timezone(tz)).date()\
               == self.return_date.replace(tzinfo=UTC).astimezone(timezone(tz)).date():
            # If return day is the same as pickup day, don't display return_date Y/M/D in description.
            return_date_part = format_time(self.with_context(use_babel=True).env, self.return_date, tz=tz, time_format=False)
        else:
            return_date_part = format_datetime(self.with_context(use_babel=True).env, self.return_date, tz=tz, dt_format=False)

        if self.order_id and self.order_id.is_recurring_rental and self.start_date and self.order_id.end_date and not (self.product_id.is_office or self.product_id.is_boardroom) and self.order_id.is_specific_move:
            return "\n%s\n%s %s %s\n%s %s" % (_("Renting period"), self.start_date.date(), _("to"), self.return_date.date(), _("End Date:"), self.order_id.end_date)
        
        if self.start_date and self.return_date and return_date_part and self.order_id.is_flexible:
            return "\n%s\n%s %s %s" % (_("Renting period"), self.start_date.date(), _("to"), self.return_date.date())

        if self.start_date and self.return_date and return_date_part and self.order_id.is_office_boardroom_order:
            return "\n%s\n%s %s %s" % (
                _("Renting period"),
                format_datetime(self.with_context(use_babel=True).env, self.start_date, tz=tz, dt_format=False),
                _("to"),
                return_date_part,
            )

        return "\n%s\n%s %s %s" % (
            _("Renting period"),
            format_datetime(self.with_context(use_babel=True).env, self.start_date, tz=tz, dt_format=False),
            _("to"),
            return_date_part,
        )

    @api.onchange('product_id')
    def onchange_product_id(self):
        ProductProduct = self.env['product.product'].sudo()
        SaleOrderLine = self.env['sale.order.line'].sudo()

        products = ProductProduct.search([
            ('product_category', 'in', ('2_office', '3_boardroom', '1_storage_unit', '4_parking'))
        ])

        products.write({'available_now': False})

        domain = [
            ('product_id', 'in', products.ids),
            ('state', 'in', ['send', 'sale', 'done', 'sent']),
            ('order_id.subscription_state', '!=', '6_churn'),
        ]
        active_lines = SaleOrderLine.search(domain)
        active_product_ids = active_lines.mapped('product_id').ids
        inactive_products = products.filtered(lambda p: p.id not in active_product_ids)
        inactive_products.write({'available_now': True})

    @api.onchange('product_template_id')
    def onchange_product_template_id(self):
        ProductTemplate = self.env['product.template'].sudo()
        SaleOrderLine = self.env['sale.order.line'].sudo()

        products = ProductTemplate.search([
            ('product_category', 'in', ('2_office', '3_boardroom', '1_storage_unit', '4_parking'))
        ])

        products.write({'available_now': False})

        domain = [
            ('product_template_id', 'in', products.ids),
            ('state', 'in', ['send', 'sale', 'done', 'sent']),
            ('order_id.subscription_state', '!=', '6_churn'),
        ]
        active_lines = SaleOrderLine.search(domain)
        active_product_ids = active_lines.mapped('product_template_id').ids
        inactive_products = products.filtered(lambda p: p.id not in active_product_ids)
        inactive_products.write({'available_now': True})

class OfficeVisitors(models.Model):
    _name = 'office.visitors'
    _description = "Visitors"

    name = fields.Char(string="Name")
    cell_phone = fields.Char(string="Cell Phone Number")
    sale_id = fields.Many2one('sale.order', string="Sales Order")


class Year(models.Model):
    _name = "year.year"
    _description = "Year"

    name = fields.Char(string="Year", copy=False)
