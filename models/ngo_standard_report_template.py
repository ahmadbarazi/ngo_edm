# -*- coding: utf-8 -*-

from odoo import api, models, fields, _

class NgoFilterTemplate(models.Model):
    _name = 'ngo.filter.template'
    _description = 'NGO Standard Search Template'

    name = fields.Char(default='Standard Filter Template')

class NgoReportTemplate(models.Model):
    _name = 'ngo.report.template'
    _description = 'NGO Standard Search Template'

    name = fields.Char(default='Standard Filter Template')
    company_id = fields.Many2one('res.company', string=_(u"Company"), readonly=True,
                                 default=lambda self: self.env.user.company_id)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id',
                                          string=_(u"Company Currency"), readonly=True,
                                          help='Utility field to express amount currency', store=True)


    guide_ids = fields.Many2many(comodel_name="ngo.guide", string=_(u"Guide"), required=False )
    file_no = fields.Many2one('ngo.beneficiary.application',string=_(u"File Number"))

    decision_ids = fields.Many2many('ngo.application.decision.list',string=_(u"Application Decision"))
    gender = fields.Selection(string=_(u"Gender"), 
        selection=[('male',_(u'Male')),('female',_(u'Female'))],readonly=False)
    size=fields.Many2one('ngo.size',string=_('Size'))
    application_type_ids = fields.Many2many(comodel_name='ngo.application.type',string=_(u"Application Type")) 
    region = fields.Many2one('ngo.region',string=_(u"Region"))
    marital_status=fields.Selection(string=_(u"Marital Status"), 
        selection=[('single',_(u'Single')),('married',_(u'Married')),('widow',_(u'Widow')),
                   ('divorced',_(u'Divorced')),('seperated',_(u'Separated')),
                   ('multiplemarriages',_(u'Multiple Marriages')),('undefined',_(u'Undefined'))],readonly=False)        
    residence_type_id = fields.Many2one('ngo.residence.type',string=_(u"Residence Type"))
    application_date_from = fields.Date(string=_(u"From Date"))
    application_date_to = fields.Date(string=_(u"To Date"))
    beneficiary_ids = fields.One2many(
        comodel_name="wizard.beneficiary.search.line",
        inverse_name="beneficiary_search_id",
        string=_(u"Beneficiary"),
        required=False
    )
    first_name = fields.Char(string=_(u"Name"), default='')
    father_name = fields.Char(string=_(u"Father Name"), default='')
    mother_name = fields.Char(string=_(u"Mother Name"))
    family_name = fields.Many2one(
        comodel_name='partner.family.name',
        string=_('Family Name'),
        index=True,
        )
    mohafaza = fields.Many2one('ngo.mohafaza',string=_("Mohafaza"))
    kadaa = fields.Many2one('ngo.kadaa',string=_("Kadaa"))
    city = fields.Many2one('ngo.city',string=_(u"City"))
    region = fields.Many2one('ngo.region',string=_(u"Region"))
    neighborhood = fields.Many2one('ngo.neighborhood',string=_("Neighborhood"))
    age_from = fields.Float(string=_(u"From Age"))
    age_to = fields.Float(string=_(u"To Age"))

    #for filter template in distribution
    birth_date = fields.Date(_(u'BirthDate'))
    nationality_id = fields.Many2one('res.country',string=_("Nationality"))
    doctrine_id = fields.Many2one('ngo.doctrine',string=_("Doctrine"))
    illness_type = fields.Many2one('ngo.illness.type',string=_("Illness Type"))
    handicap_type = fields.Many2one('ngo.handicap.type',string=_("Handicap Type"))
    medicine = fields.Many2one('ngo.medicine',string=_("Medicine"))

    academic_year = fields.Integer(string=_("Academic Year"))
    education_level = fields.Many2one('ngo.education.level',string=_("Education Level"))
    education_class = fields.Many2one('ngo.education.class',string=_("Class"))

    has_illness = fields.Boolean(string=_(u"Has Illness"))
    has_handicap  = fields.Boolean(string=_(u"Has Handicap"))
    is_student = fields.Boolean(string=_(u"is Student"))
    
    ####################################


    # compact_account = fields.Boolean('Compacte account.', default=False)

    # @api.onchange('account_in_ex_clude_ids')
    # def _onchange_account_in_ex_clude_ids(self):
        # if self.account_in_ex_clude_ids:
            # self.account_methode = 'include'
        # else:
            # self.account_methode = False

    # @api.onchange('ledger_type')
    # def _onchange_ledger_type(self):
        # if self.ledger_type in ('partner', 'journal', 'open', 'aged'):
            # self.compact_account = False
        # if self.ledger_type == 'aged':
            # self.date_from = False
            # self.reconciled = False
        # if self.ledger_type not in ('partner', 'aged',):
            # self.reconciled = True
            # return {'domain': {'account_in_ex_clude_ids': []}}
        # self.account_in_ex_clude_ids = False
        # if self.result_selection == 'supplier':
            # return {'domain': {'account_in_ex_clude_ids': [('type_third_parties', '=', 'supplier')]}}
        # if self.result_selection == 'customer':
            # return {'domain': {'account_in_ex_clude_ids': [('type_third_parties', '=', 'customer')]}}
        # return {'domain': {'account_in_ex_clude_ids': [('type_third_parties', 'in', ('supplier', 'customer'))]}}
