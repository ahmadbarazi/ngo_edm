# -*- coding: utf-8 -*-


import calendar
# import NgoReportTemplate
from datetime import datetime, timedelta
from odoo import api, models, fields, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import AccessError, UserError



FIELDS_TEMPLATE = ['name', 'guide_ids', 'file_no', 'decision_ids', 'gender', 'size',
                   'application_type_ids', 'region', 'marital_status', 'residence_type_id',
                   'application_date_from','application_date_to','mohafaza','kadaa',
                   'family_name','age_from','age_to','city',
                   'birth_date','nationality_id','doctrine_id','illness_type','handicap_type',
                   'medicine','academic_year','education_level','education_class', 'has_illness','has_handicap', 'is_student']


class NgoReportStandardLedgerLines(models.TransientModel):
    _name = 'ngo.report.standard.ledger.line'
    _order = 'id'
    _rec_name = 'move_id'
    _description = 'NGO Standard Seach Line'

    template_id = fields.Many2one('ngo.report.template', 'Template')
    line_type = fields.Selection([('0_init', 'Initial'), ('1_init_line', 'Init Line'),
                                  ('2_line', 'Line'), ('3_compact', 'Compacted'), ('4_total', 'Total'),
                                  ('5_super_total', 'Super Total')], string=_(u"Type"))
    view_type = fields.Selection([('init', 'Init'), ('normal', 'Normal'), ('total', 'Total')])
    partner_id = fields.Many2one('res.partner', 'Partner')
    group_by_key = fields.Char()
    move_id = fields.Many2one('account.move', 'Entrie')
    date = fields.Date()
    date_maturity = fields.Date('Due Date')
    report_object_id = fields.Many2one('ngo.report.standard.ledger.report.object')

    currency_id = fields.Many2one('res.currency')

    company_currency_id = fields.Many2one('res.currency')
    beneficiary_id = fields.Many2one(
        comodel_name="ngo.beneficiary",
        string=_(u"Beneficiary"),
        required=False,
        ondelete="set null",
    )

    beneficiary_code = fields.Char(related='beneficiary_id.code',string=_(u"Beneficiary Code"), store=True, readonly=True)
    beneficiary_name = fields.Char(related='beneficiary_id.name',string=_(u"Beneficiary Name"), store=True, readonly=True)
    first_name = fields.Char(string=_(u"Name"), default='')
    father_name = fields.Char(string=_(u"Father Name"), default='')
    mother_name = fields.Char(string=_(u"Mother Name"))
    family_name = fields.Many2one('partner.family.name',string=_(u"Family Name"))
    age = fields.Float(string=_(u"Age"))
    gender = fields.Selection(string=_(u"Gender"),
        selection=[('male',_(u'Male')),('female',_(u'Female'))],readonly=False)
    marital_status=fields.Selection(string=_(u"Marital Status"),
        selection=[('single',_(u'Single')),('married',_(u'Married')),('widow',_(u'Widow')),
                   ('divorced',_(u'Divorced')),('seperated',_(u'Separated')),
                   ('multiplemarriages',_(u'Multiple Marriages')),('undefined',_(u'Undefined'))],readonly=False)


    application_id = fields.Many2one('ngo.beneficiary.application',string=_(u"Application"))
    application_code = fields.Char(related='beneficiary_id.application_id.code',string=_(u"Application Code"), store=True, readonly=True)

    file_no=fields.Char(string=_(u"File Number"))
    decision_id = fields.Many2one('ngo.application.decision.list',string=_(u"Application Decision"))
    # size=fields.Many2many('ngo.size',string=_('Size'), store=True, readonly=True)
    application_type_id = fields.Many2one('ngo.application.type',string=_(u"Application Type"))
    residence_type_id = fields.Many2one('ngo.residence.type',string=_(u"Residence Type"))
    application_date = fields.Date(related='beneficiary_id.application_id.application_date', store=True, readonly=True)
    guide_id = fields.Many2one('ngo.guide',string=_(u"Guide"))
    mohafaza = fields.Many2one('ngo.mohafaza',string=_("Mohafaza"))
    kadaa = fields.Many2one('ngo.kadaa',string=_("Kadaa"))
    city = fields.Many2one('ngo.city',string=_(u"City"))
    region = fields.Many2one('ngo.region',string=_(u"Region"))
    neighborhood = fields.Many2one('ngo.neighborhood',string=_("Neighborhood"))
    has_illness = fields.Boolean(string=_(u"has Illness"))
    has_handicap  = fields.Boolean(string=_(u"has Handicap"))
    is_student = fields.Boolean(string=_(u"is Student"))


