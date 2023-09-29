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
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError, ValidationError, Warning

from odoo import exceptions
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import common
from odoo.tools import mute_logger, view_validation

import warnings
import ast
import requests
import logging


class NgoMohafaza(models.Model):
    _name = 'ngo.mohafaza'
    _description = 'Mohafaza'
    _order = "name"
    code = fields.Char(
        string=_(u"code")
    )
    name = fields.Char(
        string=_(u"Mohafaza"),
        required=True,
    )
    _sql_constraints = [('name_unique', 'unique(name)',
                         _('Mohafaza already exists!'))]


class NgoKada(models.Model):
    _name = 'ngo.kadaa'
    _description = 'Kadaa'
    _order = "name"
    code = fields.Char(
        string=_(u"code")
    )
    name = fields.Char(
        string=_(u"Kadaa"),
        required=True,
    )
    mohafaza_id = fields.Many2one('ngo.mohafaza', string=_("Mohafaza"))

    _sql_constraints = [('name_unique', 'unique(name)',
                         _('Kadaa already exists!'))]


class ApplicationDocs(models.Model):
    _name = "ngo.application.docs"
    _description = "Application Documents"
    name = fields.Char(string=_("Application Document"))
    _sql_constraints = [('application_docs_unique', 'unique (name)', _(
        'Application document must be unique!'))]


class ApplicationType(models.Model):
    _name = "ngo.application.type"
    _description = "Application Type"
    name = fields.Char(string=_("Application Type"))
    prefix = fields.Char(string=_("Prefix"), required=False, index=True)
    association_id = fields.Many2one(
        'ngo.association', string=_(u"Association"))

    _sql_constraints = [('application_type_unique', 'unique (name)', _('Application type must be unique!')),
                        ('application_type_prefix_unique', 'unique (prefix)', _('prefix must be unique!'))]

    @api.constrains('prefix')
    def _reject_change_prefix_if_related_application_exists(self):
        # raise error once the entered prefix is duplicated
        # records= self.env['ngo.application.type'].search([])
        # for record in records:
        #     if record.prefix == self.prefix and record.name != self.name:
        #         raise ValidationError( _('prefix must be unique!'))
        # avoid prefix update in case of related beneficiary applications
        applications = self.env['ngo.beneficiary.application'].search_count(
            [('application_type_id', '=', self.id)])
        if applications > 0:
            raise ValidationError(_('Related applications exists!'))

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


class ApplicationDecisionList(models.Model):
    _name = "ngo.application.decision.list"
    _description = "Application Decision"
    name = fields.Char(string=_("Decision Code"))
    description = fields.Char(string=_("Decision Description"))

    _sql_constraints = [('application_decision_unique',
                         'unique (name)', _('Decision number must be unique!'))]


# # general address model to be used in any other model
# class AddressInfo  (models.Model):
#     _name = "ngo.address"
#     _description= "Address"
#     # country_id=fields.Many2one('res.country',string=_("Country"))
#     # city = fields.Many2one('ngo.city',string=_(u"City"))
#     region = fields.Many2one('ngo.region',string=_(u"Region"))
#     # street = fields.Char(string=_(u"Street"))
#     near = fields.Char(string=_(u"Near"))
#     # beside = fields.Char(string=_(u"Beside"))
#     # above = fields.Char(string=_(u"Above"))
#     # facing = fields.Char(string=_(u"Facing"))
#     building = fields.Char(string=_(u"Building"))
#     floor = fields.Char(string=_(u"Floor #"))
#     mohafaza = fields.Many2one('ngo.mohafaza',string=_("Mohafaza"))
#     kadaa = fields.Many2one('ngo.kadaa',string=_("Kadaa"))
#     appartment = fields.Char(string=_("Appartment"))
#     neighborhood = fields.Many2one('ngo.neighborhood',string=_("Neighborhood"))
#     building_number = fields.Char(string=_("Building Number"))


