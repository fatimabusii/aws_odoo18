# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo import api, fields, models, _
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.form import WebsiteForm
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.tools.json import scriptsafe as json_scriptsafe
import json
import io
import base64
from odoo.modules.module import get_resource_path

class WebsiteSaleERP(WebsiteSale):

    @http.route('/shop/order/thanks', type='http', auth='public', website=True, sitemap=False)
    def shop_order_thanks(self, **post):
        order = request.website.sale_get_order()
        if order:
            values = {'order_id' : order}
            order.is_approved_order = True
            # self.send_order_approval_mail_for_storage(order)
        return request.render("website_extra_info.order_thanks_extra_info", values)

    # def send_order_approval_mail_for_storage(self, order):
    #     template_id = request.env.ref('bluespace_custom_16.salesperson_order_approval_mail', raise_if_not_found=False)
    #     salesperson_email = request.env['ir.config_parameter'].sudo().get_param('auto_rental.salesperson_email')
    #     email_from = request.env.company.email
    #     if template_id:
    #         template_id.sudo().write({
    #             'email_from': "{} - {}".format(request.env.company.name, email_from),
    #             'email_to': salesperson_email or '',
    #             'body_html': """
    #                 <p>Hello</p>
    #                 <p>{} have booking units for other.</p>
    #                 <p>Please check and approve {} in less than 16 business hours.</p>""".format(order.partner_id.name, order.name)
    #         })
    #         template_id.sudo().send_mail(order.id, force_send=True)
    #     return True

    @http.route(['/attachment/download/aggrement', ], type='http', auth='public')
    def download_attachment_aggrement(self):
        attachment = request.env['ir.attachment'].sudo().search(
            [('name', '=', 'Blue Spaces Rental Agreeement_v1.pdf')])
        if attachment:
            attachment = attachment[0]
        else:
            return request.redirect('/shop')

        if attachment["type"] == "url":
            if attachment["url"]:
                return request.redirect(attachment["url"])
            else:
                return request.not_found()
        elif attachment["datas"]:
            data = io.BytesIO(base64.standard_b64decode(attachment["datas"]))
            return http.send_file(data, filename=attachment['name'],
                                  as_attachment=True)
        else:
            return request.not_found()