class NgoReportStandardLedger(models.TransientModel):
    _name = 'ngo.report.standard.ledger'
    _description = 'NGO Standard Search Wizard'
 
    name = fields.Char(default='Standard Search')
   
   
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
    template_id = fields.Many2one('ngo.report.template', 'Template')
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

    _sql_constraints = [
            ('date_check', "CHECK ( (application_date_from <= application_date_from))", "The date to must be greater than the date from.")
        ]
    def build_where(self, params):
        where_select = ''
        guide_select = ' 1=1 '
        if self.guide_ids:
            guide_select = """ b.guide_id IN %s"""
            where_select = guide_select
            params.append(tuple(self.guide_ids.ids))

        first_name_select = ' 1=1 '
        if self.first_name:
            first_name_select = """ b.first_name iLIKE %s """
            where_select = where_select + ' AND ' + first_name_select if where_select else first_name_select
            params.append('%'+self.first_name+'%')

        father_name_select = ' 1=1 '
        if self.father_name:
            father_name_select = """ b.father_name iLIKE %s """
            where_select = where_select + ' AND ' + father_name_select if where_select else father_name_select
            params.append('%'+self.father_name+'%')

        mother_name_select = ' 1=1 '
        if self.mother_name:
            mother_name_select = """ b.mother_name iLIKE %s """
            where_select = where_select + ' AND ' + mother_name_select if where_select else mother_name_select
            params.append('%'+self.mother_name+'%')

        family_name_select = ' 1=1 '
        if self.family_name:
            family_name_select = """ b.family_name = %s """
            where_select = where_select + ' AND ' + family_name_select if where_select else family_name_select
            params.append(self.family_name.id)

        gender_select = ' 1=1 '
        if self.gender:
            gender_select = """ b.gender = %s """
            where_select = where_select + ' AND ' + gender_select if where_select else gender_select
            params.append(self.gender)

        marital_select = ' 1=1 '
        if self.marital_status:
            marital_select = """ b.marital_status = %s """
            where_select = where_select + ' AND ' + marital_select if where_select else marital_select
            params.append(self.marital_status)

        age_select = ' 1=1 '
        if (self.age_from or self.age_from==0) and self.age_to:
            age_select = """ b.age >= %s AND b.age <= %s """
            where_select = where_select + ' AND ' + age_select if where_select else age_select
            params.append(self.age_from)
            params.append(self.age_to)

        file_no_select = ' 1=1 '
        # 20200701 Hajjar; Purpose: file_no doesn't exists in application
        # if self.file_no:
        #     file_no_select = """ app.file_no = %s """
        #     where_select = where_select + ' AND ' + file_no_select if where_select else file_no_select
        #     params.append(self.file_no)

        decision_select = ' 1=1 '
        if self.decision_ids:
            decision_select = """ app.decision_id IN %s """
            where_select = where_select + ' AND ' + decision_select if where_select else decision_select
            params.append(tuple(self.decision_ids.ids))

        residence_type_select = ' 1=1 '
        if self.residence_type_id:
            residence_type_select = """ app.residence_type_id IN %s """
            where_select = where_select + ' AND ' + residence_type_select if where_select else residence_type_select
            params.append(tuple(self.residence_type_id.ids))

        application_type_select = ' 1=1 '
        if self.application_type_ids:
            application_type_select = """ app.application_type_id IN %s """
            where_select = where_select + ' AND ' + application_type_select if where_select else application_type_select
            params.append(tuple(self.application_type_ids.ids))

        application_date_select = ' 1=1 '
        if self.application_date_from and self.application_date_to:
            application_date_select = """ app.application_date >= %s AND app.application_date <= %s """
            where_select = where_select + ' AND ' + application_date_select if where_select else application_date_select
            params.append(self.application_date_from)
            params.append(self.application_date_to)

        mohafaza_select = ' 1=1 '
        if self.mohafaza:
            mohafaza_select = """ app.mohafaza = %s """
            where_select = where_select + ' AND ' + mohafaza_select if where_select else mohafaza_select
            params.append(self.mohafaza.id)

        kadaa_select = ' 1=1 '
        if self.kadaa:
            kadaa_select = """ app.kadaa = %s """
            where_select = where_select + ' AND ' + kadaa_select if where_select else kadaa_select
            params.append(self.kadaa.id)

        city_select = ' 1=1 '
        if self.city:
            city_select = """ app.city = %s """
            where_select = where_select + ' AND ' + city_select if where_select else city_select
            params.append(self.city.id)

        region_select = ' 1=1 '
        if self.region:
            region_select = """ app.region = %s """
            where_select = where_select + ' AND ' + region_select if where_select else region_select
            params.append(self.region.id)

        neighborhood_select = ' 1=1 '
        if self.neighborhood:
            neighborhood_select = """ app.kadaa = %s """
            where_select = where_select + ' AND ' + neighborhood_select if where_select else neighborhood_select
            params.append(self.neighborhood.id)


        size_select = ' 1=1 '
        if self.size:
            size_select = """ b.id in (select ngo_beneficiary_id from ngo_beneficiary_ngo_size_rel where ngo_size_id IN %s)  """
            where_select = where_select + ' AND ' + size_select if where_select else size_select
            params.append(tuple(self.size.ids))             

        nationality_id_select = ' 1=1 '
        if self.nationality_id:
            nationality_id_select = """ b.nationality_id IN %s """
            where_select = where_select + ' AND ' + nationality_id_select if where_select else nationality_id_select
            params.append(tuple(self.nationality_id.ids))

        has_illness_select = ' 1=1 '
        if self.has_illness:
            has_illness_select = """ b.has_illness = %s """
            where_select = where_select + ' AND ' + has_illness_select if where_select else has_illness_select
            params.append(self.has_illness)        

        has_handicap_select= ' 1=1 '
        if self.has_handicap:
            has_handicap_select = """ b.has_handicap = %s """
            where_select = where_select + ' AND ' + has_handicap_select if where_select else has_handicap_select
            params.append(self.has_handicap)  

        is_student_select= ' 1=1 '
        if self.is_student:
            is_student_select = """ b.is_student = %s """
            where_select = where_select + ' AND ' + is_student_select if where_select else is_student_select
            params.append(self.is_student)  

        # illness_type_select = ' 1=1 '
        # if self.illness_type:
        #     illness_type_select = """ b.id in (select beneficiary_id from ngo_beneficiary_medical_record where illness_type IN %s) """
        #     where_select = where_select + ' AND ' + illness_type_select if where_select else illness_type_select
        #     params.append(tuple(self.illness_type.ids))            

        # handicap_type_select = ' 1=1 '
        # if self.handicap_type:
        #     handicap_type_select = """ b.id in (select beneficiary_id from ngo_beneficiary_medical_record where handicap_type IN %s) """
        #     where_select = where_select + ' AND ' + handicap_type_select if where_select else handicap_type_select
        #     params.append(tuple(self.handicap_type.ids))  

        # medicine_select = ' 1=1 '
        # if self.medicine:
        #     medicine_select = """ b.id in (select beneficiary_id from ngo_beneficiary_medical_visit_ngo_medicine_rel inner join ngo_beneficiary_medical_visit on id = ngo_beneficiary_medical_visit_id where ngo_medicine_id IN %s) """
        #     where_select = where_select + ' AND ' + medicine_select if where_select else medicine_select
        #     params.append(tuple(self.medicine.ids))

        # academic_year_select = ' 1=1 '
        # if self.academic_year:
        #     academic_year_select = """ b.id in (select beneficiary_id from ngo_beneficiary_education_record where academic_year = %s) """
        #     where_select = where_select + ' AND ' + academic_year_select if where_select else academic_year_select
        #     params.append( self.academic_year)


        # education_level_select = ' 1=1 '
        # if self.education_level:
        #     education_level_select = """ b.id in (select beneficiary_id from ngo_beneficiary_education_record where education_level IN %s) """
        #     where_select = where_select + ' AND ' + education_level_select if where_select else education_level_select
        #     params.append(tuple(self.education_level.ids))


        # education_class_select = ' 1=1 '
        # if self.education_class:
        #     education_class_select = """ b.id in (select beneficiary_id from ngo_beneficiary_education_record where education_class IN %s) """
        #     where_select = where_select + ' AND ' + education_class_select if where_select else education_class_select
        #     params.append(tuple(self.education_class.ids))


        return where_select

    def build_where_beneficiary(self, params):
        where_select = ''
        guide_select = ' 1=1 '
        if self.guide_ids:
            guide_select = """ b.guide_id IN %s"""
            where_select = guide_select
            params.append(tuple(self.guide_ids.ids))

        first_name_select = ' 1=1 '
        if self.first_name:
            first_name_select = """ b.first_name iLIKE %s """
            where_select = where_select + ' AND ' + first_name_select if where_select else first_name_select
            params.append('%'+self.first_name+'%')

        father_name_select = ' 1=1 '
        if self.father_name:
            father_name_select = """ b.father_name iLIKE %s """
            where_select = where_select + ' AND ' + father_name_select if where_select else father_name_select
            params.append('%'+self.father_name+'%')

        mother_name_select = ' 1=1 '
        if self.mother_name:
            mother_name_select = """ b.mother_name iLIKE %s """
            where_select = where_select + ' AND ' + mother_name_select if where_select else mother_name_select
            params.append('%'+self.mother_name+'%')

        family_name_select = ' 1=1 '
        if self.family_name:
            family_name_select = """ b.family_name = %s """
            where_select = where_select + ' AND ' + family_name_select if where_select else family_name_select
            params.append(self.family_name.id)

        gender_select = ' 1=1 '
        if self.gender:
            gender_select = """ b.gender = %s """
            where_select = where_select + ' AND ' + gender_select if where_select else gender_select
            params.append(self.gender)

        marital_select = ' 1=1 '
        if self.marital_status:
            marital_select = """ b.marital_status = %s """
            where_select = where_select + ' AND ' + marital_select if where_select else marital_select
            params.append(self.marital_status)

        age_select = ' 1=1 '
        if (self.age_from or self.age_from==0) and self.age_to:
            age_select = """ b.age >= %s AND b.age <= %s """
            where_select = where_select + ' AND ' + age_select if where_select else age_select
            params.append(self.age_from)
            params.append(self.age_to)

        file_no_select = ' 1=1 '
        # 20200701 Hajjar; Purpose: file_no doesn't exists in application
        # if self.file_no:
        #     file_no_select = """ app.file_no = %s """
        #     where_select = where_select + ' AND ' + file_no_select if where_select else file_no_select
        #     params.append(self.file_no)

        size_select = ' 1=1 '
        if self.size:
            size_select = """ b.id in (select ngo_beneficiary_id from ngo_beneficiary_ngo_size_rel where ngo_size_id IN %s)  """
            where_select = where_select + ' AND ' + size_select if where_select else size_select
            params.append(tuple(self.size.ids))             

        nationality_id_select = ' 1=1 '
        if self.nationality_id:
            nationality_id_select = """ b.nationality_id IN %s """
            where_select = where_select + ' AND ' + nationality_id_select if where_select else nationality_id_select
            params.append(tuple(self.nationality_id.ids))

        has_illness_select = ' 1=1 '
        if self.has_illness:
            has_illness_select = """ b.has_isllness = %s """
            where_select = where_select + ' AND ' + has_illness_select if where_select else has_illness_select
            params.append(self.has_illness)        

        has_handicap_select= ' 1=1 '
        if self.has_handicap:
            has_handicap_select = """ b.has_handicap = %s """
            where_select = where_select + ' AND ' + has_handicap_select if where_select else has_handicap_select
            params.append(self.has_handicap)  

        is_student_select= ' 1=1 '
        if self.is_student:
            is_student_select = """ b.is_student = %s """
            where_select = where_select + ' AND ' + is_student_select if where_select else is_student_select
            params.append(self.is_student)  

        return where_select


    def action_view_lines(self):
        self._compute_data()
        return {
            'name': self.name,
            'view_mode': 'tree,form,pivot,graph',
            'views': [(self.env.ref('ngo_edm.view_aged_tree').id, 'tree'), (False, 'form'), (False, 'pivot'), (False, 'graph')],
            'res_model': 'ngo.report.standard.ledger.line',
            'type': 'ir.actions.act_window',
            'domain': [('template_id', '=', self.template_id.id)],
            'context': {'search_default_%s' % self.template_id.name: 1},
            'target': 'current',
        }

    def print_pdf_report(self):
        self.ensure_one()
        self._compute_data()
        return self.env.ref('ngo_standard_report.action_standard_report').report_action(self)

    def print_excel_report(self):
        self.ensure_one()
        self._compute_data()
        print(self.env.ref('ngo_standard_report.action_standard_excel').report_action(self))
        return self.env.ref('ngo_standard_report.action_standard_excel').report_action(self)

    def _compute_data(self):
        self._sql_lines()
        self.refresh()

    def _sql_lines(self):
        query = """
        delete from  ngo_report_standard_ledger_line;
        INSERT INTO ngo_report_standard_ledger_line
            (template_id, create_uid, create_date, beneficiary_id, application_id, guide_id, beneficiary_code, first_name, father_name, mother_name, family_name, age, marital_status, gender, application_date, decision_id, file_no, application_type_id, residence_type_id, mohafaza, kadaa, city, region, neighborhood, has_illness, has_handicap, is_student )

        SELECT
            %s AS template_id,
            %s AS create_uid,
            NOW() AS create_date,
            b.id,
            b.application_id,
            b.guide_id,
            b.code,
            b.first_name,
            b.father_name,
            b.mother_name,
            b.family_name,
            b.age,
            b.marital_status,
            b.gender,
            app.application_date,
            app.decision_id,
            app.name,
            app.application_type_id,
            app.residence_type_id,
            app.mohafaza,
            app.kadaa,
            app.city,
            app.region,
            app.neighborhood,
            b.has_illness, 
            b.has_handicap, 
            b.is_student       
            FROM
                ngo_beneficiary b INNER JOIN ngo_beneficiary_application app ON b.application_id=app.id
                """
        params = [
            self.template_id.id,
            self.env.uid
        ]
        where_select = self.build_where(params)
        where_select = ' WHERE ' + where_select if where_select else ''
        query = query + where_select
        self.env.cr.execute(query, tuple(params))
        

    def _sql_lines_count(self):
        query = """
        SELECT Count(*) cnt
            FROM
                ngo_beneficiary b INNER JOIN ngo_beneficiary_application app ON b.application_id=app.id
                """
        params = []

        where_select =  self.build_where(params)
        where_select = ' WHERE '+where_select if where_select else ''

        query = query + where_select
        self.env.cr.execute(query, tuple(params))
        result  = self.env.cr.dictfetchall()
        if result:
            return result[0]['cnt']
        else:
            return 0

    @api.onchange('template_id')
    def _onchange_template_id(self):
        self.ensure_one()
        if self.template_id:
            for field in FIELDS_TEMPLATE:
                value = self.template_id[field]
                if value:
                    self[field] = value

    def action_save_template(self):
        self.ensure_one()
        if self.template_id:
            for field in FIELDS_TEMPLATE:
                if field in ('name',):
                    continue
                value = self[field]
                if value:
                    self.template_id[field] = value
   
    def copy_template(self,template):
        if template:
            for field in FIELDS_TEMPLATE:
                if field in ('name',):
                    continue
                value = template[field]
                if value:
                    self[field] = value

    def action_open_templates(self):
        self.ensure_one()
        return {
            'name': _('Template of %s') % self.company_id.name,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ngo.report.template',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('company_id', '=', self.company_id.id)]
        }
