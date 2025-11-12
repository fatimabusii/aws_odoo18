from odoo import http,fields,tools,SUPERUSER_ID,_
from odoo.http import request
from datetime import datetime, date
# from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.tools.misc import flatten
import logging
import json
import calendar
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class WebsiteSaleCustom(WebsiteSale):

    @http.route()
    def cart(self, **post):
        order = request.website.sale_get_order()
        deposite_product_id = request.env['product.product'].search([
                                ('default_code', '=', 'RENTAL_DEPOSIT')
                            ], limit=1)
        categ_id = request.env.ref('bluespace_website_16.product_category_office')
        service_product_id = request.env['product.product'].search([
                                ('default_code', '=', 'RENTAL_SERVICE_CHARGE')
                            ], limit=1)
        if order :
            pp_id = []
            cat_list = []
            flag = False

            fpos = order.fiscal_position_id or order.fiscal_position_id._get_fiscal_position(order.partner_id)
            product_taxes = deposite_product_id.sudo().taxes_id.filtered(lambda tax: tax.company_id == order.company_id)
            taxes = fpos.map_tax(product_taxes)
            start_date = ''
            product = False

            for line in order.order_line:
                if line.product_id.id not in pp_id:
                    pp_id.append(line.product_id.id)
                    flag = True if (line.product_id.is_office or line.product_id.is_boardroom) else False
                    start_date = line.start_date
                    product = line.product_id if (line.product_id.product_category in ['1_storage_unit', '4_parking']) else False

            total_service_charge = order.compute_product_service_charge(product, start_date)

            if order.total_deposit_amount and deposite_product_id.id not in pp_id and not flag:
                deposite_product_id.sudo().list_price = order.total_deposit_amount #order.compute_product_deposit(product) + total_service_charge if total_service_charge else order.total_deposit_amount
                vals = {'product_id': deposite_product_id.id, 
                    'name' : deposite_product_id.name,
                    'product_uom_qty': 1, 
                    'order_id': order.id, 
                    'linked_line_id': False, 
                    'price_unit': order.total_deposit_amount, #order.compute_product_deposit(product) + total_service_charge if total_service_charge else order.total_deposit_amount,
                    'tax_id': [x.id for x in taxes],
                    }
                request.env['sale.order.line'].with_user(SUPERUSER_ID).create(vals)

            if order.total_service_charge and service_product_id.id not in pp_id and not flag:
                service_product_id.sudo().list_price = order.compute_product_service_charge(product, start_date) #order.total_service_charge
                vals = {'product_id': service_product_id.id, 
                    'name' : service_product_id.name,
                    'product_uom_qty': 1, 
                    'order_id': order.id, 
                    'linked_line_id': False, 
                    'price_unit': order.compute_product_service_charge(product, start_date) #order.total_service_charge
                    }
                request.env['sale.order.line'].with_user(SUPERUSER_ID).create(vals)

        return super().cart(**post)


    # @http.route()
    # def cart_update_json(
    #     self, product_id, line_id=None, add_qty=None, set_qty=None, display=True,
    #     product_custom_attribute_values=None, no_variant_attribute_values=None, **kw
    # ):
    #     res = super().cart_update_json(product_id, line_id, add_qty, set_qty, display, product_custom_attribute_values, no_variant_attribute_values, **kw)
    #     order = request.website.sale_get_order()
    #     deposite_product_id = request.env['product.product'].search([
    #                             ('default_code', '=', 'RENTAL_DEPOSIT')
    #                         ], limit=1)
    #     service_product_id = request.env['product.product'].search([
    #                             ('default_code', '=', 'RENTAL_SERVICE_CHARGE')
    #                         ], limit=1)
    #     if not order.order_line and order.no_of_visitors:
    #         order.no_of_visitors = 0

    #     deposit_service_line = order.order_line.filtered(lambda p: p.product_id.id == deposite_product_id.id or p.product_id.id == service_product_id.id)

    #     if not order.is_office_boardroom_order and order.total_deposit_amount == 0.0:
    #         deposit_service_line.unlink()
    #         return request.redirect("/shop/cart")

    #     if order.order_line:
    #         p1 = []
    #         for line in order.order_line:
    #             if (line.product_id.is_boardroom  or line.product_id.is_office) :
    #                 attribute_line_id = line.product_id.product_tmpl_id.attribute_line_ids.filtered(lambda p: p.attribute_id.name == 'Size')
    #                 prod_size = int(attribute_line_id.value_ids[0].name)
    #                 if not order.no_of_visitors:
    #                     raise UserError(_("Please enter the No of Persons!!!"))
    #                 if line.product_id.is_office :
    #                     if prod_size == 16 and order.no_of_visitors > 4 :
    #                         raise UserError(_("Please note, this office can only accommodate a maximum of 4 people."))
    #                     if prod_size == 17 and order.no_of_visitors > 6 :
    #                         raise UserError(_("Please note, this office can only accommodate a maximum of 6 people."))
    #                     if prod_size == 20 and order.no_of_visitors > 8 :
    #                         raise UserError(_("Please note, this office can only accommodate a maximum of 8 people."))
    #                     if prod_size == 41 and order.no_of_visitors > 17 :
    #                         raise UserError(_("Please note, this office can only accommodate a maximum of 17 people."))
    #                 if line.product_id.is_boardroom :
    #                     if prod_size == 16 and order.no_of_visitors > 6 :
    #                         raise UserError(_("Please note, this boardroom can only accommodate a maximum of 6 people."))
    #                     if prod_size == 19 and order.no_of_visitors > 10 :
    #                         raise UserError(_("Please note, this boardroom can only accommodate a maximum of 10 people."))

    #             if product_id in p1 and line.product_id.id == product_id and (line.product_id.is_boardroom  or line.product_id.is_office):
    #                 raise UserError(_("One Product Already in cart."))
    #             if line.product_id.id != product_id:
    #                 raise UserError(_("One Product Already in cart."))
    #             '''if (line.product_id.is_boardroom  or line.product_id.is_office) and line.price_subtotal == 0.0:
    #                 raise UserError(_("You are eligible for 2 hrs free boardroom booking. Please contact sales person to book the boardroom."))'''
    #             if product_id not in p1:
    #                 p1.append(line.product_id.id)
    #     return res
