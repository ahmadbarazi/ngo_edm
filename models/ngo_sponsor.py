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
from odoo import fields, models, api, exceptions, _

class SponsorType(models.Model):
    _name = "ngo.sponsor.type"
    _description= "Sponsor Type"
    name = fields.Char(string = _("Sponsor Type"))
    _sql_constraints = [('sponsor_type_unique', 'unique (name)', _('Sponsor Type must be unique!'))]


class sponsor(models.Model):
    _name = 'ngo.sponsor'

    @api.model
    def _get_default_code(self):
        sequence = self.env['ir.sequence'].search([('code','=','ngo.sponsor')])
        next= sequence.get_next_char(sequence.number_next_actual)
        return next

    name = fields.Char(string=_(u"Name"))
    code = fields.Char(string=_(u"Code"), required=True, default=_get_default_code, track_visibility='onchange', copy=False, readonly=True)
    sponsor_type_id = fields.Many2one('ngo.sponsor.type',string=_("Type"))
    active = fields.Boolean(string=_(u"Active"), default=True)
    phone = fields.Char()
    mobile = fields.Char()
    fax = fields.Char(string=_(u"Fax"))
    website = fields.Char(string=_(u"Website Link"))
    email = fields.Char()
    is_family_sponsor = fields.Boolean(string=_(u"Family Sponsor"), default=False)
    is_orphan_sponsor = fields.Boolean(string=_(u"Orphan Sponsor"), default=False)
    is_student_sponsor = fields.Boolean(string=_(u"Student Sponsor"), default=False)

    country_id = fields.Many2one('res.country',string=_(u"Country"))
    city = fields.Many2one('ngo.city',string=_(u"City"))
    region = fields.Many2one('ngo.region',string=_(u"Region"))
    street = fields.Char(string=_(u"Street"))
    near = fields.Char(string=_(u"Near"))
    beside = fields.Char(string=_(u"Beside"))
    above = fields.Char(string=_(u"Above"))
    facing = fields.Char(string=_(u"Facing"))
    building = fields.Char(string=_(u"Building"))
    floor = fields.Char(string=_(u"Floor #"))

    work_country_id = fields.Many2one('res.country',string=_(u"Country"))
    work_city = fields.Many2one('ngo.city',string=_(u"City"))
    work_region = fields.Many2one('ngo.region',string=_(u"Region"))
    work_street = fields.Char(string=_(u"Street"))
    work_near = fields.Char(string=_(u"Near"))
    work_building = fields.Char(string=_(u"Building"))
    work_floor = fields.Char(string=_(u"Floor #"))

    notes = fields.Text(string=_(u"Notes"))
    ##### BEGIN BENEFICIARY DETAILS #####
    beneficiary_ids = fields.Many2many('ngo.beneficiary',string=_(u"Beneficiaries"))

    ### The link to the partner associated with
    ### It may benefit us in some way, i guess ?
    partner_id = fields.Many2one('res.partner',string=_(u"Partner id"))
    ##### BEGIN BENEFICIARY DETAILS #####

    @api.model
    def create(self,vals):
        ### Create sponsor
        vals['code'] = self.env['ir.sequence'].next_by_code('ngo.sponsor')

        sp = super(sponsor,self).create(vals)

        vals['is_sponsor']=True

        partner_id = self.env['res.partner'].create(vals)
        sp.partner_id = partner_id.id

        return sp