class BeneficiaryApplication(models.Model):
    _name = 'ngo.beneficiary.application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Beneficiary Application"


    # @api.model
    # def _get_default_application_name(self):
    #     for application in self:
            # raise UserError(application.prefix)
            # sequence = self.env['ir.sequence'].search(
            #     [('code', '=', 'ngo.beneficiary.application.') + self.prefix])
            # if sequence:
            #     return 'استمارة ' + str(sequence.number_next_actual)
            # else:
            #     return ''

    # @api.model
    # def _get_default_code(self):
    #     app_type = self.env['ngo.application.type'].search(
    #         [('name', '=', 'عباد - بيروت')], limit=1)
    #     if app_type:
    #         self.application_type_id = app_type.id
    #     # if self.application_type_id:
    #         app_prefix = app_type.prefix

    #     if app_prefix:
    #         sequence = self.env['ir.sequence'].search(
    #             [('code', '=', 'ngo.beneficiary.application.'+app_prefix)])
    #     else:
    #         sequence = self.env['ir.sequence'].search(
    #             [('code', '=', 'ngo.beneficiary.application')])
    #     next = sequence.get_next_char(sequence.number_next_actual)
    #     return next

    search_ids = fields.Char(compute="_compute_search_ids",search='search_ids_search')

    create_date = fields.Datetime(string='Created on',readonly=False)
    department_id = fields.Many2one('res.users')

    @api.depends('department_id')
    def _compute_search_ids(self):
        print('my compute')

    def search_ids_search(self, operator, operand):
        if self.env.user.has_group('ngo_edm.ngo_admin'):
            return [('id', 'in', self.env['ngo.beneficiary.application'].search([]).ids)]
        elif self.env.user.has_group('ngo_edm.ngo_user'):
            return [('id', 'in', self.env['ngo.beneficiary.application'].search([('id','=',-1)]).ids)]
        else:
            obj = self.env['ngo.beneficiary.application'].search([('application_type_id', '=',self.env.user.application_type_id.id)]).ids
            return [('id', 'in', obj)]

    @api.model
    def default_get(self, fields_list):
        res = super(BeneficiaryApplication, self).default_get(fields_list)
        expense_category_count = self.env['ngo.expense.category'].search_count([])
        income_type_count = self.env['ngo.income.type'].search_count([])
        vals = []
        vals2 = []
        if expense_category_count > 0:
            for expense in range(expense_category_count):
                vals.append((0, 0, {'expense_category': expense+1, 'expense_amount': 0}))
                res.update({'expense_ids': vals})

        if income_type_count > 0:
            for income in range(income_type_count):
                vals2.append((0, 0, {'income_type': income+1, 'income_amount': 0}))
                res.update({'income_ids': vals2})
        return res


    @api.model
    def _get_default_Association(self):
        association = self.env['ngo.association'].search(
            [('name', '=', 'الإرشاد')], limit=1)
        if association:
            self.association_id = association.id
            return association.id

    @api.model
    def _get_default_application_type(self):
        app_type = self.env['ngo.application.type'].search(
            [('name', '=', 'بيروت')], limit=1)
        if app_type:
            self.application_type_id = app_type.id
            return app_type.id
            # app_prefix=app_type.prefix

        # if app_prefix:
        # sequence = self.env['ir.sequence'].search([('code','=','ngo.beneficiary.application.'+app_prefix)])
        # else:
        # sequence = self.env['ir.sequence'].search([('code','=','ngo.beneficiary.application')])
        # next= sequence.get_next_char(sequence.number_next_actual)
        # return next

    ##### BEGIN WORKFLOW DETAILS #####
    net_values = fields.Monetary(string='NET VALUE', compute="_compute_value", readonly="1")
    currency_id = fields.Many2one('res.currency', string=_("Currency"))
    code = fields.Char('Code', size=32, required=True,
                       track_visibility='onchange', copy=False ,store=True, default= lambda self: self.env['ir.sequence'].next_by_code('ngo.beneficiary.application'))

    name = fields.Char(string=_("Application name"),compute="_compute_application_name" ,store=True)

    @api.depends('first_beneficiary_name','first_beneficiary_Fathername','first_beneficiary_Lastname')
    def _compute_application_name(self):
        for record in self:
            if record.first_beneficiary_name and record.first_beneficiary_Fathername and record.first_beneficiary_Lastname:
                record.name = f"{record.first_beneficiary_name} {record.first_beneficiary_Fathername} {record.first_beneficiary_Lastname.name}"
            else:
                record.name = " "

    application_type_id = fields.Many2one('ngo.application.type', string=_(
        u"Application Type"), default=_get_default_application_type)
    decision_id = fields.Many2one('ngo.application.decision.list', string=_(
        u"Application Decision"), track_visibility='onchange')
    state = fields.Selection(string=_(u"Application State"), selection=[('draft', _(u'Draft')), ('managerapprove', _(
        u'Manager Approve')), ('review', _(u'Review'))], track_visibility='onchange', default='draft')
    application_date = fields.Date(index=True, default=datetime.today())
    registration_number = fields.Char(string=_(u"Registration Number"), track_visibility='onchange')
    registration_place = fields.Many2one('ngo.kadaa', string=_("Registration Place"), track_visibility='always')
    computed_reg_nb = fields.Char(compute='duplicate_registration_number')
    computed_reg_place = fields.Char(compute='duplicate_registration_number')
    can_edit = fields.Boolean()

    def check_write(self):
        current_user = self.env['res.users'].browse(self.env.uid)
        if current_user.has_group('ngo_edm.ngo_manager'):
            self.can_edit = True
        else:
            self.can_edit = False



    @api.depends('registration_number', 'beneficiary_ids.nationality_id', 'registration_place')
    def duplicate_registration_number(self):
        for record in self:
            if len(record.beneficiary_ids) < 0:
                record.computed_reg_nb = False
                record.computed_reg_place = False
            else:
                # if record.beneficiary_ids.nationality_id.name == 'lebabon' or record.beneficiary_ids.nationality_id.name == 'Syria' or record.beneficiary_ids.nationality_id.name == 'State of Palestine':
                application_duplicate_code = record.env['ngo.beneficiary.application'].search([('registration_number','=',record.registration_number),('code','!=',record.code)])
                if application_duplicate_code:
                    application_duplicate_code_list = []
                    application_duplicate_place_list = []
                    for applicationCode in application_duplicate_code:
                        application_duplicate_code_list.append(applicationCode.code)
                        application_duplicate_place_list.append(applicationCode.registration_place.name)
                        if False in application_duplicate_place_list:
                            application_duplicate_place_list.remove(False)
                    record.computed_reg_nb = ', '.join(str(e) for e in application_duplicate_code_list)
                    record.computed_reg_place = ', '.join(str(e) for e in application_duplicate_place_list)
                    if len(record.computed_reg_place) == 0:
                        record.computed_reg_place = False
                else:
                    record.computed_reg_nb = False
                    record.computed_reg_place = False



    application_class = fields.One2many('ngo.application.class','reverse_id', string="Application class list", required=True)
    number_of_benef = fields.Char(string="Nb Of Beneficiaries", compute="family_member_count", store=True)
    guide_id = fields.Many2one('ngo.guide', string=_(u"Guide"), required=True , default= lambda self: self.env.user.guide.id)
    partner_id = fields.Many2one('res.partner', string=_(u"Partner related"))
    reference = fields.Char(string=_(u"Reference"))
    application_revision_ids = fields.One2many(
        'ngo.application.revision', 'application_id')
    beneficiary_name = fields.Char(string=_(u"Beneficiary Name"))
    reasons_for_help = fields.Selection(string=_(u"reasons for help"),
                                        selection=[('widow', _(u'widow')), ('divorced', _(u'divorced')),
                                                   ('special_needs', _(u'special needs')),
                                                   ('education', _(u'education')), ('schoolarship', _(
                                                u'schoolarship')), ('job_review', _(u'job review')),
                                                   ('voluneteer', _(u'voluneteer')),
                                                   ('acc_voc_training', _(u'accelerated vocational training'))],
                                        readonly=False)
    is_rejected = fields.Boolean(string=_(u"Rejected"), default=False)
    # date_created = fields.Date(string=_(u"Date"),default=fields.Date.today)
    notes = fields.Text(String=_(u"Additional notes"))
    user_id = fields.Many2one(
        'res.users', default=lambda self: self.env.user, readonly=True, string=_(u"Created By"))
    approved_by_id = fields.Many2one(
        'res.users', string=_(u"Approved By"), readonly=True)
    beneficiary_id = fields.Many2one('ngo.beneficiary', string=_(u"Beneficiary"))
    identity_no = fields.Char(string=_("Identity Number", related='beneficiary_id.identity_no'))

    beneficiary_ids = fields.One2many('ngo.beneficiary', 'application_id', string=_(u"Application Members"))

    computed_beneficiary_fields = fields.Many2one('ngo.beneficiary', store=True, compute='get_computed_benef_fields')


    @api.depends('beneficiary_ids')
    def get_computed_benef_fields(self):
        for rec in self:
            if len(rec.beneficiary_ids) > 0:
                for line in rec.beneficiary_ids:
                    rec.computed_beneficiary_fields = line
                    break
            else:
                rec.computed_beneficiary_fields = False



    ##### BEGIN ADDRESS DETAILS #####
    country_id = fields.Many2one('res.country', string=_("Country"))
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
    rooms_count = fields.Integer(string=_(u"Rooms Count"))
    residence_description_id = fields.Many2one(
        'ngo.residence.description', string=_(u"Residence Description"))
    residence_type_id = fields.Many2one(
        'ngo.residence.type', string=_(u"Residence Type"))
    residence_state_id = fields.Many2one(
        'ngo.residence.state', string=_(u"Residence State"))
    electricity_meter_number = fields.Char(
        string=_(u"Electricity Meter Number"), size=13)
    ##### END ADDRESS DETAILS #####

    ##### BEGIN FAMILY DETAILS #####
    house_loan_ids = fields.One2many(
        'ngo.beneficiary.loan', 'application_id', string=_(u"House Loans"))
    house_asset_ids = fields.One2many(
        'ngo.beneficiary.house.asset', 'application_id', string=_(u"House Assets"))
    property_ids = fields.One2many(
        'ngo.beneficiary.property', 'application_id', string=_(u"Family Property"))
    expense_ids = fields.One2many(
        'ngo.beneficiary.expense', 'application_id', string=_(u"Expenses"))
    income_ids = fields.One2many(
        'ngo.beneficiary.income', 'application_id', string=_(u"Income"))

    ##### END FAMILY DETAILS #####
    # file_no=fields.Char(string=_(u"File Number"))
    first_beneficiary_id = fields.One2many('ngo.beneficiary', 'application_id', domain=[
        ('is_first_beneficiary', '=', True)])

    second_beneficiary_id = fields.One2many('ngo.beneficiary', 'application_id', domain=[
        ('is_second_beneficiary', '=', True)])

    # first_beneficiary_name = fields.Char(related='first_beneficiary_id.name', string=_(
    #     u"First Beneficiary"), store=True, readonly=True)

    first_beneficiary_name = fields.Char(string=_(u"First Name"), required=True)
    first_beneficiary_Fathername = fields.Char(string=_(u"Father Name"), required=True)
    first_beneficiary_Lastname = fields.Many2one('partner.family.name', string=_(u"Last Name"), required=True)
    first_beneficiary_nationality = fields.Many2one('res.country', string=_("Nationality"), required=True)
    first_beneficiary_mobile = fields.Char(string=_("Mobile"))
    first_beneficiary_identity_no = fields.Char(string=_("Identity Number"), required=True)
    first_beneficiary_mothername = fields.Char(string=_(u"Mother Name"))
    first_beneficiary_dob = fields.Date(string=_(u"Date of Birth"))
    first_beneficiary_marital_status = fields.Selection( string=_(u"Marital Status"),
                                                         selection=[('single', _(u'Single')),
                                                                    ('married', _(u'Married')),
                                                                    ('widow', _(u'Widow')),
                                                                    ('divorced', _(u'Divorced')),
                                                                    ('seperated', _(u'Separated')),
                                                                    ('multiplemarriages', _(u'Multiple Marriages')),
                                                                    ('engaged', _(u'Engaged')),
                                                                    ('undefined', _(u'Undefined'))])

    @api.onchange('first_beneficiary_name', 'first_beneficiary_Lastname', 'first_beneficiary_nationality',
                  'first_beneficiary_mobile', 'first_beneficiary_identity_no','first_beneficiary_Fathername','registration_number',
                  'registration_place','first_beneficiary_mothername','first_beneficiary_dob','first_beneficiary_marital_status')
    def onchange_create_record(self): # change the first beneficiary data
        if len(self.beneficiary_ids) == 0:
            self.update({
                'beneficiary_ids': [(0, 0, {'first_name': self.first_beneficiary_name, 'is_first_beneficiary': True})]
            })
        else:
            self.update({
                'beneficiary_ids': [(1, self.beneficiary_ids[0].id, {'first_name': self.first_beneficiary_name}),
                                    (1, self.beneficiary_ids[0].id, {'father_name': self.first_beneficiary_Fathername}),
                                    (1, self.beneficiary_ids[0].id, {'family_name': self.first_beneficiary_Lastname}),
                                    (1, self.beneficiary_ids[0].id, {'nationality_id': self.first_beneficiary_nationality.id}),
                                    (1, self.beneficiary_ids[0].id, {'mobile': self.first_beneficiary_mobile}),
                                    (1, self.beneficiary_ids[0].id, {'identity_no': self.first_beneficiary_identity_no}),
                                    (1, self.beneficiary_ids[0].id, {'registration_number': self.registration_number}),
                                    (1, self.beneficiary_ids[0].id, {'registration_place': self.registration_place}),
                                    (1, self.beneficiary_ids[0].id, {'mother_name': self.first_beneficiary_mothername}),
                                    (1, self.beneficiary_ids[0].id, {'birth_date': self.first_beneficiary_dob}),
                                    (1, self.beneficiary_ids[0].id, {'marital_status': self.first_beneficiary_marital_status})
                                    ]})

    def create_members(self):
        applications_withno_beneficiary = self.env['ngo.beneficiary.application'].search([('beneficiary_ids','=',False)])

        for rec in applications_withno_beneficiary:
            rec.update({
                'beneficiary_ids': [(0, 0, {'first_name': rec.first_beneficiary_name,
                                            'father_name': rec.first_beneficiary_Fathername,
                                            'family_name': rec.first_beneficiary_Lastname.id,
                                            'nationality_id':rec.first_beneficiary_nationality.id,
                                            'mobile':rec.first_beneficiary_mobile,
                                            'identity_no':rec.first_beneficiary_identity_no,
                                            'registration_number':rec.registration_number,
                                            'registration_place':rec.registration_place.id,
                                            'mother_name':rec.first_beneficiary_mothername,
                                            'birth_date':rec.first_beneficiary_dob,
                                            'marital_status':rec.first_beneficiary_marital_status,
                                            'is_first_beneficiary':True
                                            })]
            })

    @api.onchange('beneficiary_ids')
    def _onchange_update_record(self):
        for rec in self:
            if len(rec.beneficiary_ids) > 0:
                rec.first_beneficiary_name = rec.beneficiary_ids[0].first_name
                rec.first_beneficiary_Fathername = rec.beneficiary_ids[0].father_name
                rec.first_beneficiary_Lastname = rec.beneficiary_ids[0].family_name
                rec.first_beneficiary_nationality = rec.beneficiary_ids[0].nationality_id
                rec.first_beneficiary_mobile = rec.beneficiary_ids[0].mobile
                rec.first_beneficiary_identity_no = rec.beneficiary_ids[0].identity_no
                rec.registration_number = rec.beneficiary_ids[0].registration_number
                rec.registration_place = rec.beneficiary_ids[0].registration_place
                rec.first_beneficiary_mothername = rec.beneficiary_ids[0].mother_name
                rec.first_beneficiary_dob = rec.beneficiary_ids[0].birth_date
                rec.first_beneficiary_marital_status = rec.beneficiary_ids[0].marital_status


    second_beneficiary_name = fields.Char(related='second_beneficiary_id.name', string=_(
        u"Second Beneficiary"), store=True, readonly=True)
    family_number_reference = fields.Char(string=_("Family Number Reference"))
    phone = fields.Char(string=_("Phone"), track_visibility='always')
    address_checked = fields.Boolean(
        string=_(u"Address Checked"), default=False)
    street_number = fields.Char(string=_("Street Number"))
    neighborhood = fields.Many2one(
        'ngo.neighborhood', string=_("Neighborhood"))

    building_number = fields.Char(string=_("Building Number"))
    mohafaza = fields.Many2one('ngo.mohafaza', string=_("Mohafaza"))
    kadaa = fields.Many2one('ngo.kadaa', string=_("Kadaa"))
    appartment = fields.Char(string=_("Appartment"))
    address_remark = fields.Char(string=_("Address Remark"))
    date_localization = fields.Date(
        string=_("Location Registration Date"), default=datetime.today())
    application_latitude = fields.Float(string=_("Geo Latitude"), digits=(16, 5))
    application_longitude = fields.Float(
        string=_("Geo Longitude"), digits=(16, 5))
    last_revision_date = fields.Date(
        string=_("Last Revision Date"), compute='get_last_revision_date')
    prefix = fields.Char('Prefix', size=20)

    # prefix = fields.Char('Prefix', size=20,compute='_compute_application_prefix', store=True)
    distribution_ids = fields.One2many(
        'ngo.distribution.line',
        'application_id',
        string=_("Distributions"),
        readonly=True
    )
    distribution_count = fields.Integer(
        compute='_compute_distribution_count',
        string=_("# of Distributions"),
        readonly=True
    )
    beneficiary_count = fields.Integer(
        compute='_compute_beneficiary_count',
        string=_("Beneficiary Count"),
        readonly=True,
        store=True
    )

    archive_document_number = fields.Char(
        string='Document Number',
    )

    beneficiaries_phones = fields.Char(
        string='Beneficiaries Phones', compute="get_benficiaries_phone",
    )

    # decision_date = fields.Date(
    #     string='Decision Date',
    #     default=fields.Date.context_today,
    # )

    request_ids = fields.One2many(
        'ngo.beneficiary.request', 'application_id', string=_(u"House Assets"))

    like_share_data_with_other_associations = fields.Boolean(
        string=_(u"like to share my data with Other Associations"), )

    association_id = fields.Many2one(
        'ngo.association', string=_(u"Association"), default=_get_default_Association)

    association_ids = fields.One2many(
        'ngo.application.association', 'application_id', string=_(u"Application Associations"))

    _sql_constraints = [('code_unique', 'unique(code)',
                         _('Application Code already exists!'))]

    # @api.constrains('phone')
    # def check_number(self):
    #     for rec in self:
    #         if rec.phone:
    #             number = self.env['ngo.beneficiary.application'].search([('phone', '=', rec.phone), ('id', '!=', rec.id)])
    #             if number:
    #                 raise ValidationError(_("Phone number %s already exist" % rec.phone))

    @api.depends('beneficiary_ids')
    def family_member_count(self):
        for rec in self:
            rec.number_of_benef = len(rec.beneficiary_ids)
        return rec.number_of_benef

    @api.depends('income_ids', 'expense_ids')
    def _compute_value(self):
        sum = 0
        for rec in self:
            for record in rec.income_ids:
                sum = sum + record.income_amount
            for record in rec.expense_ids:
                sum = sum - record.expense_amount

            rec.net_values = sum
            return rec.net_values

    @api.onchange('registration_number')
    def _change_registration_number(self):
        # benefeciaries = self.env['ngo.beneficiary'].search([('application_id', '=', self.id)])
        for benefeciary in self.beneficiary_ids:
            benefeciary.registration_number = self.registration_number

    @api.onchange('registration_place')
    def _change_registration_place(self):
        # benefeciaries = self.env['ngo.beneficiary'].search([('application_id', '=', self.id)])
        for benefeciary in self.beneficiary_ids:
            benefeciary.registration_place = self.registration_place

    @api.onchange('decision_id')
    def _change_decision(self):
        decision = self.env['ngo.application.revision'].search(
            [('application_id', '=', self.id), ('revision_decision_no', '=', self.decision_id.id)])
        decisionexists = False
        if decision:
            for dec in decision:
                if dec.revision_decision_no == self.decision_id.id:
                    decisionexists = True
                    break
        if decisionexists == False:
            revision_object = self.env['ngo.application.revision']
            vals = {
                'application_id': self.id,
                'revision_decision_no': self.decision_id.id
            }
            revision_created = revision_object.create(vals)

    @api.onchange('association_id')
    def _compute_application_prefix(self):
        # The current user may not have access rights for donations
        # raise UserError("1")
        for application in self:
            prefix = ''
            if application.association_id:
                # raise UserError(application.application_type_id.prefix)
                app_prefix = application.association_id.prefix
            else:
                app_prefix = False

            if app_prefix:
                # sequence = application.env['ir.sequence'].search([('code','=','ngo.beneficiary.application.'+app_prefix)])
                prefix = app_prefix
            # else:
            # sequence = application.env['ir.sequence'].search([('code','=','ngo.beneficiary.application')])
            # next= sequence.get_next_char(sequence.number_next_actual)
            application.prefix = prefix
            sequence = False
            if prefix:
                sequence = self.env['ir.sequence'].search(
                    [('code', '=', 'ngo.beneficiary.application.' + prefix)])
                sequence_code = 'ngo.beneficiary.application.' + prefix
            else:
                sequence = self.env['ir.sequence'].search(
                    [('code', '=', 'ngo.beneficiary.application')])
                sequence_code = 'ngo.beneficiary.application'

            next = sequence.get_next_char(sequence.number_next_actual)

            while self.check_applicaton_duplication(next):
                next = self.env['ir.sequence'].next_by_code(sequence_code)


    # @api.onchange('name','code', 'address')
    # def _compute_application_prefix(self):

    @api.depends('distribution_ids.partner_id')
    def _compute_distribution_count(self):
        # The current user may not have access rights for donations
        for application in self:
            try:
                application.distribution_count = len(
                    application.distribution_ids)
            except Exception:
                application.distribution_count = 0

    @api.depends('beneficiary_ids')
    def _compute_beneficiary_count(self):
        # The current user may not have access rights for donations
        for application in self:
            try:
                application.beneficiary_count = len(
                    application.beneficiary_ids)
            except Exception:
                application.beneficiary_count = 0

    @api.depends('application_revision_ids', 'application_revision_ids.revision_date')
    def get_last_revision_date(self):
        if len(self.application_revision_ids) != 0:
            last_date = max(
                d.revision_date for d in self.application_revision_ids)
            self.last_revision_date = last_date
        else:
            self.last_revision_date = None

    @api.depends('beneficiary_ids', 'beneficiary_ids.phone')
    def get_benficiaries_phone(self):
        phones = ""
        if len(self.beneficiary_ids) != 0:
            for bf in self.beneficiary_ids:
                if bf.phone != False:
                    phones = phones + " - " + bf.phone
                if bf.mobile != False:
                    phones = phones + " - " + bf.mobile
        self.beneficiaries_phones = phones

    def action_draft(self):
        # self.state = 'draft'
        # self.state = 'review'
        return self.write({'state': 'draft','approved_by_id':False})

    def action_review(self):
        # self.state = 'review'
        self.ensure_one()
        for rec in self:
            try:
                # self.add_follower(approver.id)
                # self._message_auto_subscribe_notify(
                # [rec.user_id.partner_id.id],
                # template='mail.message_user_assigned')
                rec.message_post(body="Manager Notification", message_type="notification",
                                 subtype="mail.mt_comment", partner_ids=[rec.user_id.partner_id.id])
            finally:
                return rec.write({'state': 'review'})

        # rec.send_email_review()

    # def action_reject(self):
    # self.state = 'reject'
    # is_rejected = True

    def action_approved(self):
        self.approved_by_id = self._uid
        return self.write({'state': 'managerapprove'})

        # self.create_application_as_beneficiary()
        # self.create_application_as_partner()
        # self.send_email_to_group_workflow_admin_2()

    def send_email_review(self):
        # group = self.env['res.groups'].search([('name', '=', 'Test4 / Workflow Admin')])
        self.ensure_one()
        group = self.env['res.groups'].search([('name', '=', 'Settings')])

        recipient_partners = []
        for recipient in group.users:
            recipient_partners.append(
                (4, recipient.partner_id.id)
            )
        for rec in self:
            mail_details = {'subject': "notification about review for partner creation",
                            'body': "<p>Partner needs to be reviewed from the application:" + rec.name + "</p>"
                                    + "<p>User created the application:" + rec.user_id.name,
                            'partner_ids': recipient_partners
                            }

            mail = self.env['mail.thread']
            mail.message_post(type="notification",
                              subtype="mt_comment", **mail_details)
            # THIS TO POST IT IN THE CHATTER BOX
            self.message_post(type="notification",
                              subtype="mt_comment", **mail_details)

    def send_email_to_group_workflow_admin_2(self):

        group = self.env['res.groups'].search(
            [('name', '=', 'Test4 / Workflow Admin')])
        recipient_partners = []
        for recipient in group.users:
            recipient_partners.append(
                (4, recipient.partner_id.id)
            )
        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')

        url_link = base_url + "/" + "web?#" + "id=" + \
                   str(self.partner_id.id) + "&view_type=form&model=res.partner"

        string_button = self._create_button_email(url_link, "View Partner")

        subject = "Notification about partner creation"
        body = "<p>Partner approved</p><p>this email sent from python code</p>" + "<p>=====</p><p>Details:</p><p>Application type: " + self.application_type + "</p><p>Partner name:" + self.partner_id.name + \
               "</p>" + "<p>User created the application:" + self.user_id.name + "</p>" + "<p>User approved the application:" + \
               self.approved_by_id.name + "</p>" + "<p>" + string_button + "</p>" + "<p>=====</p>"

        mail_details = self._fill_email(subject, body)
        mail_details['partner_ids'] = recipient_partners

        mail = self.env['mail.thread']
        mail.message_post(type="notification",
                          subtype="mt_comment", **mail_details)
        self.message_post(type="notification",
                          subtype="mt_comment", **mail_details)

    def _create_button_email(self, url_link, button_string):
        string_button = "<a href=\"" + url_link + "\" style=\"padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; border-color:#875A7B; text-decoration: none; display: inline-block; margin-bottom: 0px; font-weight: 400; text-align: center; vertical-align: middle; cursor: pointer; white-space: nowrap; background-image: none; background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px\">" + button_string + "</a>"
        return string_button

    def _fill_email(self, subject, body):
        mail_details = {'subject': subject, 'body': body}
        return mail_details

    def create_application_as_beneficiary(self):
        beneficiary_object = self.env['ngo.beneficiary']
        vals = {'code': self.code, 'name': self.beneficiary_name, 'is_responsible': self.is_responsible,
                'gender': self.gender, 'phone': self.phone, 'mobile': self.mobile, 'notes': self.notes}
        beneficiary_approved = beneficiary_object.create(vals)
        self.beneficiary_id = beneficiary_approved
        self.beneficiary_id.main_application_id = self.id

    def create_application_as_partner(self):
        partner_object = self.env['res.partner']
        vals = {
            'name': self.beneficiary_name,
            'phone': self.phone, 'mobile': self.mobile, 'notes': self.notes, 'is_beneficiary': True
        }
        partner_created = partner_object.create(vals)

        self.beneficiary_id.partner_id = partner_created

    def check_applicaton_duplication(self, code):
        exist = self.env['ngo.beneficiary.application'].search([('code', '=', code)])
        if exist:
            ret = True
        else:
            ret = False
        return ret

    def write(self, values):
        res = super(BeneficiaryApplication, self).write(values)
        if len(self.application_class) == 0:
            raise ValidationError("Application class is required")
        if self.partner_id:
            partnerrecords = self.env['res.partner'].search(
                [('id', '=', self.partner_id.id)])
            vals = {'code': self.code, 'name': self.name, 'region': self.region, 'near': self.near,
                    'building': self.building, 'floor': self.floor,
                    'mohafaza': self.mohafaza, 'kadaa': self.kadaa, 'appartment': self.appartment,
                    'neighborhood': self.neighborhood, 'building_number': self.building_number}

            for partnerrecord in partnerrecords:
                if partnerrecord.id == self.partner_id.id:
                    partnerrecord.write(vals)

        return res

    # @api.model
    # def create(self, vals):
    #     res = super(BeneficiaryApplication, self).create(vals)
    #     if vals:
    #         message = "Changes info"
    #         res.application_class.message_post(message)
    #         return res

    @api.model
    def create(self, vals):
        rec = super(BeneficiaryApplication, self).create(vals)
        sequence_code = 'ngo.beneficiary.application'
        partnervals = []
        if len(vals.get('application_class')) == 0:
            raise UserError(_("You can't create application without application class"))
        else:
            if vals.get('prefix', '') != False:
                sequence_code = 'ngo.beneficiary.application.' + vals.get('prefix', '')
            else:
                sequence_code = 'ngo.beneficiary.application'
            sequence = False
            if vals['state'] == 'draft':
                sequence = self.env['ir.sequence'].search(
                    [('code', '=', sequence_code)])
            if sequence:
                if vals['code'] == sequence.get_next_char(sequence.number_next_actual):
                    vals['code'] = self.env['ir.sequence'].next_by_code(sequence_code)

            if self.region:
                vals['region'] = self.region
                partnervals['region'] = self.region
            if self.near:
                vals['near'] = self.near
                partnervals['near'] = self.near
            if self.building:
                vals['building'] = self.building
                partnervals['building'] = self.building
            if self.floor:
                vals['floor'] = self.floor
                partnervals['floor'] = self.floor
            if self.mohafaza:
                vals['mohafaza'] = self.mohafaza
                partnervals['mohafaza'] = self.mohafaza
            if self.kadaa:
                vals['kadaa'] = self.kadaa
                partnervals['kadaa'] = self.kadaa
            if self.appartment:
                vals['appartment'] = self.appartment
                partnervals['appartment'] = self.appartment
            if self.neighborhood:
                vals['neighborhood'] = self.neighborhood
                partnervals['neighborhood'] = self.neighborhood
            if self.building_number:
                vals['building_number'] = self.building_number
                partnervals['building_number'] = self.building_number

                partnervals['is_application'] = True

            if vals:
                rec.sudo().message_post(
                    body=_(f"Application class is changed"),

                    message_type='notification',
                    subtype_xmlid="mail.mt_comment",
                )
            # if self.beneficiary_name:
            #     vals['name'] =self.beneficiary_name

            # vals['name'] = 'Application ' + vals['code']
            # str(sequence.number_next_actual)

            # hajjar 220601: partner_ids must be concifgured
            # check with ahmad barazi concerning message_post
            # rec.message_post(body="Test Message",  message_type="email",
            #                  subtype="mail.mt_comment", partner_ids=[1])
            # vals['is_application'] = True

            partner_id = self.env['res.partner'].create(partnervals)

            rec.partner_id = partner_id.id
            # rec.code = rec.id
            return rec


