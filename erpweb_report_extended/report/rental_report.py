# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, tools, api
from datetime import datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta
# from datequarter import DateQuarter
from datetime import date
from calendar import monthrange
import logging
_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    sales_count_report = fields.Float(compute='_compute_sales_count', string='Sold', digits='Product Unit of Measure', store=True)
    current_available = fields.Boolean(compute='_compute_current_available', store=True, string='Current Available')
    prd_size = fields.Char(string='Size', store=True, related="product_tmpl_id.prd_size")
    display_name1 = fields.Char(compute='_compute_display_name1', store=True)
    location_name = fields.Char(compute='_compute_location_name', store=True, string="Location Name")

    @api.depends('product_tmpl_id.attribute_line_ids')
    def _compute_location_name(self):
        for record in self:
            location_attribute_line = record.product_tmpl_id.attribute_line_ids.filtered(lambda x: x.attribute_id.name == 'Location')
            if len(location_attribute_line.value_ids) == 1:
                record.location_name = location_attribute_line.value_ids.name
            elif len(location_attribute_line.value_ids) > 1:
                record.location_name = record.product_template_variant_value_ids.mapped('product_attribute_value_id').name
            else:
                record.location_name = ''

    @api.depends('product_tmpl_id.attribute_line_ids', 'display_name', 'name', 'default_code')
    def _compute_display_name1(self):
        for record in self:
            record.display_name1 = record.display_name

    def _compute_sales_count(self):
        res = super(ProductProduct, self)._compute_sales_count()
        for product in self:
            product.sales_count_report = product.sales_count
        return res

    def _compute_current_available(self):
        products = self.sudo().search([('product_category', 'in', ('2_office', '3_boardroom', '1_storage_unit', '4_parking'))])
        for product in products:
            product.current_available = False
            domain1 = [
                ('product_id', '=', product.id),
                ('state', 'in', ['send', 'sale', 'done','sent']),
                ('order_id.subscription_state', '!=', '6_churn'),
                ]
            sale_line_ids = self.env['sale.order.line'].sudo().search(domain1)
            if not sale_line_ids:
                product.current_available = True

class ProductTemplate(models.Model):
    _inherit = "product.template"

    display_name1 = fields.Char(compute='_compute_display_name1', store=True)
    sales_count_report = fields.Float(compute='_compute_sales_count', string='Sold', digits='Product Unit of Measure', store=True)
    current_available = fields.Boolean(compute='_compute_current_available', store=True, string='Current Available')
    prd_size = fields.Char(string='Size', store=True)

    def _compute_display_name1(self):
        for record in self:
            record.display_name1 = record.display_name

    @api.depends('product_variant_ids.sales_count')
    def _compute_sales_count(self):
        res = super(ProductTemplate, self)._compute_sales_count()
        for product in self:
            product.sales_count_report = product.sales_count
        return res

    def _compute_current_available(self):
        products = self.sudo().search([('product_category', 'in', ('2_office', '3_boardroom', '1_storage_unit', '4_parking'))])
        for product in products:
            product.current_available = False
            domain1 = [
                ('product_template_id', '=', product.id),
                ('state', 'in', ['send', 'sale', 'done','sent']),
                ('order_id.subscription_state', '!=', '6_churn'),
                ]
            sale_line_ids = self.env['sale.order.line'].sudo().search(domain1)
            if not sale_line_ids:
                product.current_available = True

