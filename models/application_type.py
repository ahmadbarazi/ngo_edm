from odoo import fields, models, api, exceptions, _
from datetime import datetime


class ApplicationType(models.Model):
    _name = 'ngo.application.class'
    _description = "Beneficiary Application Type"
    _inherit = 'mail.thread'
    name = fields.Char(string="application type")