class BeneficiaryApplicationRevision(models.Model):
    _name = 'ngo.application.revision'
    # _inherit = 'mail.thread'
    _description = "Beneficiary Application Revision"

    ##### BEGIN WORKFLOW DETAILS #####
    application_revision_no = fields.Integer(
        string=_(u"Revision Number"))  # THIS SHOULD BE AUTOGENERATED
    application_id = fields.Many2one(
        'ngo.beneficiary.application', string=_(u"Beneficiary Application"))
    revision_decision_no = fields.Many2one(
        'ngo.application.decision.list', string=_(u"Application Decision"))
    # state = fields.Selection(string=_(u"Application State"), selection=[('draft',_(u'Draft')),('review',_(u'Review')),('reject',_(u'Rejected')),('approved',_(u'Approved'))],default='draft')

    revision_date = fields.Date(index=True, default=fields.Date.context_today)
    application_guide_id = fields.Many2one('ngo.guide', string=_(u"Guide"), )
    renewal_reason = fields.Char('Renewal Reason')
    required_docs = fields.Many2many(
        'ngo.beneficiary.document', string=_(u"Required Documents"))
    reviewed_by_id = fields.Many2one('res.users', string=_(u"Reviewed By"))
    revision_remark = fields.Char('Remark')

    @api.onchange('application_id')
    def onchange_application_id(self):
        assigned_to = None
        if self.application_id:
            self.application_guide_id = self.application_id.guide_id
        else:
            self.application_guide_id = None

            # employee = self.env['hr.employee'].search([('work_email', '=', self.requested_by.email)])
            # if(len(employee) > 0):
            # if(employee[0].department_id and employee[0].department_id.manager_id):
            # assigned_to = employee[0].department_id.manager_id.user_id

        # self.assigned_to =  assigned_to


