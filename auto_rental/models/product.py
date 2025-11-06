from odoo import fields, models, tools, api
from datetime import datetime,timedelta

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_category = fields.Selection([
        ('1_storage_unit', 'Warehouse or Storage Unit'),
        ('2_office', 'Office'),
        ('3_boardroom', 'Boardroom'),
        ('4_parking', 'Parking Bay'),
    ], string='Website Product Category')
    is_available = fields.Boolean(string="Is Available ?", compute='_compute_available', store=True)
    is_deposit = fields.Boolean(string="Is Deposit?", default=False)

    def _compute_available(self):
        if not self:
            all_prds = self.search([])
            for product in all_prds:
                product.is_available = False
                domain = [
                        ('product_template_id', '=', product.id),
                        ('order_id.state', 'in', ['send', 'sale', 'done','sent']),
                        # ('order_id.stage_category', '!=', 'closed'),
                        ('product_template_id.product_category', 'in', ['1_storage_unit', '4_parking']),
                    ]
                order_line_ids = self.env['sale.order.line'].sudo().search(domain)
                if order_line_ids :
                    previous_date = fields.Date.today() + timedelta(days=-60)
                    is_notice_given_m2m = order_line_ids.filtered(lambda x: x.order_id.is_notice_given and x.order_id.is_flexible)
                    specific_move_out = order_line_ids.filtered(lambda x: x.order_id.is_specific_move)
                    free_soon = []
                    if is_notice_given_m2m:
                        for rec in is_notice_given_m2m:
                            dt = datetime.strptime("1 " + rec.order_id.month+ " " + rec.order_id.year_id.name, "%d %m %Y").date()
                            d1 = previous_date - dt
                            if abs(d1.days) > 60 :
                                product.is_available = True

                    if specific_move_out:
                        for rec in specific_move_out:
                            if rec.return_date:
                                d1 = rec.return_date - timedelta(days=60)
                                if fields.Date.today() >= d1.date() :
                                    product.is_available = True
                else:
                    product.is_available = True

                if product.product_category in ['2_office', '3_boardroom']:
                    product.is_available = True

                if product.website_ribbon_id.id == 5: #maintance_product
                    product.is_available = False
        else:
            for product in self:
                product.is_available = False
                domain = [
                        ('product_template_id', '=', product.id),
                        ('order_id.state', 'in', ['send', 'sale', 'done','sent']),
                        # ('order_id.stage_category', '!=', 'closed'),
                        ('product_template_id.product_category', 'in', ['1_storage_unit', '4_parking']),
                    ]
                order_line_ids = self.env['sale.order.line'].sudo().search(domain)
                if order_line_ids :
                    previous_date = fields.Date.today() + timedelta(days=-60)
                    is_notice_given_m2m = order_line_ids.filtered(lambda x: x.order_id.is_notice_given and x.order_id.is_flexible)
                    specific_move_out = order_line_ids.filtered(lambda x: x.order_id.is_specific_move)
                    free_soon = []
                    if is_notice_given_m2m:
                        for rec in is_notice_given_m2m:
                            dt = datetime.strptime("1 " + rec.order_id.month+ " " + rec.order_id.year_id.name, "%d %m %Y").date()
                            d1 = previous_date - dt
                            if abs(d1.days) > 60 :
                                product.is_available = True

                    if specific_move_out:
                        for rec in specific_move_out:
                            if rec.return_date:
                                d1 = rec.return_date - timedelta(days=60)
                                if fields.Date.today() >= d1.date() :
                                    product.is_available = True
                else:
                    product.is_available = True

                if product.product_category in ['2_office', '3_boardroom']:
                    product.is_available = True

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        fields_to_hide = ['categ_id']
        res = super(ProductTemplate, self).fields_get(allfields=allfields, attributes=attributes)
        for field in fields_to_hide:
            if allfields and field in allfields:
                res[field]['searchable'] = False
                res[field]['sortable'] = False
        return res

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_available = fields.Boolean(string="Is Available ?", compute='_compute_available', store=True)

    def _compute_available(self):
        if not self:
            all_prds = self.search([])
            for product in all_prds:
                product.is_available = False
                domain = [
                        ('product_id', '=', product.id),
                        ('order_id.state', 'in', ['send', 'sale', 'done','sent']),
                        # ('order_id.stage_category', '!=', 'closed'),
                        ('product_id.product_category', 'in', ['1_storage_unit', '2_office', '3_boardroom', '4_parking']),
                    ]
                order_line_ids = self.env['sale.order.line'].sudo().search(domain)
                if order_line_ids :
                    previous_date = fields.Date.today() + timedelta(days=-60)
                    is_notice_given_m2m = order_line_ids.filtered(lambda x: x.order_id.is_notice_given and x.order_id.is_flexible)
                    specific_move_out = order_line_ids.filtered(lambda x: x.order_id.is_specific_move)
                    free_soon = []
                    if is_notice_given_m2m:
                        for rec in is_notice_given_m2m:
                            dt = datetime.strptime("1 " + rec.order_id.month+ " " + rec.order_id.year_id.name, "%d %m %Y").date()
                            d1 = previous_date - dt
                            if abs(d1.days) > 60 :
                                product.is_available = True

                    if specific_move_out:
                        for rec in specific_move_out:
                            if rec.return_date:
                                d1 = rec.return_date - timedelta(days=60)
                                if fields.Date.today() >= d1.date() :
                                    product.is_available = True
                else:
                    product.is_available = True

                if product.website_ribbon_id.id == 5: #maintance_product
                    product.is_available = False
        else:
            for product in self:
                product.is_available = False
                domain = [
                        ('product_id', '=', product.id),
                        ('order_id.state', 'in', ['send', 'sale', 'done','sent']),
                        # ('order_id.stage_category', '!=', 'closed'),
                        ('product_id.product_category', 'in', ['1_storage_unit', '2_office', '3_boardroom', '4_parking']),
                    ]
                order_line_ids = self.env['sale.order.line'].sudo().search(domain)
                if order_line_ids :
                    previous_date = fields.Date.today() + timedelta(days=-60)
                    is_notice_given_m2m = order_line_ids.filtered(lambda x: x.order_id.is_notice_given and x.order_id.is_flexible)
                    specific_move_out = order_line_ids.filtered(lambda x: x.order_id.is_specific_move)
                    free_soon = []
                    if is_notice_given_m2m:
                        for rec in is_notice_given_m2m:
                            dt = datetime.strptime("1 " + rec.order_id.month+ " " + rec.order_id.year_id.name, "%d %m %Y").date()
                            d1 = previous_date - dt
                            if abs(d1.days) > 60 :
                                product.is_available = True

                    if specific_move_out:
                        for rec in specific_move_out:
                            if rec.return_date:
                                d1 = rec.return_date - timedelta(days=60)
                                if fields.Date.today() >= d1.date() :
                                    product.is_available = True
                else:
                    product.is_available = True