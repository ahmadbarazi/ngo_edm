# Copyright 2010 Jordi Esteve, Zikzakmedia S.L. (http://www.zikzakmedia.com)
# Copyright 2010 Pexego Sistemas Informáticos S.L.(http://www.pexego.es)
#        Borja López Soilán
# Copyright 2013 Joaquin Gutierrez (http://www.gutierrezweb.es)
# Copyright 2015 Antonio Espinosa <antonioea@tecnativa.com>
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2016 Jacques-Etienne Baudoux <je@bcim.be>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from contextlib import closing
from io import StringIO

from odoo import _, api, exceptions, fields, models, tools
from odoo.tools import config

_logger = logging.getLogger(__name__)
EXCEPTION_TEXT = "Traceback (most recent call last)"


class WizardBeneficiarySearch(models.TransientModel):
    _name = "wizard.beneficiary.search"
    _description = "Wizard Beneficiary Search"

    state = fields.Selection(
        selection=[
            ("init", "Parameters"),
            ("ready", "Result"),
        ],
        string=_(u"Status"),
        readonly=True,
        default="init",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string=_(u"Company"),
        required=True,
        default=lambda self: self.env.user.company_id.id,
    )

    guide_id = fields.Many2many(
        comodel_name="ngo.guide",
        string=_(u"Guide"),
        required=False
    )

    file_no = fields.Char(string=_(u"File Number"))
    decision_id = fields.Many2one('ngo.application.decision.list',string=_(u"Application Decision"))
    gender = fields.Selection(string=_(u"Gender"), 
        selection=[('male',_(u'Male')),('female',_(u'Female'))],readonly=False)
    size=fields.Many2many('ngo.size',string=_('Size'))
    application_type_id = fields.Many2one('ngo.application.type',string=_(u"Application Type")) 
    region = fields.Many2one('ngo.region',string=_(u"Region"))
    marital_status=fields.Selection(string=_(u"Marital Status"), 
        selection=[('single',_(u'Single')),('married',_(u'Married')),('widow',_(u'Widow')),
                   ('divorced',_(u'Divorced')),('seperated',_(u'Separated')),
                   ('multiplemarriages',_(u'Multiple Marriages')),('undefined',_(u'Undefined'))],readonly=False)        
    residence_type_id = fields.Many2one('ngo.residence.type',string=_(u"Residence Type"))
    application_date = fields.Date(index=True)

    beneficiary_ids = fields.One2many(
        comodel_name="wizard.beneficiary.search.line",
        inverse_name="beneficiary_search_id",
        string=_(u"Beneficiary"),
        required=False
    )

    lang = fields.Selection(
        lambda self: self._get_lang_selection_options(),
        "Language",
        size=5,
        required=True,
        help="For records searched by name (taxes, fiscal "
        "positions), the template name will be matched against the "
        "record name on this language.",
        default=lambda self: self.env.context.get("lang", self.env.user.lang),
    )
 
    @api.model
    def _get_lang_selection_options(self):
        """Gets the available languages for the selection."""
        langs = self.env["res.lang"].search([])
        return [(lang.code, lang.name) for lang in langs]

    def _reopen(self):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_id": self.id,
            "res_model": self._name,
            "target": "new",
            # save original model in context,
            # because selecting the list of available
            # templates requires a model in context
            "context": {"default_model": self._name},
        }

    def action_init(self):
        """Initial action that sets the initial state."""
        self.write(
            {
                "state": "init",
                "beneficiary_ids": [(2, r.id, False) for r in self.beneficiary_ids],
            }
        )

        return self._reopen()

    def action_find_records(self):
        """Searchs for records to update/create and shows them."""
        self.clear_caches()
        self = self.with_context(lang=self.lang)
        self._find_beneficiaries()
        self.state = "ready"
        return self._reopen()

    def action_export_excel(self):
        """Action that creates/updates/deletes the selected elements."""
        self = self.with_context(lang=self.lang)
        self.state = "done"
        return self._reopen()

    def _find_beneficiaries(self):
        """Load account templates to create/update."""
        self.beneficiary_ids.unlink()
        beneficiaries=self.env["ngo.beneficiary"].search([("guide_id.id", "in", self.guide_id.ids)])
        for beneficiary in beneficiaries:
            self.beneficiary_ids.create(
                    {
                        "beneficiary_id": beneficiary.id,
                        "beneficiary_search_id": self.id,
                    }
                )
 
class WizardBeneficiarySearchLine(models.TransientModel):
    _name = "wizard.beneficiary.search.line"
    _description = (
        "Beneficiaries that are selected."
    )

    beneficiary_search_id = fields.Many2one(
        comodel_name="wizard.beneficiary.search",
        string=_(u"Update chart wizard"),
        required=True,
        ondelete="cascade",
    )
    beneficiary_id = fields.Many2one(
        comodel_name="ngo.beneficiary",
        string=_(u"Selected Beneficiary"),
        required=False,
        ondelete="set null",
    )
    beneficiary_code = fields.Char(related='beneficiary_id.code',string=_(u"Beneficiary Code"), store=True, readonly=True)
    
    beneficiary_name = fields.Char(related='beneficiary_id.name',string=_(u"Beneficiary Name"), store=True, readonly=True)
    beneficiary_guide = fields.Char(related='beneficiary_id.guide_id.name',string=_(u"Guide"), store=True, readonly=True)
    application_id = fields.Char(related='beneficiary_id.application_id.code',string=_(u"Application Code"), store=True, readonly=True)
    file_no = fields.Char(related='beneficiary_id.guide_id.name',string=_(u"File Number"), store=True, readonly=True)
    decision_id = fields.Char(related='beneficiary_id.application_id.decision_id.name',string=_(u"Application Decision"), store=True, readonly=True)
    gender = fields.Selection(related='beneficiary_id.gender',string=_(u"Gender"), 
        selection=[('male',_(u'Male')),('female',_(u'Female'))], store=True, readonly=True)
    application_type_id = fields.Char(related='beneficiary_id.application_id.application_type_id.name',string=_(u"Application Type"), store=True, readonly=True)
    region = fields.Char(related='beneficiary_id.region.name',string=_(u"Region"), store=True, readonly=True)
    marital_status=fields.Selection(related='beneficiary_id.marital_status', string=_(u"Marital Status"), 
        selection=[('single',_(u'Single')),('married',_(u'Married')),('widow',_(u'Widow')),
                   ('divorced',_(u'Divorced')),('seperated',_(u'Separated')),
                   ('multiplemarriages',_(u'Multiple Marriages')),('undefined',_(u'Undefined'))], store=True, readonly=True)       
    residence_type_id = fields.Char(related='beneficiary_id.application_id.residence_type_id.name',string=_(u"Residence Type"), store=True, readonly=True)
    application_date = fields.Date(related='beneficiary_id.application_id.application_date', store=True, readonly=True)

 