class BeneficiaryLoan(models.Model):
    _name = 'ngo.beneficiary.loan'
    _description = "Beneficiary House Loan"

    beneficiary_id = fields.Many2one(
        'ngo.beneficiary', string=_(u"Beneficiary"))
    application_id = fields.Many2one(
        'ngo.beneficiary.application', string=_(u"Beneficiary Application"))

    loan_type = fields.Many2one('ngo.loan.type', string=_("Loan Type"))
    loan_amount = fields.Monetary(string=_("Loan Amount"))
    currency_id = fields.Many2one('res.currency', string=_("Currency"))
    start_date = fields.Date(string=_("Start Date"), default=datetime.today())
    bank = fields.Many2one('res.bank', string=_(
        u"Bank Name"))  # THIS SHOULD BE AUTOGENERATED
    payment_frequency = fields.Selection(string=_(u"Payment Frequency"),
                                         selection=[('regular', _(u'Regular')), ('irregular', _(u'Irregular')),
                                                    ('stopped', _(u'Stopped'))])
    stop_date = fields.Date(_(u'Stop Date'))
    stop_reason = fields.Char(string=_(u"Stop Reason"))

    _sql_constraints = [
        ('date_check', "CHECK ( (start_date <= stop_date))",
         "The stop date must be greater than the start date in loan info.")
    ]


