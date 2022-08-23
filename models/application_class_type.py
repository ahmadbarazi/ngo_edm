from odoo import fields, models, api, _


class ApplicationClassType(models.Model):
    _name = 'application.class.type'
    _description = 'application class type'

    name = fields.Char()
    manager_id = fields.Many2one('res.users', string=_(u"Manager"))
