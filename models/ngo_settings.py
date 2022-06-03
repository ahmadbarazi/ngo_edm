import base64
import logging

from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError 
# from odoo.modules.module import get_module_resource

class FamilyRelationship(models.Model):
    _name = 'ngo.family.relationship'
    _description = 'Family Relationship'
    _order="name"
    
    name = fields.Char(
        string=_(u"Family Relationship"),
        required=True,
    )
    _sql_constraints = [('name_unique','unique(name)',_('Relationship already exists!'))]  

class EducationLevel(models.Model):
    _name = "ngo.education.level"
    _description= "Education Level"
    name = fields.Char(string = _("Education Level"))
    _sql_constraints = [('education_level_unique', 'unique (name)', _('Education level must be unique!'))]

class EducationInstitutionType(models.Model):
    _name = "ngo.education.institution.type"
    _description= "Education Insitution Type"
    name = fields.Char(string = _("Institution Type"))
    _sql_constraints = [('education_institution_type_unique', 'unique (name)', _('Education institution type must be unique!'))]

class EducationInstitution(models.Model):
    _name = "ngo.education.institution"
    _description= "Education Insitution"
    name = fields.Char(string = _("Institution Name"))
    education_institution_type= fields.Many2one('ngo.education.institution.type','Institution Type')
    
    _sql_constraints = [('education_institution_unique', 'unique (name)', _('Education Institution must be unique!'))]

class EducationClass(models.Model):
    _name = "ngo.education.class"
    _description= "Education Class"
    name = fields.Char(string = _("Education Class"))
    education_level_id = fields.Many2one('ngo.education.level',string=_("Education Level"))    
    _sql_constraints = [('education_class_unique', 'unique (name)', _('Education Class must be unique!'))]

class EducationSpecialty(models.Model):
    _name = "ngo.education.specialty"
    _description= "Education Specialty"
    name = fields.Char(string = _("Education Specialty"))
    _sql_constraints = [('education_class_unique', 'unique (name)', _('Education Specialty must be unique!'))]

class City(models.Model):
    _name = "ngo.city"
    _description= _("City")
    code = fields.Char(
        string=_(u"code")
    )
    name = fields.Char(string = _("City"))
    country_id = fields.Many2one('res.country',string = _("Country"))
    kadaa_id = fields.Many2one('ngo.kadaa',string=_("Kadaa"))

    _sql_constraints = [('city_unique', 'unique (name)', _('Country must be unique!'))]

class Region(models.Model):
    _name = "ngo.region"
    _description= "Region"
    code = fields.Char(
        string=_(u"code")
    )    
    name = fields.Char(string = _("Region"))
    city_id = fields.Many2one('ngo.city',string = _("City"))
    _sql_constraints = [('region_unique', 'unique (name)', _('Region must be unique!'))]

class Neighborhood(models.Model):
    _name = "ngo.neighborhood"
    _description= "Neighborhood"
    name = fields.Char(string = _("Neighborhood"))
    region_id = fields.Many2one('ngo.region',string = _("Region"))
    _sql_constraints = [('neighborhood_unique', 'unique (name)', _('Neighborhood must be unique!'))]

class LoanType(models.Model):
    _name = "ngo.loan.type"
    _description= "Loan Type"
    name = fields.Char(string = _("Loan Type"))
    _sql_constraints = [('loan_type_unique', 'unique (name)', _('Loan Type must be unique!'))]

class AssetType(models.Model):
    _name = "ngo.asset.type"
    _description= "Asset Type"
    name = fields.Char(string = _("Asset Type"))
    _sql_constraints = [('asset_type_unique', 'unique (name)', _('Asset Type must be unique!'))]

class ResidenceDescription(models.Model):
    _name = "ngo.residence.description"
    _description= "Residence Description"
    name = fields.Char(string = _("Residence Description"))
    _sql_constraints = [('region_unique', 'unique (name)', _('Residence Description must be unique!'))]

class ResidenceType(models.Model):
    _name = "ngo.residence.type"
    _description= "Residence Type"
    name = fields.Char(string = _("Residence Type"))
    _sql_constraints = [('region_unique', 'unique (name)', _('Residence Type must be unique!'))]

class ResidenceState(models.Model):
    _name = "ngo.residence.state"
    _description= "Residence State"
    name = fields.Char(string = _("Residence State"))
    _sql_constraints = [('residence_state_unique', 'unique (name)', _('Residence State must be unique!'))]

class Doctrine(models.Model):
    _name = "ngo.doctrine"
    _description= "Doctrine"
    name = fields.Char(string = _("Doctrine"))
    _sql_constraints = [('doctrine_unique', 'unique (name)', _('Doctrine must be unique!'))]

class Size(models.Model):
    _name = "ngo.size"
    _description= "Beneficiary Size"
    name = fields.Char(string = _("Size"))
    _sql_constraints = [('size_unique', 'unique (name)', _('Size must be unique!'))]

class ExpenseCategory(models.Model):
    _name = "ngo.expense.category"
    _description= "Beneficiary Expense Category"
    name = fields.Char(string = _("Expense Category"))
    parent_id= fields.Many2one('ngo.expense.category',_('Parent Category'))
    _sql_constraints = [('expense_category_unique', 'unique (name)', _('Expense Category must be unique!'))]

class IncomeType(models.Model):
    _name = "ngo.income.type"
    _description= "Beneficiary Income Type"
    name = fields.Char(string = _("Income Type"))
    _sql_constraints = [('income_type_unique', 'unique (name)', _('Income Type must be unique!'))]

class IllnessType(models.Model):
    _name = "ngo.illness.type"
    _description= "Beneficiary Illness Type"
    name = fields.Char(string = _("Illness Type"))
    _sql_constraints = [('illness_type_unique', 'unique (name)', _('Illness Type must be unique!'))]

class HandicapType(models.Model):
    _name = "ngo.handicap.type"
    _description= "Beneficiary Handicap Type"
    name = fields.Char(string = _("Handicap Type"))
    _sql_constraints = [('handicap_type_unique', 'unique (name)', _('Handicap Type must be unique!'))]

class Medicine(models.Model):
    _name = "ngo.medicine"
    _description= "Medicine"
    name = fields.Char(string = _("Medicine Name"))
    _sql_constraints = [('medicine_unique', 'unique (name)', _('Medicine Name must be unique!'))]

class Career(models.Model):
    _name = "ngo.career"
    _description= "Career"
    name = fields.Char(string = _("Career"))
    _sql_constraints = [('career_unique', 'unique (name)', _('Career must be unique!'))]

class JobTitle(models.Model):
    _name = "ngo.job.title"
    _description= "Job Title"
    name = fields.Char(string = _("Job Title"))
    _sql_constraints = [('job_title_unique', 'unique (name)', _('Job Title must be unique!'))]

class JobType(models.Model):
    _name = "ngo.job.type"
    _description= "Job Type"
    name = fields.Char(string = _("Job Type"))
    _sql_constraints = [('job_type_unique', 'unique (name)', _('Job Type must be unique!'))]

class JobState(models.Model):
    _name = "ngo.job.state"
    _description= "Job State"
    name = fields.Char(string = _("Job State"))
    _sql_constraints = [('job_state_unique', 'unique (name)', _('Job State must be unique!'))]
