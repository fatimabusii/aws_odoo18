from odoo import api, fields, models, _, SUPERUSER_ID
import datetime
import calendar
from dateutil import relativedelta
from odoo.http import request
from datetime import timedelta,datetime
import logging
_logger = logging.getLogger(__name__)
from odoo.tools import format_amount, str2bool

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def message_post_with_template(self, template_id, **kwargs):
        context = self.env.context
        if kwargs.get('model', self._name) == 'sale.order' and context.get('force_send') == False:
            return
        return super(MailThread, self).message_post_with_template(template_id, **kwargs)

class TestDate(models.Model):
    _name = 'test.date'
    _rec_name= 'test_date'
    _description = 'Test Date'

    test_date = fields.Date('Test Date', required=True)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'stage_id' in init_values:
            return False #self.env.ref('sale_subscription.subtype_stage_change')
        return super()._track_subtype(init_values)

    def get_test_custom_date(self):
        notification_test_date = self.env['test.date'].search([], limit=1)
        if notification_test_date:
            return notification_test_date.test_date
        return fields.Date.today()

    @api.model
    def _cron_move_out_customer(self):
        domain = [('state', 'in', ('sale', 'done')), 
            ('stage_category', '!=', 'closed')]
        
        sale_order_ids = self.sudo().search(domain).filtered(lambda x: (x.is_notice_given and x.is_flexible) or (x.is_specific_move))
        current_date = fields.Date.today()
        
        for sale in sale_order_ids:
            move_out_date = ''
            flag = False
            test_date = self.get_test_custom_date()
            if sale.is_flexible and sale.notice_given :
                move_out_date = 'Month to Month'
                dt = datetime.strptime("1 " + sale.month+ " " + sale.year_id.name, "%d %m %Y").date()
                if (dt - current_date).days in [1, 5] or (dt - test_date).days in [1, 5]:
                    flag = True
                if flag:
                    template_id = self.env.ref('bluespace_notification.email_template_move_out_customer', raise_if_not_found=False)
                    email_from = self.env.company.email
                    if template_id:
                        template_id.sudo().write({
                            'email_from': "info@bluespaces.co.za",
                            'body_html': """
                                <div style="font-family: Calibri;">
                                    <p>Dear Blue Spaces Customer,</p>
                                    <p>According to our system, you have given notice that you wish to terminate your lease and vacate your Rented Space on {}</p>
                                    
                                    <p>Please note that your final check-out time is at 12h00, midday on {} <p>
    
                                    <p>Please remember to attend the move out inspection as arranged, or will be arranged with you closer to the time.<p>
    
                                    <p>Attending this inspection will ensure your lease is conclusively terminated and your deposit returned if no amounts are outstanding and the rented space is in the same condition as at the time of your move in date.<p>
    
                                    <p>We thank you for doing business with us and hope to see you again soon!<p>
    
                                    <p style="margin:0px 0 12px 0;box-sizing:border-box;color:blue;"><font style="color: rgb(0, 32, 96);">Best regards,</font><br><font style="color: rgb(0, 32, 96);">
                                        The Blue Spaces Team</font><br></p><table style="box-sizing:border-box;border-collapse:collapse;caption-side:bottom;" cellspacing="0" cellpadding="0" border="0">
                                            <tbody style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;">
                                                <tr style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;">
                                                    <td rowspan="6" style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;" align="center">
                                                        <img src="/bluespace_custom_16/static/src/img/bluespace.jpg" style="box-sizing: border-box; vertical-align: middle; width: 218px; height: 118px;" width="218" height="118">
                                                    </td>
                                                    <td style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;color:blue;">
                                                        <b style="box-sizing:border-box;font-weight:500;"><font style="color: rgb(0, 32, 96);"><strong style="box-sizing:border-box;font-weight:900;">The Blue Spaces Team</strong></font><br><br><font style="color: rgb(0, 32, 96);">(T):</font></b><font style="color: rgb(0, 32, 96);">&nbsp; 021 300 0645<b style="box-sizing:border-box;font-weight:500;"><br>(A):</b>&nbsp; 21 Conradie Cres, Asla Park, N2, Strand</font><b style="box-sizing:border-box;font-weight:500;"><br><font style="color: rgb(0, 32, 96);">​(E):</font></b>&nbsp; <a href="mailto:info@bluespaces.co.za" target="_blank"><u><font style="color: rgb(5, 99, 193);">info@bluespaces.co.za&nbsp;</font></u></a><br><b style="box-sizing:border-box;font-weight:500;"><font style="color: rgb(0, 32, 96);">(W):</font></b> <a href="http://www.bluespaces.co.za" target="_blank"><u><font style="color: rgb(5, 99, 193);">www.bluespaces.co.za</font></u></a><table style="box-sizing: border-box; border-collapse: collapse; caption-side: bottom; color: blue;">
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
                                """.format(move_out_date, move_out_date)
                        })
                        template_id.sudo().send_mail(sale.id, force_send=True)
            elif sale.is_specific_move :
                move_out_date = sale.end_date.strftime("%d/%m/%Y")
                _logger.info("test_date>>>>>>>>>>>>>>>>>> %s ==== %s",test_date,sale.end_date)
                _logger.info("-----------------------%s",(sale.end_date - test_date).days)
                if (sale.end_date - current_date).days in [1, 5] or (sale.end_date - test_date).days in [1, 5]:
                    flag = True
                _logger.info("FFFFFFFFFFFFFFFFFFFFFFFF:::: %s %s",sale,flag)
                if flag:
                    template_id = self.env.ref('bluespace_notification.email_template_move_out_customer', raise_if_not_found=False)
                    email_from = self.env.company.email
                    if template_id:
                        template_id.sudo().write({
                            'email_from': "info@bluespaces.co.za",
                            'body_html': """
                                <div style="font-family: Calibri;">
                                    <p>Dear Blue Spaces Customer,</p>
                                    <p>According to our system, you have given notice that you wish to terminate your lease and vacate your Rented Space on {}</p>
                                    
                                    <p>Please note that your final check-out time is at 12h00, midday on {} <p>
    
                                    <p>Please remember to attend the move out inspection as arranged, or will be arranged with you closer to the time.<p>
    
                                    <p>Attending this inspection will ensure your lease is conclusively terminated and your deposit returned if no amounts are outstanding and the rented space is in the same condition as at the time of your move in date.<p>
    
                                    <p>We thank you for doing business with us and hope to see you again soon!<p>
    
                                    <p style="margin:0px 0 12px 0;box-sizing:border-box;color:blue;"><font style="color: rgb(0, 32, 96);">Best regards,</font><br><font style="color: rgb(0, 32, 96);">
                                        The Blue Spaces Team</font><br></p><table style="box-sizing:border-box;border-collapse:collapse;caption-side:bottom;" cellspacing="0" cellpadding="0" border="0">
                                            <tbody style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;">
                                                <tr style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;">
                                                    <td rowspan="6" style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;" align="center">
                                                        <img src="/bluespace_custom_16/static/src/img/bluespace.jpg" style="box-sizing: border-box; vertical-align: middle; width: 218px; height: 118px;" width="218" height="118">
                                                    </td>
                                                    <td style="border-style:solid;box-sizing:border-box;border-left-width:0px;border-bottom-width:0px;border-right-width:0px;border-top-width:0px;border-left-color:inherit;border-bottom-color:inherit;border-right-color:inherit;border-top-color:inherit;color:blue;">
                                                        <b style="box-sizing:border-box;font-weight:500;"><font style="color: rgb(0, 32, 96);"><strong style="box-sizing:border-box;font-weight:900;">The Blue Spaces Team</strong></font><br><br><font style="color: rgb(0, 32, 96);">(T):</font></b><font style="color: rgb(0, 32, 96);">&nbsp; 021 300 0645<b style="box-sizing:border-box;font-weight:500;"><br>(A):</b>&nbsp; 21 Conradie Cres, Asla Park, N2, Strand</font><b style="box-sizing:border-box;font-weight:500;"><br><font style="color: rgb(0, 32, 96);">​(E):</font></b>&nbsp; <a href="mailto:info@bluespaces.co.za" target="_blank"><u><font style="color: rgb(5, 99, 193);">info@bluespaces.co.za&nbsp;</font></u></a><br><b style="box-sizing:border-box;font-weight:500;"><font style="color: rgb(0, 32, 96);">(W):</font></b> <a href="http://www.bluespaces.co.za" target="_blank"><u><font style="color: rgb(5, 99, 193);">www.bluespaces.co.za</font></u></a><table style="box-sizing: border-box; border-collapse: collapse; caption-side: bottom; color: blue;">
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
                                """.format(move_out_date, move_out_date)
                        })
                        template_id.sudo().send_mail(sale.id, force_send=True)
    
    def get_manager_email(self):
        manager_email = self.env['ir.config_parameter'].sudo().get_param('bluespace_notification.manager_email')
        return manager_email

    def get_move_in_list(self):
        today = fields.Date.today()
        
        domain = [('state', 'in', ('sale', 'done')), 
            ('stage_category', '!=', 'closed')]
        
        sale_order_ids = self.sudo().search(domain).filtered(lambda x: not x.is_notice_given)
        current_date = fields.Date.today()
        dt_new = current_date + relativedelta.relativedelta(months=1, day=1)
        last_dt = dt_new.replace(day = calendar.monthrange(dt_new.year, dt_new.month)[1])

        sale_order_lines = sale_order_ids.mapped('order_line').filtered(lambda x: x.product_id.product_category in ['2_office', '3_boardroom', '1_storage_unit', '4_parking'] and x.start_date.date() >= dt_new and x.start_date.date() <= last_dt)
        test_date = self.get_test_custom_date()

        move_in_list = []

        for sale in sale_order_lines:
            move_in_dict = {}
            move_in_dict.update({'id': sale.order_id.id, 'order_no': sale.order_id.name, 'customer_name': sale.order_id.partner_id.name, 'move_in_date': sale.start_date.date()})
            move_in_list.append(move_in_dict)

        return move_in_list

    @api.model
    def _cron_move_in_customer_manager(self):
        today = fields.Date.today()
        test_date = self.get_test_custom_date()
        
        '''domain = [('state', 'in', ('sale', 'done')), 
            ('stage_category', '!=', 'closed')]
        
        sale_order_ids = self.sudo().search(domain).filtered(lambda x: not x.is_notice_given)
        current_date = fields.Date.today()
        dt_new = current_date + relativedelta.relativedelta(months=1, day=1)
        last_dt = dt_new.replace(day = calendar.monthrange(dt_new.year, dt_new.month)[1])

        sale_order_lines = sale_order_ids.mapped('order_line').filtered(lambda x: x.product_id.product_category in ['2_office', '3_boardroom', '1_storage_unit', '4_parking'] and x.start_date.date() >= dt_new and x.start_date.date() <= last_dt)
        test_date = self.get_test_custom_date()

        move_in_list = []

        for sale in sale_order_lines:
            move_in_dict = {}
            move_in_dict.update({'id': sale.order_id.id, 'order_no': sale.order_id.name, 'customer_name': sale.order_id.partner_id.name, 'move_in_date': sale.start_date.date()})
            move_in_list.append(move_in_dict)'''

        if today.day in [25] or test_date.day in [25]:
            template_id = self.env.ref('bluespace_notification.email_template_move_in_customer_manager', raise_if_not_found=False)
            email_from = self.env.company.email
            manager_email = self.env['ir.config_parameter'].sudo().get_param('bluespace_notification.manager_email')
            user = self.env.user.id
            if template_id:
                '''template_id.sudo().write({
                    'email_from': "info@bluespaces.co.za",
                    'email_to': manager_email or '',
                    'body_html': """
                        <div style="font-family: Calibri;">
                            <p>Dear Blue Spaces Manager,</p>
                            <p>Rental Order No : {} </p>
                            <p>Customer Name : {} </p>
                            <p>Move In Date : {} </p>

                                <t t-out="{{ move_in_list }}"/>

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
                        """
                })'''
                template_id.sudo().send_mail(self.id, force_send=True)