class BeneficiaryHouseAsset(models.Model):
    _name = 'ngo.beneficiary.house.asset'
    _description = "Beneficiary House Asset"

    beneficiary_id = fields.Many2one(
        'ngo.beneficiary', string=_(u"Beneficiary"))
    application_id = fields.Many2one(
        'ngo.beneficiary.application', string=_(u"Beneficiary Application"))
    asset_type = fields.Many2one('ngo.asset.type', string=_("Asset Type"))
    asset_count = fields.Integer(string=_("Asset Count"))
    asset_kind = fields.Char(string=_("Asset Kind"))
    asset_state = fields.Selection(string=_("Asset State"),
                                   selection=[('bad', _(u'Bad')), ('fair', _(u'Fair')), ('good', _(u'Good')),
                                              ('vgood', _(u'Very Good')), ('excellent', _(u'Excellent'))])


class BeneficiaryRequest(models.Model):
    _name = 'ngo.beneficiary.request'
    _description = "Beneficiary request"

    application_id = fields.Many2one(
        'ngo.beneficiary.application', string=_(u"Beneficiary Application"))
    asset_type = fields.Many2one('ngo.asset.type', string=_("Asset Type"))
    asset_count = fields.Integer(string=_("Asset Count"))

    request_date = fields.Date(
        string='Request Date',
        default=fields.Date.context_today,
    )

    delivery_date = fields.Date(
        string='Delivery Date',
    )

    remark = fields.Char(string=_("Remark"))

    _sql_constraints = [
        ('date_check', "CHECK ( (request_date <= delivery_date))",
         "The delivery date must be greater than the start date in request info.")
    ]


