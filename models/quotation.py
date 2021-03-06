# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import datetime


class RequestQuotation(models.Model):
    _name = 'real.state.quotation'
    _description = "Real State Vendor Quotation"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    @api.one
    @api.depends('vendor_estimated_start', 'vendor_estimated_end')
    def _compute_vendor_estimated_duration(self):
        if self.vendor_estimated_start and self.vendor_estimated_end:
            start = datetime.strptime(self.vendor_estimated_start, "%Y-%m-%d")
            end = datetime.strptime(self.vendor_estimated_end, "%Y-%m-%d")
            duration = end.date() - start.date()
            if int(duration.days) > 0:
                self.vendor_estimated_duration = str(duration.days) + ' Day(s)'

    @api.constrains('vendor_estimated_start', 'vendor_estimated_end')
    def _check_estimated_dates(self):
        if self.vendor_estimated_start and self.vendor_estimated_end:
            if self.vendor_estimated_start > self.vendor_estimated_end:
                raise exceptions.ValidationError('End Date Must Be After Start Date')

    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')

    state = fields.Selection(string="State",
                             selection=[('draft', 'Draft'), ('vendor_submit', 'Vendor Offer'),
                                        ('to_review', 'Reviewing'), ('accepted', 'Accepted'), ('refused', 'Refused'), ],
                             default='draft')

    partner_id = fields.Many2one(comodel_name="res.partner", string="Vendor", required=False, )
    request_id = fields.Many2one(comodel_name="real.state.request", string="Request", required=False, )
    property_type_id = fields.Many2one(comodel_name="property.type", string="Property Type",
                                       related='request_id.property_type_id', readonly=True, )
    finishing_type_id = fields.Many2one(comodel_name="finishing.type", string="Finishing Budget",
                                        related='request_id.finishing_type_id', readonly=True, )
    property_area = fields.Float(string="Property Area", related='request_id.property_area', readonly=True, )
    vendor_estimated_cost = fields.Float(string="Estimated Cost", required=False, )
    vendor_estimated_start = fields.Date(string="Estimated Start", required=False, )
    vendor_estimated_end = fields.Date(string="Estimated End", required=False, )
    vendor_estimated_duration = fields.Char("Estimated Duration", compute=_compute_vendor_estimated_duration, )
    vendor_notes = fields.Text(string="Vendor Notes", required=False, )

    rooms_no = fields.Integer(string="Number Of Romms", related='request_id.rooms_no')
    bathrooms_no = fields.Integer(string="Number Of Bathrooms", related='request_id.bathrooms_no')
    landscape = fields.Float(string="Landscape Area", related='request_id.landscape')
    location_id = fields.Many2one(comodel_name="property.location", string="Property Location",
                                  related='request_id.location_id')
    floor_no = fields.Integer(string="Floor Number", related='request_id.floor_no')
    visit = fields.Boolean(string="Visit Site", related='request_id.visit')
    design_drawing = fields.Selection(string="Design & Drawing",
                                      selection=[('2d_design_drawing', '2D Design $ Drawing'),
                                                 ('3d_design', '3D Design'),
                                                 ('3d_design_2d_drawing', '3D Design & 2D Drawing'),
                                                 ('detailed_3d', 'Detailed 3D'), ], related='request_id.design_drawing')
    drawing_file = fields.Binary(string="Drawing File", related='request_id.drawing_file')

    interior_categ_ids = fields.Many2many(comodel_name="product.category",
                                          related='request_id.interior_categ_ids', )
    exterior_categ_ids = fields.Many2many(comodel_name="product.category",
                                          related='request_id.exterior_categ_ids', )
    outdoor_categ_ids = fields.Many2many(comodel_name="product.category",
                                         related='request_id.outdoor_categ_ids', )
    product_ids = fields.One2many(comodel_name="product.line", inverse_name='quotation_id', string="Products", )
    image_ids = fields.One2many(comodel_name="request.image.line", inverse_name='request_id',related='request_id.image_ids', string="Images", )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('real.state.quotation') or '/'
        return super(RequestQuotation, self).create(vals)

    @api.one
    def action_user_submit(self):
        self.write({'state': 'vendor_submit'})

    @api.one
    def action_vendor_submit(self):
        self.write({'state': 'to_review'})

    @api.one
    def action_user_accept(self):
        self.write({'state': 'accepted'})
        self.request_id.state = 'quotation'
        line = self.request_id.accepted_quotations_ids.create({'request_id': self.request_id.id})
        line.vendor_estimated_cost = self.vendor_estimated_cost
        line.vendor_estimated_start = self.vendor_estimated_start
        line.vendor_estimated_end = self.vendor_estimated_end
        line.vendor_estimated_duration = self.vendor_estimated_duration
        self.request_id.vendor_notes = self.vendor_notes

    @api.one
    def action_user_reject(self):
        self.write({'state': 'rejected'})


class QuotationsWizard(models.TransientModel):
    _name = 'real.state.quotation.wizard'
    _description = 'Vendors Group Of Quotations'
    partner_ids = fields.Many2many(comodel_name="res.partner", string="Vendors", )

    @api.one
    def create_quotations(self):
        request_id = self.env.context.get('active_id', False)
        for partner in self.partner_ids:
            self.env['real.state.quotation'].create(
                {'request_id': request_id, 'state': 'vendor_submit', 'partner_id': partner.id})
