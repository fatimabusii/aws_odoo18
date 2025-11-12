# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api
from datetime import datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta
# from datequarter import DateQuarter
from datetime import date
from calendar import monthrange

class FinancialOccupation(models.Model):
    _name = "erpweb.financial.occupation.report"
    _description = "Financial Occupation Report"
    _auto = False

    date = fields.Date('Date', readonly=True)
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
    price = fields.Float('Daily Amount', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', readonly=True)
    move_in_date = fields.Date(string="Move In Date", readonly=True)
    move_out_date = fields.Date(string="Move Out Date", readonly=True)
    percent_occupation = fields.Float('Financial Occupation (%)', store=True)
    product_category = fields.Selection([
        ('1_storage_unit', 'Warehouse or Storage Unit'),
        ('4_parking', 'Parking Bay'),
    ], string='Product Category')
    name = fields.Char('Order Reference', readonly=True)

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        fields_to_hide = ['move_in_date', 'move_out_date', 'product_id', 'product_tmpl_id', 'product_uom',
        'company_id', 'quantity', 'currency_id', 'name', 'state', 'user_id', 'qty_returned', 'qty_delivered', 
        'partner_id', 'order_id', 'price', 'id', 'percent_occupation']
        res = super(FinancialOccupation, self).fields_get(allfields=allfields, attributes=attributes)
        for field in fields_to_hide:
            res[field]['sortable'] = False
            res[field]['searchable'] = False
        return res

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        result = super(FinancialOccupation, self).read_group(
            domain, fields, groupby, offset=offset,
            limit=limit, orderby=orderby, lazy=lazy)
        products = self.env['product.product'].search([('product_category', 'in', ('1_storage_unit', '4_parking'))])
        total_product_price = sum(products.filtered(lambda l: l.product_category in ('1_storage_unit', '4_parking')).mapped('lst_price'))
        ctx = self.env.context
        for r in result :
            if r.get('date:month', False):
                dt = datetime.strptime("1 "+r['date:month'], "%d %B %Y").date()
                last_dt = dt.replace(day = calendar.monthrange(dt.year, dt.month)[1])
                sale_order_lines = self.env['sale.order.line'].search([('product_id', 'in', products.ids),('state', 'in', ['done', 'sale']), ('order_id.is_paid', '=', True), ('order_id.start_date', '>=', dt)])
                total_sol = sale_order_lines.filtered(lambda s: s.start_date.month == dt.month)
                total_sol_unit_price = sum(total_sol.mapped('price_unit'))

                for d in domain:
                    if 'product_category' in d:
                        products = self.env['product.product'].search([d])
                        total_sol = sale_order_lines.filtered(lambda s: s.start_date.month == dt.month and s.product_id.id in products.ids)
                        total_product_price = sum(products.mapped('lst_price'))
                        total_sol_unit_price = sum(total_sol.mapped('price_unit'))
                per = (total_sol_unit_price / total_product_price) * 100
                r.update({'percent_occupation':per})

            if r.get('date:week', False):
                wk = r['date:week']
                dt_week = wk.split(" ")
                start_date1 = datetime(int(dt_week[1]), 1, 1) + relativedelta(weeks=+int(dt_week[0][1:]))
                end_date1 = start_date1 + timedelta(days = 6)
                sale_order_lines = self.env['sale.order.line'].search([('product_id', 'in', products.ids),('state', 'in', ['sale', 'done']), ('order_id.is_paid', '=', True), ('order_id.start_date', '>=', start_date1), ('order_id.start_date', '<=', end_date1)])
                total_product_price = sum(products.mapped('lst_price'))
                total_sol_unit_price = sum(sale_order_lines.mapped('price_unit'))

                per = (total_sol_unit_price / total_product_price) * 100
                r.update({'percent_occupation':per})

            if r.get('date:day', False):
                start_date1 = r['date:day'] #datetime(int(dt_week[1]), 1, 1) + relativedelta(weeks=+int(dt_week[0][1:]))
                dd = datetime.strptime(start_date1, "%d %b %Y").date()
                sale_order_lines = self.env['sale.order.line'].search([('product_id', 'in', products.ids),('state', 'in', ['sale', 'done']), ('order_id.is_paid', '=', True), ('order_id.start_date', '=', dd)])
                total_product_price = sum(products.mapped('lst_price'))
                total_sol_unit_price = sum(sale_order_lines.mapped('price_unit'))

                per = (total_sol_unit_price / total_product_price) * 100
                r.update({'percent_occupation':per})

            if r.get('date:year', False):
                year1 = r['date:year'] #datetime(int(dt_week[1]), 1, 1) + relativedelta(weeks=+int(dt_week[0][1:]))
                firstday = datetime(int(year1), 1,1).date()
                lastday = datetime(int(year1), 12,31).date()
                sale_order_lines = self.env['sale.order.line'].search([('product_id', 'in', products.ids),('state', 'in', ['sale', 'done']), ('order_id.is_paid', '=', True), ('order_id.start_date', '>=', firstday), ('order_id.start_date', '<=', lastday)])
                total_product_price = sum(products.mapped('lst_price'))
                total_sol_unit_price = sum(sale_order_lines.mapped('price_unit'))
                per = (total_sol_unit_price / total_product_price) * 100
                r.update({'percent_occupation':per})

            if r.get('date:quarter', False):
                qt = r['date:quarter'] #datetime(int(dt_week[1]), 1, 1) + relativedelta(weeks=+int(dt_week[0][1:]))
                qtt = int(qt[1:3])
                yr = int(qt[3:])
                # firstday = DateQuarter(yr, qtt).start_date()
                # lastday = DateQuarter(yr, qtt).end_date()
                firstday, lastday = self.quarter_range(yr, qtt)
                sale_order_lines = self.env['sale.order.line'].search([('product_id', 'in', products.ids),('state', 'in', ['sale', 'done']), ('order_id.is_paid', '=', True), ('order_id.start_date', '>=', firstday), ('order_id.start_date', '<=', lastday)])
                total_product_price = sum(products.mapped('lst_price'))
                total_sol_unit_price = sum(sale_order_lines.mapped('price_unit'))
                per = (total_sol_unit_price / total_product_price) * 100
                r.update({'percent_occupation':per})

            if r.get('product_category', False):
                products = self.env['product.product'].search([('product_category', '=', r['product_category'])])
                sale_order_lines = self.env['sale.order.line'].search([('product_id', 'in', products.ids),('state', 'in', ['sale', 'done']), ('order_id.is_paid', '=', True)])
                total_sol = sale_order_lines.filtered(lambda s: s.product_id.id in products.ids)
                total_product_price = sum(products.mapped('lst_price'))
                total_sol_unit_price = sum(total_sol.mapped('price_unit'))
                per = (total_sol_unit_price / total_product_price) * 100
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
            sol.price_subtotal / (date_part('month',s.rental_return_date - s.start_date) + 1)
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
            generate_series(s.start_date::date, s.rental_return_date::date, '1 month'::interval)::date date,
            %s AS price,
            sol.company_id,
            sol.state,
            sol.currency_id,
            s.start_date AS move_in_date,
            s.rental_return_date AS move_out_date,
            pt.product_category AS product_category,
            ((CASE
                WHEN (sol.product_id = p.id) AND s.state in ('sale', 'done') THEN sum(sol.price_unit)
            END)/ sum(pt.list_price)
            ) * 100 as percent_occupation
        """% (self._quantity(), self._price())

    def _from(self):
        return """
            sale_order_line AS sol
            join sale_order s on (sol.order_id=s.id)
            join product_product AS p on p.id=sol.product_id
            join product_template AS pt on p.product_tmpl_id=pt.id
            join uom_uom AS u on u.id=sol.product_uom
            join uom_uom AS u2 on u2.id=pt.uom_id
        """

    def _groupby(self):
        return """
            sol.id,
            s.name,
            s.start_date,
            s.rental_return_date,
            u.factor,
            u2.factor,
            p.product_tmpl_id,
            pt.product_category,
            s.subscription_state,
            s.state,
            s.notice_given,
            p.id
        """

    def _query(self):
        return """
            (SELECT %s
            FROM %s
            WHERE sol.is_rental AND pt.product_category in ('1_storage_unit', '4_parking') AND p.active IS TRUE AND s.is_paid IS TRUE
            GROUP BY %s)
        """ % (
            self._select(),
            self._from(),
            self._groupby()
        )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