class BeneficiaryProperty(models.Model):
    _name = 'ngo.beneficiary.property'
    _description = "Beneficiary Property"

    beneficiary_id = fields.Many2one(
        'ngo.beneficiary', string=_(u"Beneficiary"))
    application_id = fields.Many2one(
        'ngo.beneficiary.application', string=_(u"Beneficiary Application"))

    property_type = fields.Selection(string=_("Property Type"),
                                     selection=[('house', _(u'House')), ('car', _(u'Car')),
                                                ('property', _(u'Property')), ('shares', _(u'Shares')),
                                                ('other', _(u'Other'))])
    current_value = fields.Monetary(string=_("Property Value"))
    currency_id = fields.Many2one('res.currency', string=_("Currency"))
    ownership_act = fields.Boolean(string=_("Ownership Act"))
    owner_name = fields.Char(string=_("Owner Name"))
    property_area = fields.Float(string=_("Area(sq.meter)"))
    manufacture_year = fields.Integer(string=_("Manufacture Year"))
    property_kind = fields.Char(string=_("Property Kind"))
    property_usage = fields.Char(string=_("Property Usage"))
    monthly_income = fields.Monetary(string=_("Monthly Income"))
    active = fields.Boolean(string=_("Active"))
    aquisition_date = fields.Date(
        string=_("Aquisition Date"), default=datetime.today())
    stop_date = fields.Date(string=_("Stop Date"))

    _sql_constraints = [
        ('date_check', "CHECK ( (aquisition_date  <= stop_date))",
         "The stop date must be greater than the aquisition date in application properties.")
    ]


