# -*- coding: utf-8 -*-
##############################################################################
#   
#    Copyright (C) 2017 Navybits (<http://www.navybits.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import base64
from random import choice
from string import digits
import itertools
from werkzeug import url_encode
import pytz

from odoo.exceptions import ValidationError, AccessError
from odoo.modules.module import get_module_resource
from odoo.addons.resource.models.resource_mixin import timezone_datetime
from odoo import fields, models, api, exceptions, _


class guide(models.Model):
    _name = 'ngo.guide'
    _inherit = ['resource.mixin', 'image.mixin']

    @api.model
    def _default_image(self):
        image_path = get_module_resource('ngo_edm', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    @api.model
    def _get_default_code(self):
        sequence = self.env['ir.sequence'].search([('code', '=', 'ngo.guide')])
        next = sequence.get_next_char(sequence.number_next_actual)
        return next

    name = fields.Char(string=_(u"Name"))
    code = fields.Char(string=_(u"Code"), required=True, default=_get_default_code, track_visibility='onchange',
                       copy=False, readonly=True)
    active = fields.Boolean(string=_(u"Active"), default=True)
    phone = fields.Char()
    mobile = fields.Char()
    fax = fields.Char(string=_(u"Fax"))
    website = fields.Char(string=_(u"Website Link"))
    email = fields.Char()

    country_id = fields.Many2one('res.country', string=_(u"Country"))
    city = fields.Many2one('ngo.city', string=_(u"City"))
    region = fields.Many2one('ngo.region', string=_(u"Region"))
    street = fields.Char(string=_(u"Street"))
    near = fields.Char(string=_(u"Near"))
    building = fields.Char(string=_(u"Building"))
    address_remark = fields.Char(
        string='Address Remark',
    )
    floor = fields.Char(string=_(u"Floor #"))
    image_1920 = fields.Image(default=_default_image)

    # image_variant_1920 = fields.Image("Variant Image", max_width=1920, max_height=1920)
    # image_variant_128 = fields.Image("Variant Image 128", related="image_variant_1920", max_width=128, max_height=128, store=True)
    # image_1920 = fields.Image("Image", compute='_compute_image_1920', inverse='_set_image_1920')
    # image_128 = fields.Image("Image 128", compute='_compute_image_128')
    # image_1024 = fields.Image("Image", max_width=1920, max_height=1920, store=True)
    # image_128 = fields.Image("Image 128", related="image_1024", max_width=128, max_height=128, store=True)

    notes = fields.Text(string=_(u"Notes"))

    ##### BEGIN BENEFICIARY DETAILS #####
    beneficiary_ids = fields.Many2many('ngo.beneficiary', string=_(u"Beneficiaries"))

    ### The link to the partner associated with
    ### It may benefit us in some way, i guess ?
    partner_id = fields.Many2one('res.partner', string=_(u"Partner id"))

    ##### BEGIN BENEFICIARY DETAILS #####

    def _compute_image_1920(self):
        """Get the image from the template if no image is set on the variant."""
        for record in self:
            record.image_1920 = record.image_variant_1920

    def _set_image_1920(self):
        for record in self:
            if (
                    # We are trying to remove an image even though it is already
                    # not set, remove it from the template instead.
                    not record.image_1920 and not record.image_variant_1920 or
                    # We are trying to add an image, but the template image is
                    # not set, write on the template instead.
                    record.image_1920
            ):
                record.image_variant_1920 = False
            else:
                record.image_variant_1920 = record.image_1920

    def _compute_image_128(self):
        """Get the image from the template if no image is set on the variant."""
        for record in self:
            record.image_128 = record.image_variant_128

    @api.model
    def create(self, vals):
        partnervals = []
        ### Create guide
        vals['code'] = self.env['ir.sequence'].next_by_code('ngo.guide')
        # partnervals['is_guide']= True

        gd = super(guide, self).create(vals)

        # gd = super(guide,self).create(vals)

        partner_id = self.env['res.partner'].create(partnervals)
        partner_id.is_guide = True
        gd.partner_id = partner_id.id

        return gd
