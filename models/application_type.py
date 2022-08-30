from odoo import fields, models, api, exceptions, _
from datetime import datetime


class ApplicationType(models.Model):
    _name = 'ngo.application.class'
    _description = "Beneficiary Application Type"
    name = fields.Char(string="application type")

    filetype_id = fields.Many2one('application.class.type', string="File Type")
    status = fields.Selection(
        [('draft', 'Draft'), ('approved', 'Approved'), ('submitted', 'Submitted'), ('rejected', 'Rejected')],
        string="Status", default='draft')
    remarks = fields.Text(string="Remarks")

    reverse_id = fields.Many2one('ngo.beneficiary.application')
