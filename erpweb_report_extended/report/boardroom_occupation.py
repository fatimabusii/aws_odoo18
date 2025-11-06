# -*- coding: utf-8 -*-
from odoo import fields, models, tools, api
from datetime import datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta
# from datequarter import DateQuarter
from datetime import date
from calendar import monthrange
import holidays

class BoardroomOccupation(models.Model):
    _name = "erpweb.boardroom.occupation.report"
    _description = "Boardroom Occupation Report"
    _auto = False

    date = fields.Date('Date', readonly=True)
    order_id = fields.Many2one('sale.order', 'Order #', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', readonly=True)
    percent_occupation = fields.Float('Percent Occupation (%)', store=True)
    product_category = fields.Selection([
        ('3_boardroom', 'First Floor Boardroom'),
    ], string='Product Category')
    name = fields.Char('Order Reference', readonly=True)

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        fields_to_hide = ['product_category', 'percent_occupation', 'order_id', 'name', 'product_id', 'product_tmpl_id']
        res = super(BoardroomOccupation, self).fields_get(allfields=allfields, attributes=attributes)
        for field in fields_to_hide:
            res[field]['sortable'] = False
            res[field]['searchable'] = False
        return res

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        result = super(BoardroomOccupation, self).read_group(
            domain, fields, groupby, offset=offset,
            limit=limit, orderby=orderby, lazy=lazy)
        products = self.env['product.product'].search([('product_category', '=', '3_boardroom')])
        ctx = self.env.context
        sa_holidays = holidays.SouthAfrica()
        for r in result :
            if r.get('date:month', False):
                dt = datetime.strptime("1 "+r['date:month'], "%d %B %Y").date()
                last_dt = dt.replace(day = calendar.monthrange(dt.year, dt.month)[1])
                month_days = calendar.monthrange(dt.year, dt.month)[1]
                holiday_count = len(sa_holidays[dt: last_dt])
                weekend_count = 0
                for i in range(month_days):
                    day = dt + timedelta(days=i)
                    if(day.weekday()>4):
                        weekend_count = weekend_count + 1
                sale_order_lines = self.env['sale.order.line'].search([('product_id', 'in', products.ids), ('state', 'in', ['sale', 'done', 'sent']), ('order_id.start_date', '>=', dt)])
                total_sol = sale_order_lines.filtered(lambda s: s.start_date.month == dt.month and s.product_id.product_category == '3_boardroom')
                total_sol_hours = sum(total_sol.mapped('allocated_hours'))
                total_days = month_days - holiday_count - weekend_count
                per = ((total_sol_hours / (total_days * 9) * len(products)))
                r.update({'percent_occupation':per})

            if r.get('date:week', False):
                wk = r['date:week']
                dt_week = wk.split(" ")
                start_date1 = datetime(int(dt_week[1]), 1, 1) + relativedelta(weeks=+int(dt_week[0][1:]))
                end_date1 = start_date1 + timedelta(days = 6)
                sale_order_lines = self.env['sale.order.line'].search([('product_id', 'in', products.ids), ('state', 'in', ['sale', 'done', 'sent']), ('order_id.start_date', '>=', start_date1), ('order_id.start_date', '<=', end_date1)])
                total_sol = sale_order_lines.filtered(lambda s: s.product_id.product_category in ('2_office', '3_boardroom'))
                total_sol_hours = sum(total_sol.mapped('allocated_hours'))
                holiday_count = len(sa_holidays[start_date1: end_date1])
                weekend_count = 0
                week_days = end_date1 - start_date1
                for i in range(week_days.days):
                    day = start_date1 + timedelta(days=i)
                    if(day.weekday()>4):
                        weekend_count = weekend_count + 1
                total_days = week_days.days - holiday_count - weekend_count
                per = (total_sol_hours / ((total_days * 9) * len(products)))
                r.update({'percent_occupation':per})

            if r.get('date:day', False):
                start_date1 = r['date:day'] #datetime(int(dt_week[1]), 1, 1) + relativedelta(weeks=+int(dt_week[0][1:]))
                dd = datetime.strptime(start_date1, "%d %b %Y").date()
                total_sol = self.env['sale.order.line'].search([('product_id', 'in', products.ids),('state', 'in', ['sale', 'done', 'sent']), ('start_date', '=', dd)])
                total_sol_hours = sum(total_sol.mapped('allocated_hours'))

                per = (total_sol_hours / ((1 * 9) * len(products)))
                r.update({'percent_occupation':per})

            if r.get('date:year', False):
                year1 = r['date:year'] #datetime(int(dt_week[1]), 1, 1) + relativedelta(weeks=+int(dt_week[0][1:]))
                firstday = datetime(int(year1), 1,1).date()
                lastday = datetime(int(year1), 12,31).date()
                year_days = (lastday - firstday).days
                total_sol = self.env['sale.order.line'].search([('product_id', 'in', products.ids),('state', 'in', ['sale', 'done', 'sent']), ('start_date', '>=', firstday), ('start_date', '<=', lastday)])
                total_sol_hours = sum(total_sol.mapped('allocated_hours'))
                holiday_count = len(sa_holidays[firstday: lastday])
                weekend_count = 0
                for i in range(year_days):
                    day = firstday + timedelta(days=i)
                    if(day.weekday()>4):
                        weekend_count = weekend_count + 1
                total_days = year_days - holiday_count - weekend_count

                per = (total_sol_hours / ((total_days * 9) * len(products)))
                r.update({'percent_occupation':per})

            if r.get('date:quarter', False):
                qt = r['date:quarter'] #datetime(int(dt_week[1]), 1, 1) + relativedelta(weeks=+int(dt_week[0][1:]))
                qtt = int(qt[1:3])
                yr = int(qt[3:])
                # firstday = DateQuarter(yr, qtt).start_date()
                # lastday = DateQuarter(yr, qtt).end_date()
                firstday, lastday = self.quarter_range(yr, qtt)
                total_sol = self.env['sale.order.line'].search([('product_id', 'in', products.ids),('state', 'in', ['sale', 'done', 'sent']), ('start_date', '>=', firstday), ('start_date', '<=', lastday)])
                total_sol_hours = sum(total_sol.mapped('allocated_hours'))
                holiday_count = len(sa_holidays[firstday: lastday])
                weekend_count = 0
                quater_days = (lastday - firstday).days
                for i in range(quater_days):
                    day = firstday + timedelta(days=i)
                    if(day.weekday()>4):
                        weekend_count = weekend_count + 1
                total_days = quater_days - holiday_count - weekend_count


                per = (total_sol_hours / ((total_days * 9) * len(products)))
                r.update({'percent_occupation':per})

            if r.get('product_category', False):
                products = self.env['product.product'].search([('product_category', '=', r['product_category'])])
                total_sol = self.env['sale.order.line'].search([('product_id', 'in', products.ids),('state', 'in', ['sale', 'done', 'sent'])])
                total_sol_hours = sum(total_sol.mapped('allocated_hours'))
                start_date = (total_sol.mapped('start_date'))
                total_days = 1
                if start_date:
                    holiday_count = len(sa_holidays[min(start_date): max(start_date)])
                    weekend_count = 0
                    count_days = (max(start_date) - min(start_date)).days
                    for i in range(count_days):
                        day = min(start_date) + timedelta(days=i)
                        if(day.weekday()>4):
                            weekend_count = weekend_count + 1
                    total_days = count_days - holiday_count - weekend_count
                per = (total_sol_hours / ((total_days * 9) * len(products)))
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


    def _select(self):
        return """
            sol.id,
            sol.order_id,
            generate_series(s.start_date::date, s.rental_return_date::date, '1 month'::interval)::date date,
            s.name as name,
            pt.product_category AS product_category,
            ((CASE
                WHEN (sol.product_id = p.id) AND s.state in ('sale', 'done', 'sent') THEN count(sol.id)
            END)/ sum(p.id)
            ) * 100 as percent_occupation
        """
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
            s.date_order,
            s.start_date,
            s.rental_return_date,
            pt.product_category,
            s.state,
            p.id
        """

    def _query(self):
        return """
            (SELECT %s
            FROM %s
            WHERE sol.is_rental AND pt.product_category = '3_boardroom' AND p.active IS TRUE AND s.state in ('sale', 'done', 'sent')
            GROUP BY %s)
        """ % (
            self._select(),
            self._from(),
            self._groupby()
        )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
