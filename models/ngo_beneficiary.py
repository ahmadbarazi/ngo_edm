# -*- coding: utf-8 -*-
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
from datetime import datetime

from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.modules.module import get_module_resource
from odoo.addons.resource.models.resource_mixin import timezone_datetime
from odoo import fields, models, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta


class NgoStopReason(models.Model):
    _name = 'ngo.stop.reason'
    _description = 'Stop Reason'
    _order = "name"

    name = fields.Char(
        string=_(u"Stop Reason"),
        required=True,
    )
    _sql_constraints = [('name_unique', 'unique(name)', _('Stop Reason already exists!'))]


class PartnerFamilyName(models.Model):
    _name = 'partner.family.name'
    _description = 'Partner Family Name'
    _order = "name"
    1
    name = fields.Char(
        string=_(u"Family Name"),
        required=True,
    )
    _sql_constraints = [('name_unique', 'unique(name)', _('Family Name already exists!'))]


class Beneficiary(models.Model):
    _name = 'ngo.beneficiary'
    _description = "Beneficiary"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin', 'image.mixin']


    def action_open_contract_form(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "ngo.beneficiary",
            "views": [[False, "form"]],
            "res_id": self.id,
        }


    @api.model
    def _default_image(self):
        image_path = get_module_resource('ngo_edm', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    @api.model
    def _get_default_code(self):
        sequence = self.env['ir.sequence'].search([('code', '=', 'ngo.beneficiary')])
        next = sequence.get_next_char(sequence.number_next_actual)
        return next

    @api.depends('family_name')
    @api.model
    def _get_lastname(self):
        # lastname = ''
        for i in self:
            if i.family_name.name:
                i.last_name = i.family_name.name
                # lastname = i.last_name
        # raise UserError(lastname)
        # return lastname

    ##### BEGIN PERSONAL DETAILS #####
    code = fields.Char(string=_(u"Code"), required=True, default=_get_default_code, track_visibility='onchange',
                       copy=False, readonly=True)
    first_name = fields.Char(string=_(u" First Name"), default='')
    father_name = fields.Char(string=_(u"Father Name"), default='')
    mother_name = fields.Char(string=_(u"Mother Name"))
    family_name = fields.Many2one(
        comodel_name='partner.family.name',
        string=_('Family Name'),
        ondelete='restrict',
        index=True,
    )
    last_name = fields.Char(string=_('Last Name'))
    name = fields.Char(string=_(u"Name"))
    registration_number = fields.Char(string=_(u"Registration Number"))
    registration_place = fields.Many2one('ngo.kadaa', string=_("Registration Place"))

    phone = fields.Char(string=_("Phone"))
    mobile = fields.Char(string=_("Mobile"), track_visibility='always', required=True)
    gender = fields.Selection(string=_(u"Gender"),
                              selection=[('male', _(u'Male')), ('female', _(u'Female'))], readonly=False)
    birth_date = fields.Date(_(u'BirthDate'))
    marital_status = fields.Selection(string=_(u"Marital Status"),
                                      selection=[('single', _(u'Single')), ('married', _(u'Married')),
                                                 ('widow', _(u'Widow')),
                                                 ('divorced', _(u'Divorced')), ('seperated', _(u'Separated')),
                                                 ('multiplemarriages', _(u'Multiple Marriages')),
                                                 ('undefined', _(u'Undefined'))], readonly=False)
    family_relationship_id = fields.Many2one('ngo.family.relationship', string=_("Family Relationship"))

    nationality_id = fields.Many2one('res.country', string=_("Nationality"))
    doctrine_id = fields.Many2one('ngo.doctrine', string=_("Doctrine"))
    active = fields.Boolean(String=_(u"Active"), default=True)
    is_stopped = fields.Boolean(String=_(u"Stopped"), default=False)
    stop_date = fields.Date(String=_(u"Stop Date"))
    decease_date = fields.Date(String=_(u"Decease Date"))
    size = fields.Many2many('ngo.size', string=_('Size'))
    is_responsible = fields.Boolean(String=_(u"is family"), default=False)
    is_first_beneficiary = fields.Boolean(String=_(u"First Beneficiary"), default=False)
    is_second_beneficiary = fields.Boolean(String=_(u"Second Beneficiary"), default=False)
    detail = fields.Selection(string=_(u"Type"), selection=[('0', 'عائلة'), ('1', 'فرد')], required=True, default='1')
    image_1920 = fields.Image(default=_default_image)

    ##### END PERSONAL DETAILS #####

    notes = fields.Text(String=_(u"Additional notes"))
    responsible_id = fields.Many2one('ngo.beneficiary', string=_(u"Responsible"),
                                     domain=[('is_responsible', '=', True)])
    # parent_id = fields.Many2one('ngo.beneficiary',string=_(u"Beneficiary Family"),domain=[('is_responsible','=',True)])
    # child_ids = fields.One2many('ngo.beneficiary','parent_id',string=_(u"Children of the responsible"))

    ##### BEGIN SURVEY DETAILS #####
    # main_application_id = fields.Many2one('ngo.beneficiary.application',string=_(u"Applications"))
    application_id = fields.Many2one('ngo.beneficiary.application', string=_(u"Application"))
    street = fields.Char(related='application_id.street', string=_(u"Street"), store=True, readonly=True)
    region = fields.Many2one(related='application_id.region', string=(u"Region"), store=True, readonly=True)
    city = fields.Many2one(related='application_id.city', string=(u"City"), store=True, readonly=True)

    address_remark = fields.Char(
        string='Address Remark',
    )

    ##### END SURVEY DETAILS #####
    guide_id = fields.Many2one('ngo.guide', string=_(u"Guide"))

    ##### BEGIN SPONSOR DETAILS #####
    sponsor_ids = fields.Many2many('ngo.sponsor', string=_(u"Sponsors"))
    ##### END SPONSOR DETAILS #####

    ##### BEGIN PARTNER DETAILS #####
    partner_id = fields.Many2one('res.partner', string=_(u"Partner related"))
    ##### END PARTNER DETAILS #####

    ##### BEGIN FAMILY DETAILS #####
    # house_loan_ids = fields.One2many('ngo.beneficiary.loan','beneficiary_id',string=_(u"House Loans"))
    # house_asset_ids = fields.One2many('ngo.beneficiary.house.asset','beneficiary_id',string=_(u"House Assets"))
    # property_ids = fields.One2many('ngo.beneficiary.property','beneficiary_id',string=_(u"Family Property"))
    # expense_ids = fields.One2many('ngo.beneficiary.expense','beneficiary_id',string=_(u"Expenses"))
    ##### END FAMILY DETAILS #####

    ##### BEGIN MEMBER DETAILS #####
    medical_record_ids = fields.One2many('ngo.beneficiary.medical.record', 'beneficiary_id',
                                         string=_(u"Medical Record"))
    medical_visit_ids = fields.One2many('ngo.beneficiary.medical.visit', 'beneficiary_id', string=_(u"Medical Record"))
    education_record_ids = fields.One2many('ngo.beneficiary.education.record', 'beneficiary_id',
                                           string=_(u"Education Record"))
    job_history_ids = fields.One2many('ngo.beneficiary.employment.history', 'beneficiary_id', string=_(u"Job History"))
    income_ids = fields.One2many('ngo.beneficiary.income', 'beneficiary_id', string=_(u"Income"))
    expense_ids = fields.One2many('ngo.beneficiary.expense', 'beneficiary_id', string=_(u"Expense"))
    hide_benfeciary_expense = fields.Boolean(string="hide", compute="_compute_expense")
    hide_size = fields.Boolean(string="hide", compute="_compute_size")
    ##### END MEMBER DETAILS #####
    identity_no = fields.Char(string=_("Identity Number"), required=True)
    is_student = fields.Boolean(string=_("Is Student"))
    email = fields.Char()
    zakat_fund_number = fields.Char(string=_("Zakat Fund Number"))
    stop_reason = fields.Many2one('ngo.stop.reason', string=_("Stop Reason"))
    family_number_reference = fields.Char(string=_("Family Number Reference"))
    age = fields.Float(string=_(u"Age"), compute='_compute_age', store=True)
    previous_application_id = fields.Many2one('ngo.beneficiary.application', string=_(u"Previous Application"))
    has_illness = fields.Boolean(string=_(u"Has Illness"), compute="get_has_illness", store=True, )
    has_handicap = fields.Boolean(string=_(u"Has Handicap"), compute="get_has_handicap", store=True, )

    # Report_ngo_distribution_food_first_ids = fields.One2many(
    #     'report.ngo_edm.distribution_food_report_view',
    #     'first_beneficiary_id',
    #     string=_(u"distribution food report first"),
    #     states={'done': [('readonly', True)]},
    # )

    # Report_ngo_distribution_food_Second_ids = fields.One2many(
    #     'report.ngo_edm.distribution_food_report_view',
    #     'second_beneficiary_id',
    #     string=_(u"distribution food report second"),
    #     states={'done': [('readonly', True)]},
    # )

    @api.constrains('mobile')
    def check_name(self):
        for rec in self:
            number = self.env['ngo.beneficiary'].search([('mobile', '=', rec.mobile), ('id', '!=', rec.id)])
            if number:
                raise ValidationError(_("number %s is already exist" % rec.mobile))

    @api.constrains('identity_no')
    def check_identity_no(self):
        for rec in self:
            number = self.env['ngo.beneficiary'].search([('identity_no', '=', rec.identity_no), ('id', '!=', rec.id)])
            if number:
                raise ValidationError(_("number %s is already exist" % rec.identity_no))

    @api.depends("hide_benfeciary_expense")
    def _compute_expense(self):
        expense_hide = self.env['ir.config_parameter'].sudo().get_param('ngo_edm.expenses')
        for record in self:
            record.hide_benfeciary_expense = expense_hide

        return record.hide_benfeciary_expense

    @api.depends("hide_size")
    def _compute_size(self):
        size_hide = self.env['ir.config_parameter'].sudo().get_param('ngo_edm.hide_benfeciary_size')
        for record in self:
            record.hide_size = size_hide

        return record.hide_size

    @api.model
    def default_get(self, fields):
        expense_hide = self.env['ir.config_parameter'].sudo().get_param('ngo_edm.expenses')
        size_hide = self.env['ir.config_parameter'].sudo().get_param('ngo_edm.hide_benfeciary_size')
        res = super(Beneficiary, self).default_get(fields)
        res.update({
            'hide_benfeciary_expense': expense_hide,
            'hide_size': size_hide
        })
        return res

    @api.constrains('is_first_beneficiary', 'is_second_beneficiary')
    def _validate_first_second_beneficiary(self):
        if self.is_first_beneficiary == True and self.is_second_beneficiary == True:
            raise ValidationError(_("First Beneficiary must be different from Second Beneficiary!!"))

    @api.onchange('detail')
    def onchange_detail(self):
        # isresponsible = False
        if self.detail == '0':
            self.is_responsible = True
        else:
            self.is_responsible = False
        # self.user_type_id = usertype

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        if self.parent_id:
            self.responsible_id = self.parent_id
        else:
            self.responsible_id = None

    # @api.model_create_multi
    # def create(self, vals_list):
    # name=''
    # for vals in vals_list:
    # if not vals['is_responsible']:
    # name = (str(vals['first_name'] or '') + ' ' +str(vals['father_name'] or '')+ ' ' +str(vals['last_name'] or ''))
    # vals['name'] = name
    # res = super(Beneficiary, self).create(vals_list)
    # return res

    # @api.model_create_multi
    @api.model
    def create(self, vals):
        ### Create beneficiary

        vals['code'] = self.env['ir.sequence'].next_by_code('ngo.beneficiary')
        name = vals['first_name']
        if vals['first_name'] and vals['father_name'] and vals['last_name']:
            name = str(vals['first_name'] or '') + ' ' + str(vals['father_name'] or '') + ' ' + str(
                vals['last_name'] or '')
        elif vals['first_name'] and vals['father_name']:
            name = str(vals['first_name'] or '') + ' ' + str(vals['father_name'] or '')
        elif vals['first_name'] and vals['last_name']:
            name = str(vals['first_name'] or '') + ' ' + str(vals['last_name'] or '')
        else:
            name = str(vals['first_name'] or '')

        self.name = name
        vals['name'] = name

        sp = super(Beneficiary, self).create(vals)

        # for vals_list in vals:
        # if vals_list.get('parent_id') and vals_list.get('name') and vals_list.get('is_responsible'):
        # parent_beneficiary = self.env['ngo.beneficiary'].browse(vals_list['parent_id'])
        # partner_id = self.env['res.partner'].create({'parent_id': parent_beneficiary.partner_id.id,
        # 'name': vals_list['name'],
        # 'display_name':vals_list['name'],
        # 'active': True,
        # 'type': 'contact',
        # 'is_company':False,
        # 'is_beneficiary':True,
        # 'is_responsible': vals_list['is_responsible']
        # })

        # beneficiary_application = self.env['ngo.beneficiary.application'].browse(vals['application_id'])
        partner_id = self.env['res.partner'].create({
            'name': vals['name'],
            'display_name': vals['name'],
            'active': True,
            'type': 'contact',
            'is_company': False,
            'is_beneficiary': True
        })
        sp.partner_id = partner_id.id

        return sp

    @api.onchange('family_name')
    def _onchange_family_name(self):
        for i in self:
            if i.family_name.name:
                i.last_name = i.family_name.name
                # raise UserError(i.last_name)
            if i.first_name and i.father_name and i.family_name:
                i.name = (i.first_name + ' ' + i.father_name + ' ' + i.family_name.name)
            elif i.first_name and i.family_name:
                i.name = i.first_name + ' ' + i.family_name.name
            elif i.father_name and i.family_name:
                i.name = i.father_name + ' ' + i.family_name.name
            else:
                i.name = i.family_name.name

    @api.onchange('father_name')
    def _onchange_father_name(self):
        for i in self:
            if i.first_name and i.father_name and i.family_name:
                i.name = (i.first_name + ' ' + i.father_name + ' ' + i.family_name.name)
            elif i.first_name and i.father_name:
                i.name = i.first_name + ' ' + i.father_name
            elif i.father_name and i.family_name:
                i.name = i.father_name + ' ' + i.family_name.name
            else:
                i.name = i.father_name

    @api.onchange('first_name')
    def _onchange_first_name(self):
        for i in self:
            if i.first_name and i.father_name and i.family_name:
                i.name = (i.first_name + ' ' + i.father_name + ' ' + i.family_name.name)
            elif i.first_name and i.father_name:
                i.name = i.first_name + ' ' + i.father_name

            elif i.first_name and i.family_name:
                i.name = i.first_name + ' ' + i.family_name.name
            else:
                i.name = i.first_name

    def write(self, vals):
        res = super(Beneficiary, self).write(vals)
        for beneficiary in self:
            # if not beneficiary.is_responsible:
            if beneficiary.name != (
                    str(beneficiary.first_name or '') + ' ' + str(beneficiary.father_name or '') + ' ' + str(
                    beneficiary.last_name or '')):
                beneficiary.name = (
                            str(beneficiary.first_name or '') + ' ' + str(beneficiary.father_name or '') + ' ' + str(
                        beneficiary.last_name or ''))
        return res

    @api.depends('birth_date', 'decease_date')
    def _compute_age(self):
        for record in self:
            if record.decease_date:
                age = relativedelta(record.decease_date, record.birth_date)
            else:
                age = relativedelta(datetime.now(), record.birth_date)
            record.age = age.years + (age.months / 12)

    @api.depends('medical_record_ids', 'medical_record_ids.illness_type')
    def get_has_illness(self):
        for record in self:
            record.has_illness = False
            for med in record.medical_record_ids:
                if med.illness_type.id:
                    record.has_illness = True
                    break
                else:
                    record.has_illness = False

    @api.depends('medical_record_ids', 'medical_record_ids.handicap_type')
    def get_has_handicap(self):
        for record in self:
            record.has_handicap = False
            for med in record.medical_record_ids:
                if med.handicap_type.id:
                    record.has_handicap = True
                    break
                else:
                    record.has_handicap = False


class BeneficiaryIncome(models.Model):
    _name = 'ngo.beneficiary.income'
    _description = "Beneficiary Income"

    application_id = fields.Many2one('ngo.beneficiary.application', string=_(u"Application"))
    beneficiary_id = fields.Many2one('ngo.beneficiary', string=_(u"Beneficiary"),
                                     domain="[('application_id','=',application_id)]")
    income_type = fields.Many2one('ngo.income.type', string=_("Income Type"))
    income_amount = fields.Monetary(string=_("Income Amount"), tracking=True, track_visibility='onchange')
    association_id = fields.Many2one('ngo.association', string=_("Association"))
    currency_id = fields.Many2one('res.currency', string=_("Currency"))
    sponsor_id = fields.Many2one('ngo.sponsor', string=_("Sponsor"))
    start_date = fields.Date(string=_("Start Date"), default=datetime.today())
    stop_date = fields.Date(string=_("Stop Date"))

    _sql_constraints = [
        ('date_check', "CHECK ((start_date <= stop_date))",
         "The stop date must be greater than the start date in income info.")
    ]

    @api.onchange('beneficiary_id')
    def _onchange_beneficiary_id(self):
        for rec in self:
            if rec.beneficiary_id and not rec.application_id:
                rec.application_id = rec.beneficiary_id.application_id.id


class BeneficiaryMedicalRecord(models.Model):
    _name = 'ngo.beneficiary.medical.record'
    _description = "Beneficiary Medical Record"

    beneficiary_id = fields.Many2one('ngo.beneficiary', string=_("Beneficiary"))
    illness_type = fields.Many2one('ngo.illness.type', string=_("Illness Type"))
    handicap_type = fields.Many2one('ngo.handicap.type', string=_("Handicap Type"))
    start_date = fields.Date(string=_("Start Date"), default=datetime.today())
    # active = fields.Boolean(string=_("Active"),    default=True,    )
    stop_date = fields.Date(string=_("Stop Date"))

    _sql_constraints = [
        ('date_check', "CHECK ( (start_date <= stop_date))",
         "The stop date must be greater than the start date in medical record info.")
    ]


class BeneficiaryMedicalVisit(models.Model):
    _name = 'ngo.beneficiary.medical.visit'
    _description = "Beneficiary Medical Visit"

    beneficiary_id = fields.Many2one('ngo.beneficiary', string=_("Beneficiary"))
    illness_type = fields.Many2one('ngo.illness.type', string=_("Illness Type"))
    handicap_type = fields.Many2one('ngo.handicap.type', string=_("Handicap Type"))
    medicine = fields.Many2many('ngo.medicine', string=_("Medicine"))
    visit_date = fields.Date(string=_("Visit Date"), default=datetime.today())
    next_visit_date = fields.Date(string=_("Next Visit Date"))
    amount_to_pay = fields.Monetary(string=_("Amount To Pay"))
    currency_id = fields.Many2one('res.currency', string=_("Currency"))
    visit_month = fields.Integer(string=_("Visit Month"))
    visit_year = fields.Integer(string=_("Visit Year"))


class BeneficiaryEducationRecord(models.Model):
    _name = 'ngo.beneficiary.education.record'
    _description = "Beneficiary Education Record"

    beneficiary_id = fields.Many2one('ngo.beneficiary', string=_("Beneficiary"))
    academic_year = fields.Integer(string=_("Academic Year"))
    education_institution = fields.Many2one('ngo.education.institution', string=_("Education Institution"))
    education_institution_type = fields.Many2one('ngo.education.institution.type', string=_("Institution Type"))
    is_student = fields.Boolean(string=_("Is Student"))
    education_level = fields.Many2one('ngo.education.level', string=_("Education Level"))
    education_class = fields.Many2one('ngo.education.class', string=_("Class"))


class BeneficiaryEmploymentHistory(models.Model):
    _name = 'ngo.beneficiary.employment.history'
    _description = "Beneficiary Employment History"

    beneficiary_id = fields.Many2one('ngo.beneficiary', string=_("Beneficiary"))
    career = fields.Many2one('ngo.career', string=_("Career"))
    job_title = fields.Many2one('ngo.job.title', string=_("Job Title"))
    job_area = fields.Many2one('ngo.region', string=_("Region"))
    job_type = fields.Many2one('ngo.job.type', string=_("Job Type"))
    job_state = fields.Many2one('ngo.job.state', string=_("Job State"))
    start_date = fields.Date(string=_("Start Date"), default=datetime.today())
    stop_date = fields.Date(string=_("End Date"))
    stop_reason = fields.Char(string=_("Stop Reason"))

    _sql_constraints = [
        ('date_check', "CHECK ( (start_date <= stop_date))",
         "The stop date must be greater than the start date in employment history info.")
    ]
