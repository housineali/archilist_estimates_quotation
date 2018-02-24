# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PropertyType(models.Model):
    _name = 'property.type'
    _rec_name = 'name'
    _description = 'Property Type'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    name = fields.Char(string="name", required=False, track_visibility='onchange')
    active = fields.Boolean(string="active", default=True, track_visibility='onchange')

class FinishingType(models.Model):
    _name = 'finishing.type'
    _rec_name = 'name'
    _description = 'Finishing Type'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    name = fields.Char(string="name", required=False, track_visibility='onchange')
    active = fields.Boolean(string="active", default=True, track_visibility='onchange')
