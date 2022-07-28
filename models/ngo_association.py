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
from odoo.exceptions import ValidationError, Warning


class AssociationType(models.Model):
    _name = "ngo.association.type"
    _description = "Association Type"
    name = fields.Char(string=_("Association Type"))
    _sql_constraints = [('association_type_unique', 'unique (name)', _('Association type must be unique!'))]


class AssociationSpecialty(models.Model):
    _name = "ngo.association.specialty"
    _description = "Association Specialty"
    name = fields.Char(string=_("Association Specialty"))
    _sql_constraints = [('association_specialty_unique', 'unique (name)', _('Association specialty must be unique!'))]


class DoctorSpecialty(models.Model):
    _name = "ngo.doctor.specialty"
    _description = "Doctor Specialty"
    name = fields.Char(string=_("Doctor Specialty"))
    _sql_constraints = [('doctor_specialty_unique', 'unique (name)', _('Doctor specialty must be unique!'))]


class ResponsiblePosition(models.Model):
    _name = "ngo.responsible.position"
    _description = "Responsible Position"
    name = fields.Char(string=_("Responsible Position"))
    _sql_constraints = [('responsible_position_unique', 'unique (name)', _('The responsible position must be unique!'))]


class association(models.Model):
    _name = 'ngo.association'

    @api.model
    def _get_default_code(self):
        sequence = self.env['ir.sequence'].search([('code', '=', 'ngo.association')])
        next = sequence.get_next_char(sequence.number_next_actual)
        return next

    name = fields.Char(string=_(u"Name"))
    code = fields.Char(string=_(u"Code"), required=True, default=_get_default_code, track_visibility='onchange',
                       copy=False, readonly=True)
    active = fields.Boolean(string=_(u"Active"), default=True)

    association_type_id = fields.Many2one('ngo.association.type', string=_("Type"))
    association_specialty_id = fields.Many2one('ngo.association.specialty', string=_("Specialty"))

    phone = fields.Char()
    fax = fields.Char(string=_(u"Fax"))
    website = fields.Char(string=_(u"Website Link"))
    email = fields.Char()
    notes = fields.Text(string=_(u"Notes"))
    country_id = fields.Many2one('res.country', string=_(u"Country"))
    city = fields.Many2one('ngo.city', string=_(u"City"))
    region = fields.Many2one('ngo.region', string=_(u"Region"))
    street = fields.Char(string=_(u"Street"))
    address_remark = fields.Char(
        string='Address Remark',
    )
    near = fields.Char(string=_(u"Near"))
    beside = fields.Char(string=_(u"Beside"))
    above = fields.Char(string=_(u"Above"))
    facing = fields.Char(string=_(u"Facing"))
    building = fields.Char(string=_(u"Building"))
    floor = fields.Char(string=_(u"Floor #"))
    responsible_name = fields.Char(string=_(u"Responsible Name"))
    responsible_code = fields.Char(string=_(u"Responsible Code"))
    responsible_position = fields.Many2one('ngo.responsible.position', string=_(u"Responsible Position"))
    responsible_mobile = fields.Char(string=_(u"Responsible Mobile"))

    vendor_name = fields.Char(string=_(u"Vendor Name"))
    representative_name = fields.Char(string=_(u"Representative Name"))
    sponsor_id = fields.Many2one('ngo.sponsor', string=_(u"Sponsor"))
    # sponsor_name = fields.Char(string=_(u"Sponsor Name"))
    doctor_name = fields.Char(string=_(u"Doctor Name"))
    doctor_specialty = fields.Many2one('ngo.doctor.specialty', string=_(u"Doctor Specialty"))
    prefix = fields.Char(string=_("Prefix"), required=False, index=True)

    ##### BEGIN BENEFICIARY DETAILS #####
    # beneficiary_income_ids = fields.One2many('ngo.beneficiary.income','association_id',string=_(u"Beneficiaries"))

    ### The link to the partner associated with
    ### It may benefit us in some way, i guess ?
    partner_id = fields.Many2one('res.partner', string=_(u"Partner id"))

    ##### BEGIN BENEFICIARY DETAILS #####

    @api.onchange('prefix')
    def _onchange_prefix(self):
        # Create sequence related to the new application type
        if self.prefix:
            vals = {'name': 'NGO Beneficiary Application ' + self.prefix,
                    'code': 'ngo.beneficiary.application.' + self.prefix, 'prefix': self.prefix + '-', 'padding': 6}
            newsequence = self.env['ir.sequence']
            sequence = self.env['ir.sequence'].search(
                [('code', '=', 'ngo.beneficiary.application.' + self.prefix)])
            if not sequence:
                newsequence.create(vals)

    @api.constrains('prefix')
    def _reject_change_prefix_if_related_application_exists(self):
        # raise error once the entered prefix is duplicated
        # records= self.env['ngo.application.type'].search([])
        # for record in records:
        #     if record.prefix == self.prefix and record.name != self.name:
        #         raise ValidationError( _('prefix must be unique!'))
        # avoid prefix update in case of related beneficiary applications
        applications = self.env['ngo.beneficiary.application'].search_count(
            [('association_id', '=', self.id)])
        if applications > 0:
            raise ValidationError(_('Related applications exists!'))

    @api.model
    def create(self, vals):
        partnervals = []
        ### Create sponsor
        vals['code'] = self.env['ir.sequence'].next_by_code('ngo.association')

        sp = super(association, self).create(vals)

        # partnervals['is_association']=True

        partner_id = self.env['res.partner'].create(partnervals)
        partner_id.is_association = True
        sp.partner_id = partner_id.id

        return sp
