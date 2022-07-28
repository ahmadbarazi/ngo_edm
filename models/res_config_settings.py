from odoo import api, exceptions, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    expenses = fields.Boolean("hide expenses", config_parameter='ngo_edm.expenses')
    hide_benfeciary_size = fields.Boolean("hide size", config_parameter='ngo_edm.hide_benfeciary_size')
