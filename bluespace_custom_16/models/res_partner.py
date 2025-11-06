# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

from odoo.exceptions import UserError

class ResPartnerTag(models.Model):
    _inherit = "res.partner.category"

    rank = fields.Integer(string="Rank")

class Partner(models.Model):
    _inherit = 'res.partner'

    state = fields.Selection([
        ('draft', 'draft'),
        ('rejected', 'Reject'),
        ('approve', 'Approve'),
    ], default='draft',)
    free_office = fields.Boolean(string="Free Office")

    #Entity
    entity_name = fields.Char("Entity Name")
    entity_reg_no = fields.Char(string="Entity Registration Number")
    entity_vat_no = fields.Char(string="Entity VAT Number")
    entity_reg_cert = fields.Binary(string="Upload Entity Registration Certificate/Document")

    #Entity Representative
    entity_rep_role = fields.Many2one("entity.representative.role", string="Entity Representative Role")
    entity_rep_name_sur = fields.Char(string="Entity Representative Name and Surname")
    entity_rep_id_number = fields.Char(string="Entity Representative ID Number")
    entity_rep_cell = fields.Char(string="Entity Representative Cell Phone Number")
    entity_rep_email = fields.Char(string="Entity Representative Email Address")
    entity_rep_proof = fields.Binary(string="Entity Representative- Upload Proof of Current Residential Address (FICA complaint)")
    entity_rep_sign = fields.Binary(string="Entity Representative- Mandate/Resolution for Representative to Sign this Lease Agreement")

    #Individual Responsible for Payment of Accounts
    ind_resp_pay_ac_name_sur = fields.Char(string="Individual Responsible for Payment of Accounts - Name and Surname")
    ind_resp_pay_ac_cell = fields.Char(string="Individual Responsible for Payment of Accounts - Telephone/Cell Phone Number")
    ind_resp_pay_ac_email = fields.Char(string="Individual Responsible for Payment of Accounts - Email Address")

    vehicle_reg_num = fields.Char(string="Vehicle Registration Number")
    most_recent_landlord_name = fields.Char(string="Most Recent Landlord Name")
    most_recent_landlord_phone = fields.Char(string="Most Recent Landlord Contact Number")
    relative_name = fields.Char(string="Friend/Relative Name")
    relative_phone = fields.Char(string="Friend/Relative Contact Number")

    def _prepare_portal_user(self):
        group_portal_user = self.env.ref('base.group_portal')
        return {
            "login" : self.email,
            "name" : self.name,
            "email" : self.email,
            "active" : True,
            "partner_id" : self.id,
            "groups_id" : [(4, group_portal_user.id)]
        }

    def action_approved(self):
        self.write({'state' : 'approve'})
        '''portal_user_vals = self._prepare_portal_user()
        users_id = self.env['res.users'].search([('email', '=', self.email)],limit=1)
        if not users_id:
            portal_user_id = self.env['res.users'].sudo().create(portal_user_vals)
            if portal_user_id:
                portal_user_id.action_reset_password()'''

        portal_wizard = self.env['portal.wizard'].with_context(active_ids=[self.id]).create({})
        portal_user = portal_wizard.user_ids
        portal_user.action_grant_access()
        return True

    # def action_approved(self):
    #     print("APOOOOOOO")
    #     self.write({'state' : 'approve'})

    def action_rejected(self):
        self.write({'state' : 'rejected'})

    def action_draft(self):
        self.write({'state' : 'draft'})

    def _compute_partner_document_count(self):
        # Method not optimized for batches since it is only used in the form view.
        document_count = 0
        for record in self:
            attachment_count = self.env['ir.attachment'].search_count([('res_model', '=', 'res.partner'), ('res_id', '=', record.id)])
            record.partner_document_count = attachment_count

    partner_document_count = fields.Integer(compute='_compute_partner_document_count')

    def action_open_attechment(self):
        attachment_obj = self.env['ir.attachment']
        attachment_ids = attachment_obj.search([('res_id', '=', self.id), ('res_model', '=', 'res.partner')])
        action = {
            "name" : _('Partner Documents'),
            "view_type" : 'form',
            'view_mode': 'kanban,list',
            "res_model": 'ir.attachment',
            "view_id" : False,
            "type" : "ir.actions.act_window",
            "domain" : [('id', 'in', attachment_ids.ids)],
            }
        return action

    def get_test_custom_date(self):
        notification_test_date = self.env['test.date'].search([], limit=1)
        if notification_test_date:
            return notification_test_date.test_date
        return fields.Date.today()

    def _execute_followup_partner(self, options=None):
        res = super()._execute_followup_partner(options)
        today = fields.Date.today()
        test_date = self.get_test_custom_date()
        if today.day in [4, 6] or test_date.day in [4, 6]:
            self.ensure_one()
            if options is None:
                options = {}
            if options.get('manual_followup', self.followup_status in ['in_need_of_action', 'with_overdue_invoices']):
                followup_line = self.followup_line_id or self._get_first_followup_level()

                if followup_line.create_activity:
                    # log a next activity for today
                    self.activity_schedule(
                        activity_type_id=followup_line.activity_type_id and followup_line.activity_type_id.id or self._default_activity_type().id,
                        note=followup_line.activity_note,
                        summary=followup_line.activity_summary,
                        user_id=(self._get_followup_responsible()).id
                    )

                #self._update_next_followup_action_date(followup_line)
                if self.followup_next_action_date:
                    self.followup_next_action_date = False

                email_subject = ''
                if today.day == 4 or test_date.day == 4:
                    email_subject = 'Blue Spaces Rental Payment Overdue'
                if today.day == 6 or test_date.day == 6:
                    email_subject = 'Blue Spaces Rental Payment Overdue - Final Notice'

                self._send_followup(options={'followup_line': followup_line, 'email_subject': email_subject, **options})

                return True
            return False
        return res


    def _cron_execute_followup_company(self):
        res = super()._cron_execute_followup_company()
        today = fields.Date.today()
        test_date = self.get_test_custom_date()
        if today.day in [4, 6] or test_date.day in [4, 6]:
            followup_data = self._query_followup_data(all_partners=True)
            in_need_of_action = self.env['res.partner'].browse([d['partner_id'] for d in followup_data.values() if d['followup_status'] in ['with_overdue_invoices', 'in_need_of_action']])
            in_need_of_action_auto = in_need_of_action.filtered(lambda p: p.followup_line_id.auto_execute and p.followup_reminder_type == 'automatic')
            for partner in in_need_of_action_auto:
                try:
                    partner._execute_followup_partner()
                except UserError as e:
                    # followup may raise exception due to configuration issues
                    # i.e. partner missing email
                    _logger.warning(e, exc_info=True)
        return res

class EntityRepresentativeRole(models.Model):
    _name = 'entity.representative.role'
    _description = 'Entity Representative Role'

    name = fields.Char(string="Role")

class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    is_individual = fields.Boolean(string="Is Individual")
