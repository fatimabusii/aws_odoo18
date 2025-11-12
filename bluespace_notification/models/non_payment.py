from odoo import api, fields, models, _
import datetime
import calendar
from dateutil import relativedelta
from odoo.http import request
from datetime import timedelta,datetime
import logging
_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    manager_email = fields.Char(string="Non Payment Manager Email")

    def set_values(self):
        res = super(ResConfigSettings,self).set_values()
        set_value = self.env['ir.config_parameter'].sudo()
        set_value.set_param('bluespace_notification.manager_email',self.manager_email)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings,self).get_values()
        set_value = self.env['ir.config_parameter'].sudo()
        manager_email = set_value.get_param('bluespace_notification.manager_email')
        res.update(manager_email=manager_email)
        return res

class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_test_custom_date(self):
        notification_test_date = self.env['test.date'].search([], limit=1)
        if notification_test_date:
            return notification_test_date.test_date
        return fields.Date.today()

    def get_manager_email(self):
        manager_email = self.env['ir.config_parameter'].sudo().get_param('bluespace_notification.manager_email')
        return manager_email

    def get_non_payment_list(self):
        today = fields.Date.today()
        test_date = self.get_test_custom_date()
        non_payment_list = []
        if today.day in [8] or test_date.day in [8]:

            domain = [('state', '=', 'posted'), 
                ('payment_state', 'in', ('not_paid', 'partial')), 
                ('move_type', 'in', self.get_sale_types()), 
                ('company_id', '=', self.env.company.id)]
            
            move_ids = self.sudo().search(domain)
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_date = now.strftime("%d/%m/%Y")

            for move in move_ids:
                non_payment_dict = {}

                order_id = move.line_ids.sale_line_ids.order_id
                if order_id:
                    product_id = order_id.mapped('order_line').mapped('product_id').filtered(lambda x: x.product_category in ['2_office', '3_boardroom', '1_storage_unit', '4_parking'])
                    product_type = product_id.display_name
                    order_line_id = order_id.order_line.filtered(lambda x:x.product_id.id == product_id.id)
                    _logger.info("order_line_id>>>>>>>>>>>>>>>>>>> %s %s",move,order_id)
                    move_in_date = order_line_id.start_date.strftime("%d/%m/%Y")
                    
                    move_out_date = ''
                    if order_id.is_flexible :
                        move_out_date = 'Month to Month'
                    elif order_id.is_specific_move :
                        move_out_date = order_id.end_date.strftime("%d/%m/%Y")

                    non_payment_dict.update({
                        'odoo_at': current_time + "-" + current_date,
                        'cust_name': move.partner_id.name,
                        'phone_email': str(move.partner_id.mobile or move.partner_id.phone) + "-" + move.partner_id.email,
                        'space_type': product_type,
                        'move_in_date': move_in_date,
                        'move_out_date': move_out_date,
                        'amt_due': round(move.amount_residual,2)
                        })
                    non_payment_list.append(non_payment_dict)

        return non_payment_list

    @api.model
    def _cron_non_payment_notification(self):
        '''today = fields.Date.today()
        test_date = self.get_test_custom_date()
        if today.day in [8] or test_date.day in [8]:

            domain = [('state', '=', 'posted'), 
                ('payment_state', 'in', ('not_paid', 'partial')), 
                ('move_type', 'in', self.get_sale_types()), 
                ('company_id', '=', self.env.company.id)]
            
            move_ids = self.sudo().search(domain)
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_date = now.strftime("%d/%m/%Y")

            for move in move_ids:
                order_id = move.line_ids.sale_line_ids.order_id
                if order_id:
                    product_id = order_id.mapped('order_line').mapped('product_id').filtered(lambda x: x.product_category in ['2_office', '3_boardroom', '1_storage_unit', '4_parking'])
                    product_type = product_id.display_name
                    order_line_id = order_id.order_line.filtered(lambda x:x.product_id.id == product_id.id)
                    _logger.info("order_line_id>>>>>>>>>>>>>>>>>>> %s %s",move,order_id)
                    move_in_date = order_line_id.start_date.strftime("%d/%m/%Y")
                    
                    move_out_date = ''
                    if order_id.is_flexible :
                        move_out_date = 'Month to Month'
                    elif order_id.is_specific_move :
                        move_out_date = order_id.end_date.strftime("%d/%m/%Y")'''
    
        template_id = self.env.ref('bluespace_notification.email_template_non_payment_manager', raise_if_not_found=False)
        manager_email = self.env['ir.config_parameter'].sudo().get_param('bluespace_notification.manager_email')
        email_from = self.env.company.email
        today = fields.Date.today()
        test_date = self.get_test_custom_date()

        if template_id and (today.day in [8] or test_date.day in [8]):
            '''template_id.sudo().write({
                'email_from': "info@bluespaces.co.za",
                'email_to': manager_email or '',
                'body_html': """
                    <div style="font-family: Calibri;">
                        <p>Dear Blue Spaces Manager</p>
                        <p>The following Customer has not paid his account and now needs to be locked out today.</p><br/>
                        <p><strong>Sent by Odoo at: </strong> {} on {} <p>
                        <p><strong>Customer Name: </strong> {} <p>
                        <p><strong>Customer Contact Number and email: </strong> {} - {}<p>
                        <p><strong>Rental Space Type and number: </strong> {} <p>
                        <p><strong>Move in Date: </strong> {} <p>
                        <p><strong>Move out Date:: </strong> {} <p>
                        <p><strong>Amount Due: </strong> R {} <p><br/>



                        <p style="margin:0px 0 12px 0;box-sizing:border-box;color:blue;"><font style="color: rgb(0, 32, 96);">Best regards,</font><br><font style="color: rgb(0, 32, 96);">
                            The Blue Spaces Team</font><br></p><table style="box-sizing:border-box;border-collapse:collapse;caption-side:bottom;" cellspacing="0" cellpadding="0" border="0">
                                <tbody style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;">
                                    <tr style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;">
                                        <td rowspan="6" style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;" align="center">
                                            <img src="/bluespace_custom_16/static/src/img/bluespace.jpg" style="box-sizing: border-box; vertical-align: middle; width: 218px; height: 118px;" width="218" height="118">
                                        </td>
                                        <td style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;color:blue;">
                                            <b style="box-sizing:border-box;font-weight:500;"><font style="color: rgb(0, 32, 96);">The Blue Spaces Team</font><br><br><font style="color: rgb(0, 32, 96);">(T):</font></b><font style="color: rgb(0, 32, 96);">&nbsp; 021 300 0645<b style="box-sizing:border-box;font-weight:500;"><br>(A):</b>&nbsp; 21 Conradie Cres, Asla Park, N2, Strand</font><b style="box-sizing:border-box;font-weight:500;"><br><font style="color: rgb(0, 32, 96);">​(E):</font></b>&nbsp; <a href="mailto:info@bluespaces.co.za" target="_blank"><u><font style="color: rgb(5, 99, 193);">info@bluespaces.co.za&nbsp;</font></u></a><br><b style="box-sizing:border-box;font-weight:500;"><font style="color: rgb(0, 32, 96);">(W):</font></b> <a href="http://www.bluespaces.co.za" target="_blank"><u><font style="color: rgb(5, 99, 193);">www.bluespaces.co.za</font></u></a><table style="box-sizing: border-box; border-collapse: collapse; caption-side: bottom; color: blue;">
                                                <tbody style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;"><tr style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;"></tr>
                                                <tr style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;"></tr>
                                                <tr style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;"></tr>
                                                <tr style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;"></tr>
                                                <tr style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;"></tr>
                                                <tr style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;"></tr>
                                            </tbody></table>
                                        </td>
                                    </tr>
                                </tbody>
                            </table><p style="margin-bottom: 0px;"><br></p>
                        </div>
                    """.format(current_time, current_date, move.partner_id.name, move.partner_id.mobile or move.partner_id.phone, move.partner_id.email, product_type, move_in_date, move_out_date, round(move.amount_residual,2))
            })'''
            template_id.sudo().send_mail(self.id, force_send=True)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _send_invoice(self):
        template_id = self.env['ir.config_parameter'].sudo().get_param(
            'sale.default_invoice_email_template'
        )
        if not template_id:
            return
        template_id = int(template_id)
        template = self.env['mail.template'].browse(template_id)
        for tx in self:
            tx = tx.with_company(tx.company_id).with_context(
                company_id=tx.company_id.id,
            )
            invoice_to_send = tx.invoice_ids.filtered(
                lambda i: not i.is_move_sent and i.state == 'posted' and i._is_ready_to_be_sent()
            )
            invoice_to_send.is_move_sent = True # Mark invoice as sent
            '''for invoice in invoice_to_send:
                lang = template._render_lang(invoice.ids)[invoice.id]
                model_desc = invoice.with_context(lang=lang).type_name
                invoice.with_context(model_description=model_desc).with_user(
                    SUPERUSER_ID
                ).message_post_with_template(
                    template_id=template_id,
                    email_layout_xmlid='mail.mail_notification_layout_with_responsible_signature',
                )'''