class WebsiteFormerpweb(WebsiteForm):

    @http.route('/website/form/shop.sale.order', type='http', auth="public", methods=['POST'], website=True)
    def website_form_saleorder(self, **kwargs):
        is_thanks_page = False
        extra_info = {}
        if 'unit_used_for_text' in kwargs and kwargs.get('unit_used_for_text') or ('unit_used_desc' in kwargs and kwargs.get('unit_used_desc')):
            if kwargs.get('unit_used_for_text'):
                is_search_keyword = request.env['ir.config_parameter'].sudo().get_param("website_extra_info.is_search_keyword")
                unit_used_for_keyaword = request.env['ir.config_parameter'].sudo().get_param("website_extra_info.unit_used_for_keyaword")
                if is_search_keyword and unit_used_for_keyaword and kwargs.get('unit_used_for_text'):
                    if kwargs.get('unit_used_for_text'):
                        str2 = kwargs.get('unit_used_for_text').split()
                        if str2[-1] and "," in str2[-1]:
                            str2[-1] = str2[-1].rstrip(',')
                        str2 = [s.lower() for s in str2]
                        if any(x.lower() in str2 for x in unit_used_for_keyaword.split(',')):
                            is_thanks_page = True
                if kwargs.get('unit_used_desc'):
                    str1 = kwargs.get('unit_used_desc').split()
                    if str1[-1] and "," in str1[-1]:
                        str1[-1] = str1[-1].rstrip(',')
                    str1 = [s.lower() for s in str1]
                    if any(x.lower() in str1 for x in unit_used_for_keyaword.split(',')):
                        is_thanks_page = True
        if ('what_content_text' in kwargs and kwargs.get('what_content_text')) or ('what_desc' in kwargs and kwargs.get('what_desc')):
            is_what_type_of_contents = request.env['ir.config_parameter'].sudo().get_param("website_extra_info.is_what_type_of_contents")
            contents_for_keyaword = request.env['ir.config_parameter'].sudo().get_param("website_extra_info.contents_for_keyaword")
            if is_what_type_of_contents and contents_for_keyaword and kwargs.get('what_content_text'):
                if kwargs.get('what_content_text'):
                    str2 = kwargs.get('what_content_text').split()
                    if str2[-1] and "," in str2[-1]:
                        str2[-1] = str2[-1].rstrip(',')
                    str2 = [s.lower() for s in str2]
                    if any(x.lower() in str2 for x in contents_for_keyaword.split(',')):
                        is_thanks_page = True
                if kwargs.get('what_desc'):
                    str1 = kwargs.get('what_desc').split()
                    if str1[-1] and "," in str1[-1]:
                        str1[-1] = str1[-1].rstrip(',')
                    str1 = [s.lower() for s in str1]
                    if any(x.lower() in str1 for x in contents_for_keyaword.split(',')):
                        is_thanks_page = True
        if 'what_activity_occur' in kwargs and kwargs.get('what_activity_occur') or ('what_desc' in kwargs and kwargs.get('what_desc')):
            is_what_type_of_activity = request.env['ir.config_parameter'].sudo().get_param("website_extra_info.is_what_type_of_activity")
            activity_for_keyaword = request.env['ir.config_parameter'].sudo().get_param("website_extra_info.activity_for_keyaword")
            if is_what_type_of_activity and activity_for_keyaword and kwargs.get('what_activity_occur'):
                if kwargs.get('what_activity_occur'):
                    str2 = kwargs.get('what_activity_occur').split()
                    if str2[-1] and "," in str2[-1]:
                        str2[-1] = str2[-1].rstrip(',')
                    str2 = [s.lower() for s in str2]
                    if any(x.lower() in str2 for x in activity_for_keyaword.split(',')):
                        is_thanks_page = True
                if kwargs.get('what_desc'):
                    str1 = kwargs.get('what_desc').split()
                    if str1[-1] and "," in str1[-1]:
                        str1[-1] = str1[-1].rstrip(',')
                    str1 = [s.lower() for s in str1]
                    if any(x.lower() in str1 for x in activity_for_keyaword.split(',')):
                        is_thanks_page = True

        model_record = request.env.ref('sale.model_sale_order')
        try:
            data = self.extract_data(model_record, kwargs)
        except ValidationError as e:
            return json.dumps({'error_fields': e.args[0]})

        order = request.website.sale_get_order()
        {'unit_used_for': 'other', 'unit_used_for_text': 'hello', 'what_content': 'other', 'what_content_text': 'hhhh', 'what_activity': 'other', 'what_activity_occur': 'ggg'}

        if order:
            if 'unit_used_for' in kwargs and kwargs.get('unit_used_for') or 'unit_used_for_text' in kwargs and kwargs.get('unit_used_for_text') or 'unit_used_desc' in kwargs and kwargs.get('unit_used_desc'):
                order.write({'unit_used_for_text' : kwargs.get('unit_used_for', ' '), 'other_info_unit' : kwargs.get('unit_used_for_text', ' '), 'other_info_description' : kwargs.get('unit_used_desc')})
            if 'what_content' in kwargs and kwargs.get('what_content') or 'what_content_text' in kwargs and kwargs.get('what_content_text') or 'what_desc' in kwargs and kwargs.get('what_desc'):
                order.write({'what_content_text' : kwargs.get('what_content', ' '),
                    'other_info_what' : kwargs.get('what_content_text', ' '), 'other_description' : kwargs.get('what_desc')})
            if 'what_activity' in kwargs and kwargs.get('what_activity') or 'what_activity_occur' in kwargs and kwargs.get('what_activity_occur') or 'activity_desc' in kwargs and kwargs.get('activity_desc'):
                order.write({'what_activity_occur' : kwargs.get('what_activity', ' '),
                    'other_info_activity' : kwargs.get('what_activity_occur', ' '), 'activity_description' : kwargs.get('activity_desc')})
            if kwargs.get('all') and 'all' in kwargs:
                agreement_file_path = get_resource_path('website_extra_info', 'static/src/description', 'Blue Spaces Rental Agreeement.pdf')
                agreement_file = open(agreement_file_path, 'rb').read()

                agreement_attachment = request.env['ir.attachment'].sudo().create({
                    'name': 'Blue Spaces Rental Agreeement',
                    'datas': base64.encodebytes(agreement_file),
                    'res_id': order.id,
                    'res_model': 'sale.order',
                })
                order.write({'all_lease_agreement': True})

        if data['record']:
            order.write(data['record'])

        if data['custom']:
            values = {
                'body': nl2br(data['custom']),
                'model': 'sale.order',
                'message_type': 'comment',
                'res_id': order.id,
            }
            request.env['mail.message'].with_user(SUPERUSER_ID).create(values)

        if data['attachments']:
            self.insert_attachment(model_record, order.id, data['attachments'])

        return json.dumps({'id': order.id, 'is_thanks_page' : is_thanks_page})