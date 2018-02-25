# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import datetime


class Request(models.Model):
    _name = 'real.state.request'
    _description = "Real State Service Request"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    @api.one
    @api.depends('client_expected_start', 'client_expected_end')
    def _compute_client_expected_duration(self):
        if self.client_expected_start and self.client_expected_end:
            start = datetime.strptime(self.client_expected_start, "%Y-%m-%d")
            end = datetime.strptime(self.client_expected_end, "%Y-%m-%d")
            duration = end.date() - start.date()
            if int(duration.days) > 0:
                self.client_expected_duration = str(duration.days) + ' Day(s)'

    @api.one
    @api.depends('user_estimated_start', 'user_estimated_end')
    def _compute_user_estimated_duration(self):
        if self.user_estimated_start and self.user_estimated_end:
            start = datetime.strptime(self.user_estimated_start, "%Y-%m-%d")
            end = datetime.strptime(self.user_estimated_end, "%Y-%m-%d")
            duration = end.date() - start.date()
            if int(duration.days) > 0:
                self.user_estimated_duration = str(duration.days) + ' Day(s)'

    @api.one
    def _compute_quotation_count(self):
        records = self.env['real.state.quotation'].search([('request_id', '=', self.id)])
        self.quotation_count = len(records)

    @api.constrains('client_expected_start', 'client_expected_end')
    def _check_expecting_dates(self):
        if self.client_expected_start and self.client_expected_end:
            if self.client_expected_start > self.client_expected_end:
                raise exceptions.ValidationError('End Date Must Be After Start Date')

    @api.constrains('user_estimated_start', 'user_estimated_end')
    def _check_estimated_dates(self):
        if self.user_estimated_start and self.user_estimated_end:
            if self.user_estimated_start > self.user_estimated_end:
                raise exceptions.ValidationError('End Date Must Be After Start Date')

    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')
    user_id = fields.Many2one('res.users', string='Requester', index=True, track_visibility='onchange',
                              default=lambda self: self.env.uid)
    state = fields.Selection(string="State",
                             selection=[('draft', 'Draft'), ('to_review', 'Reviewing'),
                                        ('estimation_review', 'Estimation Review'),
                                        ('waiting_final_offer', 'Waiting Final Offer'), ('quotation', 'Quotation'),
                                        ('rejected', 'Rejected'), ('estimation_refused', 'Estimation Refused'), ],
                             default='draft')
    property_type_id = fields.Many2one(comodel_name="property.type", string="Property Type", required=False, )
    finishing_type_id = fields.Many2one(comodel_name="finishing.type", string="Finishing Type", required=False, )
    property_area = fields.Float(string="Property Area", required=False, )
    # client_budget = fields.Float(string="Budget", required=False, )
    client_expected_start = fields.Date(string="Expected Start", required=False, )
    client_expected_end = fields.Date(string="Expected End", required=False, )
    client_expected_duration = fields.Char("Expected Duration", compute=_compute_client_expected_duration, )
    client_notes = fields.Text(string="Client Notes", required=False, )
    estimated_budget = fields.Float(string="Estimated Cost", required=False, )
    user_estimated_start = fields.Date(string="Estimated Start", required=False, )
    user_estimated_end = fields.Date(string="Estimated End", required=False, )
    user_estimated_duration = fields.Char("Estimated Duration", compute=_compute_user_estimated_duration, )
    user_notes = fields.Text(string="User Notes", required=False, )
    quotation_count = fields.Integer(string="Count", required=False, compute=_compute_quotation_count)
    accepted_quotations_ids = fields.One2many(comodel_name="real.state.quotation.accepted", inverse_name="request_id",
                                              string="", required=False, )
    color = fields.Integer(string="", required=False, )

    # Interior
    rooms_no = fields.Integer(string="Number Of Rooms", required=False, )
    rooms_area = fields.Float(string="Rooms Area",  required=False, )
    toilets_no = fields.Integer(string="Number Of Bathrooms", required=False, )
    toilets_area = fields.Float(string="Bathrooms Area",  required=False, )
    bedroom_area = fields.Float(string="Bedrooms Area",  required=False, )
    living_rooms_area = fields.Float(string="Living Rooms Area",  required=False, )
    reception_area = fields.Float(string="Reception Area",  required=False, )
    office_space_area = fields.Float(string="Office Space Area",  required=False, )
    kitchen_area = fields.Float(string="Kitchen Area",  required=False, )
    counter_bar_area = fields.Float(string="Counter Bar Area",  required=False, )
    corridor_area = fields.Float(string="Corridor Area",  required=False, )
    lobby_area = fields.Float(string="Lobby / Foyer Area",  required=False, )
    stair_case_area = fields.Float(string="Stair Case Area",  required=False, )
    balcony_area = fields.Float(string="Balcony / Terrace Area",  required=False, )
    interior_product_ids = fields.One2many(comodel_name="product.line",inverse_name='request_interior_id', string="Products", )
    # Exterior
    building_facades_area = fields.Float(string="Building Facades Area",  required=False, )
    building_area = fields.Float(string="Roof Area",  required=False, )
    garage_area = fields.Float(string="Garage Area",  required=False, )
    walls_area = fields.Float(string="Walls & Fences Area",  required=False, )
    entrance_area = fields.Float(string="Entrance Area",  required=False, )
    gates_area = fields.Float(string="Gates Area",  required=False, )
    outdoor_stairs_area = fields.Float(string="Outdoor Stairs / Ladders Area",  required=False, )
    security_area = fields.Float(string="Security Area",  required=False, )
    exterior_product_ids = fields.One2many(comodel_name="product.line",inverse_name='request_exterior_id', string="Products", )
    # Landscape and Outdoor
    facedes_elements = fields.Float(string="Facades & Roof Elements",  required=False, )
    walk_ways_area = fields.Float(string="Walkways / Pavements Area",  required=False, )
    greens_area = fields.Float(string="Greens Area",  required=False, )
    pools_area = fields.Float(string="Lakes & Pools Area",  required=False, )
    sheds_area = fields.Float(string="Sheds & Pavilions Area",  required=False, )
    outdoor_product_ids = fields.One2many(comodel_name="product.line",inverse_name='request_outdoor_id', string="Products", )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('real.state.request') or '/'
        return super(Request, self).create(vals)

    def get_mail_url(self):
        return self.get_share_url()

    @api.multi
    def action_client_submit(self):
        self.write({'state': 'to_review'})
        group_manager = self.env['res.groups'].search(
            [('category_id.name', '=', 'Real State'), ('name', '=', 'Admin')])
        recipient_partners = []
        for recipient in group_manager.users:
            recipient_partners.append(
                (4, recipient.partner_id.id)
            )
        template = self.env['ir.model.data'].get_object('archilist_estimates_quotation',
                                                        'email_notification_client_submit_request')
        mail = self.env['mail.template'].browse(template.id).send_mail(self.id)
        mail_obj = self.env['mail.mail'].search([('id', '=', mail)])

        mail_obj.recipient_ids = recipient_partners

    @api.multi
    def action_reviewed(self):
        if self.estimated_budget == False or self.estimated_budget <= 0:
            raise exceptions.ValidationError('Please Enter Estimated Cost')
        if self.user_estimated_start == False:
            raise exceptions.ValidationError('Please Enter Estimated Start Date')
        if self.user_estimated_end == False:
            raise exceptions.ValidationError('Please Enter Estimated End Date')

        self.write({'state': 'estimation_review'})
        template = self.env['ir.model.data'].get_object('archilist_estimates_quotation',
                                                        'email_notification_admin_review_request')
        mail = self.env['mail.template'].browse(template.id).send_mail(self.id)

    @api.multi
    def action_estimation_accepted(self):

        self.write({'state': 'waiting_final_offer'})
        group_manager = self.env['res.groups'].search(
            [('category_id.name', '=', 'Real State'), ('name', '=', 'Admin')])
        recipient_partners = []
        for recipient in group_manager.users:
            recipient_partners.append(
                (4, recipient.partner_id.id)
            )
        template = self.env['ir.model.data'].get_object('archilist_estimates_quotation',
                                                        'email_notification_admin_accept_estimation')
        mail = self.env['mail.template'].browse(template.id).send_mail(self.id)
        mail_obj = self.env['mail.mail'].search([('id', '=', mail)])

        mail_obj.recipient_ids = recipient_partners

    @api.multi
    def action_rejected(self):
        self.write({'state': 'rejected'})
        template = self.env['ir.model.data'].get_object('archilist_estimates_quotation',
                                                        'email_notification_admin_reject_request')
        mail = self.env['mail.template'].browse(template.id).send_mail(self.id)

    @api.multi
    def action_estimation_refused(self):
        self.write({'state': 'estimation_refused'})
        group_manager = self.env['res.groups'].search(
            [('category_id.name', '=', 'Real State'), ('name', '=', 'Admin')])
        recipient_partners = []
        for recipient in group_manager.users:
            recipient_partners.append(
                (4, recipient.partner_id.id)
            )
        template = self.env['ir.model.data'].get_object('archilist_estimates_quotation',
                                                        'email_notification_admin_reject_estimation')
        mail = self.env['mail.template'].browse(template.id).send_mail(self.id)
        mail_obj = self.env['mail.mail'].search([('id', '=', mail)])

        mail_obj.recipient_ids = recipient_partners


class AcceptedQuotations(models.Model):
    _name = 'real.state.quotation.accepted'

    quotation_id = fields.Many2one(comodel_name="real.state.quotation", string="Quotation", required=False, )
    request_id = fields.Many2one(comodel_name="real.state.request", string="Request", required=False, )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Vendor", required=False, )
    vendor_estimated_cost = fields.Float(string="Final Cost", required=False, )
    vendor_estimated_start = fields.Date(string="Start", required=False, )
    vendor_estimated_end = fields.Date(string="End", required=False, )
    vendor_estimated_duration = fields.Char("Duration", )
    vendor_notes = fields.Text(string="Vendor Notes", required=False, )

class ProductInteriorLines(models.Model):
    _name = 'product.line'

    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )
    request_interior_id = fields.Many2one(comodel_name="real.state.request", string="", required=False, )
    request_exterior_id = fields.Many2one(comodel_name="real.state.request", string="", required=False, )
    request_outdoor_id = fields.Many2one(comodel_name="real.state.request", string="", required=False, )
    uom_id = fields.Many2one(comodel_name="product.uom", string="Unit of measure", required=False, )
    amount = fields.Float(string="Amount",  required=False, )