class RentalReportNew(models.Model):
    _name = "erpweb.sale.rental.report"
    _description = "Rental Analysis Report"
    _auto = False

    date = fields.Datetime('Date', readonly=True)
    order_id = fields.Many2one('sale.order', 'Order #', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure', readonly=True)
    quantity = fields.Float('Daily Ordered Qty', readonly=True)
    qty_delivered = fields.Float('Daily Picked-Up Qty', readonly=True)
    qty_returned = fields.Float('Daily Returned Qty', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    user_id = fields.Many2one('res.users', 'Salesman', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', readonly=True)
    #categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Sales Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True)
    price = fields.Float('Amount', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', readonly=True)
    move_in_date = fields.Datetime(string="Move In Date", readonly=True)
    move_out_date = fields.Datetime(string="Move Out Date", readonly=True)
    percent_occupation = fields.Float('Percent Occupation (%)', store=True)
    product_category = fields.Selection([
        ('1_storage_unit', 'Warehouse or Storage Unit'),
        ('2_office', 'First Floor Office'),
        ('3_boardroom', 'First Floor Boardroom'),
        ('4_parking', 'Parking Bay'),
    ], string='Product Category')
    name = fields.Char('Order Reference', readonly=True)
    color = fields.Integer(readonly=True)
    allocated_hours = fields.Float("Allocated Hours", readonly=True)
    is_flexible = fields.Boolean(string="Flexible(M2M)", readonly=True)
    is_specific_move = fields.Boolean(string="Specific move out", readonly=True)
    is_office_boardroom_order = fields.Boolean(string="Is Office Boardroom Order", readonly=True)
    notice_given = fields.Boolean(string="Notice Given", readonly=True)
    is_approved_order = fields.Boolean(string="Need Order Confirmation?", readonly=True)
    is_paid = fields.Boolean(string='Is Paid?', readonly=True)
    default_code = fields.Char('Internal Reference', readonly=True)
    product_size = fields.Char('Product Size', readonly=True)
    attribute_name = fields.Char('Product Attribute', readonly=True)
    value_name = fields.Char('Attribute Value', readonly=True)
    location_name = fields.Char('Location', readonly=True)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        result = super(RentalReportNew, self).read_group(
            domain, fields, groupby, offset=offset,
            limit=limit, orderby=orderby, lazy=lazy)
        products = self.env['product.product'].search([('product_category', 'in', ('2_office', '3_boardroom', '1_storage_unit', '4_parking'))])
        ctx = self.env.context
        for r in result :
            # if groupby and not r.get('date:month', False):
            #     for g in groupby:
            #         if g == 'product_category':
            #             products = self.env['product.product'].search(r.get('__domain', False))
            #             sale_order_lines = self.env['sale.order.line'].search([('state', 'not in', ['draft', 'cancel'])])
            #             total_sol = sale_order_lines.filtered(lambda s: s.product_id.id in products.ids)
            #             product_ids = total_sol.mapped('product_id')
            #             per = (len(product_ids) / len(products)) * 100
            #             r.update({'__count': per, 'percent_occupation':per})
            #         if g == 'product_id':
            #             products = self.env['product.product'].search([('id', '=', r.get('product_id')[0])])
            #             sale_order_lines = self.env['sale.order.line'].search([('state', 'not in', ['draft', 'cancel'])])
            #             total_sol = sale_order_lines.filtered(lambda s: s.product_id.id in products.ids)
            #             product_ids = total_sol.mapped('product_id')
            #             per = 0
            #             if len(products) > 0:
            #                 per = (len(product_ids) / len(products)) * 100
            #             r.update({'__count': per, 'percent_occupation':per})

            if r.get('date:month', False):
                dt = datetime.strptime("1 "+r['date:month'], "%d %B %Y").date()
                last_dt = dt.replace(day = calendar.monthrange(dt.year, dt.month)[1])
                sale_order_lines = self.env['sale.order.line'].search([('state', 'not in', ['draft', 'cancel']), ('order_id.start_date', '>=', dt)])
                total_sol = sale_order_lines.filtered(lambda s: s.start_date.month == dt.month)
                product_ids = total_sol.mapped('product_id')

                for d in domain:
                    if 'product_category' in d:
                        products = self.env['product.product'].search([d])
                        total_sol = sale_order_lines.filtered(lambda s: s.start_date.month == dt.month and s.product_id.id in products.ids)
                        product_ids = total_sol.mapped('product_id')

                per = (len(product_ids) / len(products)) * 100
                r.update({'percent_occupation':per})

            if r.get('date:week', False):
                wk = r['date:week']
                dt_week = wk.split(" ")
                start_date1 = datetime(int(dt_week[1]), 1, 1) + relativedelta(weeks=+int(dt_week[0][1:]))
                end_date1 = start_date1 + timedelta(days = 6)
                total_sol = self.env['sale.order.line'].search([('state', 'not in', ['draft', 'cancel']), ('start_date', '>=', start_date1), ('start_date', '<=', end_date1)])
                product_ids = total_sol.mapped('product_id')

                per = (len(product_ids) / len(products)) * 100
                r.update({'percent_occupation':per})

            if r.get('date:day', False):
                start_date1 = r['date:day'] #datetime(int(dt_week[1]), 1, 1) + relativedelta(weeks=+int(dt_week[0][1:]))
                dd = datetime.strptime(start_date1, "%d %b %Y").date()
                total_sol = self.env['sale.order.line'].search([('product_id', 'in', products.ids),('state', 'not in', ['draft', 'cancel']), ('start_date', '=', dd)])
                product_ids = total_sol.mapped('product_id')

                per = (len(product_ids) / len(products)) * 100
                r.update({'percent_occupation':per})

            if r.get('date:year', False):
                year1 = r['date:year'] #datetime(int(dt_week[1]), 1, 1) + relativedelta(weeks=+int(dt_week[0][1:]))
                firstday = datetime(int(year1), 1,1).date()
                lastday = datetime(int(year1), 12,31).date()
                total_sol = self.env['sale.order.line'].search([('product_id', 'in', products.ids),('state', 'not in', ['draft', 'cancel']), ('start_date', '>=', firstday), ('start_date', '<=', lastday)])
                product_ids = total_sol.mapped('product_id')

                per = (len(product_ids) / len(products)) * 100
                r.update({'percent_occupation':per})

            if r.get('date:quarter', False):
                qt = r['date:quarter'] #datetime(int(dt_week[1]), 1, 1) + relativedelta(weeks=+int(dt_week[0][1:]))
                qtt = int(qt[1:3])
                yr = int(qt[3:])
                # firstday = DateQuarter(yr, qtt).start_date()
                # lastday = DateQuarter(yr, qtt).end_date()
                firstday, lastday = self.quarter_range(yr, qtt)
                total_sol = self.env['sale.order.line'].search([('product_id', 'in', products.ids),('state', 'not in', ['draft', 'cancel']), ('start_date', '>=', firstday), ('start_date', '<=', lastday)])
                product_ids = total_sol.mapped('product_id')

                per = (len(product_ids) / len(products)) * 100
                r.update({'percent_occupation':per})

            if r.get('product_category', False):
                products = self.env['product.product'].search([('product_category', '=', r['product_category'])])
                sale_order_lines = self.env['sale.order.line'].search([('product_id', 'in', products.ids),('state', 'not in', ['draft', 'cancel'])])
                total_sol = sale_order_lines.filtered(lambda s: s.product_id.id in products.ids)
                product_ids = total_sol.mapped('product_id')

                per = (len(product_ids) / len(products)) * 100
                r.update({'percent_occupation':per})

        return result
    

    def quarter_range(year, quarter):
        """Return the first and last day (date objects) of the given quarter."""
        if quarter not in (1, 2, 3, 4):
            raise ValueError("Quarter must be between 1 and 4")
        
        # First month of the quarter
        first_month = 3 * (quarter - 1) + 1
        last_month = first_month + 2

        first_day = date(year, first_month, 1)
        last_day = date(year, last_month, monthrange(year, last_month)[1])
        return first_day, last_day

    def _quantity(self):
        return """
            sol.product_uom_qty / (u.factor * u2.factor) AS quantity,
            sol.qty_delivered / (u.factor * u2.factor) AS qty_delivered,
            sol.qty_returned / (u.factor * u2.factor) AS qty_returned
        """

    def _price(self):
        return """
            CASE WHEN pt.product_category in ('2_office', '3_boardroom', '1_storage_unit', '4_parking') THEN
                sol.price_subtotal
            ELSE 0
            END
        """

    def _color(self):
        """2 = orange (notice period/month), 4 = blue(Booked, but not moved in), 6 = red(Occupied. i.e. moved in), 10 = green(Open unit/Vacant)"""
        return """
            CASE WHEN s.state = 'cancel' THEN 0
                WHEN s.state in ('sale', 'done') AND s.subscription_state = '6_churn' THEN 10
                WHEN s.is_notice_given = True THEN 2
                WHEN s.state = 'sent' THEN 11
                WHEN s.state = 'draft' THEN 3
                WHEN s.is_approved_order = True THEN 9
                WHEN s.state in ('sale', 'done') AND sol.qty_delivered = sol.product_uom_qty THEN 6
                WHEN s.state in ('sale', 'done') AND (sol.qty_delivered = 0 OR sol.qty_delivered IS NULL OR s.subscription_state in ('1_draft', '3_progress')) THEN 4
            ELSE 0
            END as color
        """

    def _select(self):
        return """
            sol.id,
            sol.order_id,
            sol.product_id,
            s.name as name,
            %s,
            sol.product_uom,
            sol.order_partner_id AS partner_id,
            sol.salesman_id AS user_id,
            p.product_tmpl_id,
            s.start_date as date,
            %s AS price,
            sol.company_id,
            sol.state,
            sol.currency_id,
            s.start_date AS move_in_date,
            CASE
                WHEN s.is_specific_move AND s.is_website THEN s.end_date
            ELSE
                s.rental_return_date
            END AS move_out_date,
            pt.product_category AS product_category,
            ((CASE
                WHEN (sol.product_id = p.id) AND s.state not in ('draft', 'cancel') THEN sum(sol.price_unit)
            END)/ sum(pt.list_price)
            ) * 100 as percent_occupation,
            sol.allocated_hours AS allocated_hours,
            s.is_flexible as is_flexible,
            s.is_specific_move as is_specific_move,
            s.is_office_boardroom_order as is_office_boardroom_order,
            s.is_notice_given as notice_given,
            s.is_approved_order as is_approved_order,
            s.is_paid as is_paid,
            p.display_name1 as default_code,
            pt.prd_size as product_size,
            pa.name AS attribute_name,
            pav.name AS value_name,
            p.location_name AS location_name,
            %s
        """% (self._quantity(), self._price(), self._color())

    def _from(self):
        return """
            sale_order_line AS sol
            join sale_order s on (sol.order_id=s.id)
            join product_product AS p on p.id=sol.product_id
            join product_template AS pt on p.product_tmpl_id=pt.id
            join uom_uom AS u on u.id=sol.product_uom
            join uom_uom AS u2 on u2.id=pt.uom_id
            JOIN product_template_attribute_line ptl ON ptl.product_tmpl_id = pt.id
            JOIN product_attribute pa ON pa.id = ptl.attribute_id
            JOIN product_attribute_value_product_template_attribute_line_rel pav_rel ON pav_rel.product_template_attribute_line_id = ptl.id
            JOIN product_attribute_value pav ON pav.id = pav_rel.product_attribute_value_id
        """

    def _groupby(self):
        return """
            pt.product_category,
            pt.prd_size,
            pt.display_name1,
            sol.id,
            sol.product_id,
            sol.order_id,
            s.date_order,
            s.start_date,
            s.rental_return_date,
            s.name,
            u.factor,
            u2.factor,
            p.product_tmpl_id,
            s.subscription_state,
            s.state,
            s.is_notice_given,
            p.id,
            sol.allocated_hours,
            s.is_flexible,
            s.is_specific_move,
            s.is_office_boardroom_order,
            s.notice_given,
            s.is_approved_order,
            s.is_paid,
            s.end_date,
            s.is_website,
            pa.name,
            pav.name,
            p.location_name
        """

    def _orderby(self):
        return """
            pt.product_category, pt.prd_size, p.display_name1
        """

    def _query(self):
        return """
            (SELECT %s
            FROM %s
            WHERE sol.is_rental AND pa.name->>'en_US' = 'Location' AND p.active IS TRUE AND pt.product_category in ('2_office', '3_boardroom', '1_storage_unit', '4_parking') and pav.name->>'en_US'=p.location_name
            GROUP BY %s
            ORDER BY %s ASC)
        """ % (
            self._select(),
            self._from(),
            self._groupby(),
            self._orderby()
        )

    def init(self):
        # self._table = sale_rental_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    rental_status = fields.Selection(
        related='order_id.rental_status',
        string="Rental Order Status",
        copy=False, store=True, precompute=True)
    color = fields.Integer(readonly=True)