class BeneficiaryExpense(models.Model):
    _name = 'ngo.beneficiary.expense'
    _description = "Beneficiary Expense"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    application_id = fields.Many2one(
        'ngo.beneficiary.application', string=_(u"Beneficiary Application"))
    beneficiary_id = fields.Many2one(
        'ngo.beneficiary', string=_(u"Beneficiary"))
    expense_category = fields.Many2one(
        'ngo.expense.category', string=_("Expense Category"))
    expense_subcategory = fields.Many2one(
        'ngo.expense.category', string=_("Expense SubCategory"))
    expense_amount = fields.Float(string=_("Expense Amount"),track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string=_("Currency"))
    active = fields.Boolean(string=_("Active"), default=True)
    stop_date = fields.Date(string=_("Stop Date"))


class BeneficiaryAppRevision(models.Model):
    _name = 'ngo.beneficiary.application.revision'
    # _inherit = 'mail.thread'
    _description = "Beneficiary Application Revision"

    ##### BEGIN WORKFLOW DETAILS #####
    application_revision_no = fields.Integer(
        string=_(u"Revision Number"))  # THIS SHOULD BE AUTOGENERATED
    application_id = fields.Many2one(
        'ngo.beneficiary.application', string=_(u"Beneficiary Application"))
    revision_decision_no = fields.Many2one(
        'ngo.application.decision.list', string=_(u"Application Decision"))
    # state = fields.Selection(string=_(u"Application State"), selection=[('draft',_(u'Draft')),('review',_(u'Review')),('reject',_(u'Rejected')),('approved',_(u'Approved'))],default='draft')

    revision_date = fields.Date(index=True, default=datetime.today())
    application_guide_id = fields.Many2one('ngo.guide', string=_(u"Guide"), )
    renewal_reason = fields.Char('Renewal Reason')
    required_docs = fields.Many2many(
        'ngo.application.docs', string=_(u"Required Documents"))
    reviewed_by_id = fields.Many2one('res.users', string=_(u"Reviewed By"))

    @api.onchange('application_id')
    def onchange_application_id(self):
        assigned_to = None
        if self.application_id:
            self.application_guide_id = self.application_id.guide_id
        else:
            self.application_guide_id = None

            # employee = self.env['hr.employee'].search([('work_email', '=', self.requested_by.email)])
            # if(len(employee) > 0):
            # if(employee[0].department_id and employee[0].department_id.manager_id):
            # assigned_to = employee[0].department_id.manager_id.user_id

        # self.assigned_to =  assigned_to


class ApplicationAssociation(models.Model):
    _name = "ngo.application.association"
    _description = "Application Association"

    application_id = fields.Many2one(
        'ngo.beneficiary.application', string=_(u"Beneficiary Application"))

    association_id = fields.Many2one(
        'ngo.association', string=_(u"Application association"))
    benefits = fields.Boolean(
        string='Benefits',
    )

    remark = fields.Char(
        string='Remark',
    )

    _sql_constraints = [('application_association_unique',
                         'unique (application_id,association_id)', _('Association must be unique for each'))]
