import logging
from contextlib import closing
from io import StringIO

from odoo import _, api, exceptions, fields, models, tools
from odoo.tools import config
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)
EXCEPTION_TEXT = "Traceback (most recent call last)"


class ngo_distribution_receiving(models.TransientModel):
    _name = "ngo.distribution.receiving"
    _description = "Distributions Receiving"

    barcode = fields.Char(string=_(u"Bon Barcode"), size=18, )
    barcode_scan = fields.Boolean(string=_(u"Scan Barcode"))
    distribution_line_id = fields.Many2one('ngo.distribution.line', string=_(u"Distribution Line"), required=False)
    application_code = fields.Char(related='distribution_line_id.application_id.code', string=_(u"Application Code"),
                                   store=True, readonly=True)
    application_name = fields.Char(related='distribution_line_id.application_id.name',store=True, readonly=True)
    distribution_name = fields.Char(related='distribution_line_id.distribution_id.name', string=_(u"distribution name"),
                                    store=True, readonly=True)
    receipt_date = fields.Datetime(related='distribution_line_id.receipt_date', string=_(u"distribution name"),
                                   store=True, readonly=True)
    state = fields.Selection(related='distribution_line_id.state', string=_(u"state"), store=True, readonly=True)
    duration = fields.Integer(compute='_duration_tellnow')
    beneficiary_ids = fields.One2many('ngo.beneficiary', compute="_compute_beneficiary_ids")

    def _compute_beneficiary_ids(self):
        # You need to search the IDs of the drivers
        self.beneficiary_ids = self.distribution_line_id.application_id.beneficiary_ids

    # distributionline_ids = fields.One2many(
    #     "ngo.distribution.receiving.line",
    #     "distribution_receiving_id",
    #     string=_(u"Distributions applications receiving"),
    #     required=False
    # )

    # @api.constrains('barcode')
    # def _check_your_field(self):
    #     if self.barcode:
    #         if len(self.barcode) > 18:
    #             raise ValidationError('Number of characters must not exceed 18')

    @api.depends('receipt_date')
    def _duration_tellnow(self):
        if self.receipt_date:
            self.duration = int((datetime.now() - self.receipt_date).seconds / 60)
        else:
            self.duration = 0

    @api.onchange('barcode')
    def _barcode_changed(self):
        self.find_distribution()

    # @api.onchange('barcode_scan')
    # def _barcode_scan_changed(self):    
    #     if self.barcode_scan ==False:
    #        self.barcode_scan ==True

    def find_distribution(self):
        """Load distribution line templates to create/update."""
        DATE_FORMAT = "%Y-%m-%d "
        if self.barcode:
            if self.barcode != "":
                distributionlines = self.env["ngo.distribution.line"].search([("order_code", "=", self.barcode)])
                if distributionlines:
                    for distributionline in distributionlines:
                        if distributionline.receipt_date == False:
                            distributionline.receipt_date = datetime.now()
                            distributionline.state = "delivered"
                        self.distribution_line_id = distributionline.id
                        self.beneficiary_ids = self.distribution_line_id.application_id.beneficiary_ids

    # @api.model
    # def _get_lang_selection_options(self):
    #     """Gets the available languages for the selection."""
    #     langs = self.env["res.lang"].search([])
    #     return [(lang.code, lang.name) for lang in langs]

    # def _reopen(self):
    #     return {
    #         "type": "ir.actions.act_window",
    #         "view_mode": "form",
    #         "res_id": self.id,
    #         "res_model": self._name,
    #         "target": "new",
    #         # save original model in context,
    #         # because selecting the list of available
    #         # templates requires a model in context
    #         "context": {"default_model": self._name},
    #     }

    # def action_init(self):
    #     """Initial action that sets the initial state."""
    #     self.write(
    #         {
    #             "state": "init",
    #             "distributionline_ids": [(2, r.id, False) for r in self.distributionline_ids],
    #         }
    #     )

    #     return self._reopen()

    # def action_find_records(self):
    #     """Searchs for records to update/create and shows them."""
    #     self.clear_caches()
    #     self = self.with_context(lang=self.lang)
    #     self._find_distribution()
    #     self.state = "ready"
    #     return self._reopen()

# class ngo_distribution_receiving_line(models.TransientModel):
#     _name = "ngo.distribution.receiving.line"
#     _description = (
#         "Distributions Applications Received Lines"
#     )

#     distribution_receiving_id = fields.Many2one(
#         "ngo.distribution.receiving",
#         string=_(u"Distribution Receiving")
#     )

#     beneficiary_ids = fields.One2many('ngo.beneficiary', compute='_compute_beneficiary_ids')
#     # beneficiary_ids = fields.One2many(
#     #     'ngo.beneficiary', 'application_id', string=_(u"Application Members"))

#     # @api.multi
#     # def view_beneficiaries(self):
#     #     return {
#     #         'name': 'Drivers',
#     #         'view_type': 'form',
#     #         'view_mode': 'tree',
#     #         'res_model': 'car.driver',
#     #         'type': 'ir.actions.act_window',
#     #         'domain': [('id', 'in', driver_ids)], # List of IDs of the Drivers
#     #     }

#     def _compute_beneficiary_ids(self):
#         # You need to search the IDs of the drivers
#         self.beneficiary_ids = distribution_line_id.application_id.beneficiary_ids
