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
from odoo import fields, models, api, exceptions,_
from datetime import datetime
class Partner(models.Model):
    _inherit = 'res.partner'

    ### The class partner is inherited to be able work with the accounting modules
    ### Without it i can't use my classes to enter them in the Customer/Vendor fields in the acounting module

    is_beneficiary = fields.Boolean(string=_(u"Is Beneficiary"))
    is_application = fields.Boolean(string=_(u"Is Application"))
    is_sponsor = fields.Boolean(string=_(u"Is Sponsor"))
    is_responsible = fields.Boolean(string=_(u"Is Responsible"))
    is_association = fields.Boolean(string=_(u"Is Association"))
    is_guide = fields.Boolean(string=_(u"Is Guide"))
    region = fields.Many2one('ngo.region',string=_(u"Region"))
    near = fields.Char(string=_(u"Near"))
    building = fields.Char(string=_(u"Building"))
    floor = fields.Char(string=_(u"Floor #"))
    mohafaza = fields.Many2one('ngo.mohafaza',string=_("Mohafaza"))
    kadaa = fields.Many2one('ngo.kadaa',string=_("Kadaa"))
    appartment = fields.Char(string=_("Appartment"))
    neighborhood = fields.Many2one('ngo.neighborhood',string=_("Neighborhood"))
    building_number = fields.Char(string=_("Building Number"))
    # state = fields.Selection(string=_(u"Application State"), selection=[('draft', _(u'Draft')), ('managerapprove', _(
    #     u'Manager Approve')), ('review', _(u'Review'))], track_visibility='onchange', default='draft')
    # association_id = fields.Many2one('ngo.association',string=_("Association"))
    # application_type_id = fields.Many2one('ngo.application.type', string=_(
    #     u"Application Type"))
    # prefix = fields.Char(string=_("Prefix"), required=False, index=True)
    # application_date = fields.Date(index=True, default=datetime.today())
    # guide_id = fields.Many2one('ngo.guide', string=_(u"Guide"))
    # registration_number = fields.Char(string=_(u"Registration Number"), track_visibility='onchange')
    # registration_place = fields.Many2one('ngo.kadaa', string=_("Registration Place"), track_visibility='onchange')
    # decision_id = fields.Many2one('ngo.application.decision.list', string=_(
    #     u"Application Decision"), track_visibility='onchange')
    # electricity_meter_number = fields.Char(
    #     string=_(u"Electricity Meter Number"),size=13)
    # address_remark = fields.Char(
    #     string='Address Remark',
    # )
    # in case of changing the size of code field all related models the contain the code where the partner used as parent for these models the code should updated also
    code = fields.Char('Code', size=32)

    @api.depends('distribution_ids.partner_id')
    def _compute_distribution_count(self):
        # The current user may not have access rights for donations
        for partner in self:
            try:
                partner.distribution_count = len(partner.distribution_ids)
            except Exception:
                partner.distribution_count = 0

    distribution_ids = fields.One2many(
        'ngo.distribution.line',
        'partner_id',
        string=_(u"Distributions"),
        readonly=True
    )
    distribution_count = fields.Integer(
        compute='_compute_distribution_count',
        string=_(u"# of Distributions"),
        readonly=True
    )
    