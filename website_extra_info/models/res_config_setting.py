# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_search_keyword = fields.Boolean(string="Storage Usage")
    is_what_type_of_contents = fields.Boolean(string="Storage Content")
    is_what_type_of_activity = fields.Boolean(string="Storage Activity")
    unit_used_for_keyaword = fields.Text(string='Unit Keyword')
    contents_for_keyaword = fields.Text(string='Contents Keyword')
    activity_for_keyaword = fields.Text(string='Activity Keyword')

    def set_values(self):
        res = super(ResConfigSettings,self).set_values()
        set_value = self.env['ir.config_parameter'].sudo()
        set_value.set_param('website_extra_info.is_search_keyword',self.is_search_keyword)
        set_value.set_param('website_extra_info.is_what_type_of_contents',self.is_what_type_of_contents)
        set_value.set_param('website_extra_info.is_what_type_of_activity',self.is_what_type_of_activity)
        set_value.set_param('website_extra_info.unit_used_for_keyaword', self.unit_used_for_keyaword)
        set_value.set_param('website_extra_info.contents_for_keyaword', self.contents_for_keyaword)
        set_value.set_param('website_extra_info.activity_for_keyaword', self.activity_for_keyaword)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings,self).get_values()
        set_value = self.env['ir.config_parameter'].sudo()
        is_search_keyword = set_value.get_param('website_extra_info.is_search_keyword')
        is_what_type_of_contents = set_value.get_param('website_extra_info.is_what_type_of_contents')
        is_what_type_of_activity = set_value.get_param('website_extra_info.is_what_type_of_activity')
        unit_used_for_keyaword = set_value.get_param('website_extra_info.unit_used_for_keyaword')
        contents_for_keyaword = set_value.get_param('website_extra_info.contents_for_keyaword')
        activity_for_keyaword = set_value.get_param('website_extra_info.activity_for_keyaword')
        res.update(
            is_search_keyword = is_search_keyword,
            is_what_type_of_contents = is_what_type_of_contents,
            is_what_type_of_activity = is_what_type_of_activity,
            unit_used_for_keyaword = unit_used_for_keyaword,
            contents_for_keyaword = contents_for_keyaword,
            activity_for_keyaword = activity_for_keyaword,
        )
        return res
