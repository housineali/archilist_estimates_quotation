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
                             selection=[('draft', 'Draft'), ('to_review', 'Estimate'),
                                        ('estimation_review', 'Estimation Review'),
                                        ('waiting_final_offer', 'Waiting Final Offer'), ('quotation', 'Quotation'),
                                        ('rejected', 'Rejected'), ('estimation_refused', 'Estimation Refused'), ],
                             default='draft')
    property_type_id = fields.Many2one(comodel_name="property.type", string="Property Type", required=False, )
    finishing_type_id = fields.Many2one(comodel_name="finishing.type", string="Finishing Budget", required=False, )
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

    rooms_no = fields.Integer(string="Number Of Romms", required=False, )
    bathrooms_no = fields.Integer(string="Number Of Bathrooms", required=False, )
    landscape = fields.Float(string="Landscape Area", required=False, )
    location_id = fields.Many2one(comodel_name="property.location", string="Property Location", required=False, )
    floor_no = fields.Integer(string="Floor Number", required=False, )
    visit = fields.Boolean(string="Visit Site", )
    design_drawing = fields.Selection(string="Design & Drawing",
                                      selection=[('2d_design_drawing', '2D Design $ Drawing'),
                                                 ('3d_design', '3D Design'),
                                                 ('3d_design_2d_drawing', '3D Design & 2D Drawing'),
                                                 ('detailed_3d', 'Detailed 3D'), ], required=False, )
    drawing_file = fields.Binary(string="Drawing File", )

    interior_categ_ids = fields.Many2many(comodel_name="product.category", relation="interior_categ_rel", string="", )
    exterior_categ_ids = fields.Many2many(comodel_name="product.category", relation="exterior_categ_rel", string="", )
    outdoor_categ_ids = fields.Many2many(comodel_name="product.category", relation="outdoor_categ_rel", string="", )
    product_ids = fields.One2many(comodel_name="product.line", inverse_name='request_id', string="Products", )
    image_ids = fields.One2many(comodel_name="request.image.line", inverse_name='request_id', string="Images", )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('real.state.request') or '/'
        res = super(Request, self).create(vals)
        return res

    @api.one
    def action_get_products(self):
        for line in self.product_ids:
            line.unlink()
        for categ in self.interior_categ_ids:
            for prod in categ.product_ids:
                self.product_ids.create(
                    {'request_id': self.id, 'product_id': prod.id, 'unit_price': prod.list_price,
                     'uom_id': categ.uom_id.id, 'category_id': categ.id})
        for categ in self.exterior_categ_ids:
            for prod in categ.product_ids:
                self.product_ids.create(
                    {'request_id': self.id, 'product_id': prod.id, 'unit_price': prod.list_price,
                     'uom_id': categ.uom_id.id, 'category_id': categ.id})
        for categ in self.outdoor_categ_ids:
            for prod in categ.product_ids:
                self.product_ids.create(
                    {'request_id': self.id, 'product_id': prod.id, 'unit_price': prod.list_price,
                     'uom_id': categ.uom_id.id, 'category_id': categ.id})

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
        sum = 0
        for line in self.product_ids:
            sum += line.total_cost
        self.estimated_budget = sum

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


class ImageLines(models.Model):
    _name = 'request.image.line'

    name = fields.Char(string="Description", required=False, )
    image = fields.Binary(string="Image", )
    request_id = fields.Many2one(comodel_name="real.state.request", string="", required=False, )



class ProductInteriorLines(models.Model):
    _name = 'product.line'

    @api.one
    @api.depends('amount', 'unit_price')
    def _compute_total_cost(self):
        self.total_cost = self.unit_price * self.amount

    product_id = fields.Many2one(comodel_name="product.product", string="Product", required=False, )
    category_id = fields.Many2one(comodel_name="product.category", string="Category", )
    request_id = fields.Many2one(comodel_name="real.state.request", string="", required=False, )
    quotation_id = fields.Many2one(comodel_name="real.state.quotation",  )
    uom_id = fields.Many2one(comodel_name="product.uom", string="Unit of measure", related='product_id.uom_id' )
    amount = fields.Float(string="Amount", required=False, )
    unit_price = fields.Float(string="Unit Price", related='product_id.list_price' )
    total_cost = fields.Float(string="Total Cost", compute=_compute_total_cost)
    notes = fields.Text(string="Notes", required=False, )
