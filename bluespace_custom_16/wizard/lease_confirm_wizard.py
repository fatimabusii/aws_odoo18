# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class LeaseCOnfirmWizard(models.TransientModel):
    _name = 'lease.confirm.wizard'
    _description = 'Lease Confirm Wizard'

    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        print("ssssssssssssss:::::::::::::::::ccccccccccc:::::::::",self.env.context)
        ctx = self.env.context
        if ctx.get('is_office_boardroom_order'):
            defaults['is_office_boardroom_order'] = ctx.get('is_office_boardroom_order')
        return defaults

    is_office_boardroom_order = fields.Boolean(string="Is Office Boardroom Order")

    unit_used_for_text = fields.Selection([
        ('self_unit', 'Self storage'),
        ('e_eommerce', 'e-Commerce'),
        ('tradesman_store', 'Tradesman Store'),
        ('offices', 'Offices'),
        ('dance_studio', 'Dance Studio'),
        ('art_studio', 'Art Studio'),
        ('other', 'Other'),
    ], string="Unit Use")
    other_info_unit = fields.Char(string="Other Unit info")
    other_info_description = fields.Text(string="Other Unit Description")

    what_content_text = fields.Selection([
        ('household_goods', 'Household Goods'),
        ('vehicle', 'Vehicle'),
        ('documents', 'Documents'),
        ('other', 'Other'),
    ], string="Contents in Unit")
    other_info_what = fields.Char(string="Other Content Info")
    other_description = fields.Text(string="Other Content Description")

    what_activity_occur = fields.Selection([
        ('storage', 'Storage'),
        ('admin', 'Admin'),
        ('picking', 'Picking'),
        ('packing', 'Packing'),
        ('other', 'Other'),
    ], string="Activity in Unit")
    other_info_activity = fields.Char(string="Other Activity Info")
    activity_description = fields.Text(string="Other Activity Description")

    lease_prepaid_water = fields.Boolean()
    lease_no_hazardous = fields.Boolean()
    lease_calendar_month = fields.Boolean()
    lease_refuse_access = fields.Boolean()
    lease_sell_goods = fields.Boolean()
    lease_lessors_hypotec = fields.Boolean()
    lease_not_insure = fields.Boolean()
    lease_nuisance = fields.Boolean()
    lease_credit_check = fields.Boolean()
    lease_accept_all = fields.Boolean()

    lease_ofc_boardroom = fields.Boolean()

    #all_lease_agreement = fields.Boolean(string="I hereby confirm my acceptance of the lease agreement, and I authorise a credit check")

    # @api.onchange('lease_accept_all')
    # def _onchange_lease_accept_all(self):
    #     print("lease_accept_all----------------------",self.lease_accept_all)
    #     if self.lease_accept_all:
    #         self.write()

    def action_submit(self):
        print("action_submit@@@@@@@@@@@@@@@@@:::::",self.env.context)
        if not self.is_office_boardroom_order:
            if not self.lease_accept_all:
                raise UserError('Please read and accept all lease terms and conditions!')
            elif not self.lease_accept_all and (not self.lease_prepaid_water or not self.lease_no_hazardous or not self.lease_calendar_month or \
                not self.lease_refuse_access or not self.lease_sell_goods or not self.lease_lessors_hypotec or not self.lease_not_insure \
                or not self.lease_nuisance or not self.lease_credit_check) :
                raise UserError('Please read and accept all lease terms and conditions!')
            else:
                print("###########")
                ctx = self.env.context
                if ctx.get('active_id'):
                    sale_id = self.env['sale.order'].sudo().browse(ctx.get('active_id'))
                    print("sssssssssssss:::::sale_id:::::",sale_id)
                    if sale_id:
                        vals = {
                            'unit_used_for_text': self.unit_used_for_text,
                            'other_info_unit': self.other_info_unit,
                            'other_info_description': self.other_info_description,
                            'what_content_text': self.what_content_text,
                            'other_info_what': self.other_info_what,
                            'other_description': self.other_description,
                            'what_activity_occur': self.what_activity_occur,
                            'other_info_activity': self.other_info_activity,
                            'activity_description': self.activity_description
                        }
                        sale_id.write(vals)
                        sale_id.all_lease_agreement = True
                        sale_id.lease_confirm = True
                        sale_id.action_confirm()

        if self.is_office_boardroom_order:
            if not self.lease_ofc_boardroom:
                raise UserError('Please read and accept all lease terms and conditions!')
            else:
                ctx = self.env.context
                if ctx.get('active_id'):
                    sale_id = self.env['sale.order'].sudo().browse(ctx.get('active_id'))
                    if sale_id:
                        sale_id.all_lease_agreement = True
                        sale_id.lease_confirm = True
                        sale_id.action_confirm()

