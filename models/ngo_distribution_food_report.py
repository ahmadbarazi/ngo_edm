# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, tools
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from openerp.tools.translate import _
from openerp.exceptions import UserError
import openerp
import json
import logging
import random


class ngo_distribution_food_portion_report_model(models.TransientModel):
    _name = 'ngo_edm.ngo.distribution.food.report.model'
    # distribution_id = fields.Many2one('ngo.distribution',string=_('Distribution'))
    # application_id = fields.Many2one('ngo.beneficiary.application',string=_('Application'))
    distribution_id = fields.Integer()
    application_id = fields.Integer()

    def get_report(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'model': self._name,
            'form': {
                'distribution_id': self.distribution_id,
                'application_id': self.application_id,
            },
        }

        return self.env.ref('ngo_edm.distribution_food_report').report_action(self, data=data)


class Report_ngo_distribution_food(models.Model):
    _name = 'report.ngo_edm.distribution_food_report_view'

    distribution_id = fields.Many2one('ngo.distribution', string=_(u"Application"))
    application_id = fields.Many2one('ngo.beneficiary.application', string=_(u"Application"))  # ADD DOMAIN
    order_code = fields.Char(_(u"Barcode"))
    delivery_date_text = fields.Char(_(u"delivery date text"))

    # first_beneficiary_id = fields.Many2one( 'ngo.beneficiary', string=_(u"First Beneficiary"))
    # Second_beneficiary_id = fields.Many2one( 'ngo.beneficiary', string=_(u"Second Beneficiary"))

    def run_sql(self, qry, params):
        self._cr.execute(qry, tuple(params))

    @api.model
    def _get_report_values(self, docids, data=None):
        # report_obj = self.env['ir.actions.report']
        # report = report_obj._get_report_from_name('ngo_edm.distribution_food_portion_report_view')

        distribution_id = data['form']['distribution_id']

        params = [
            distribution_id
        ]

        sql = """  delete from report_ngo_edm_distribution_food_report_view;
                    insert into report_ngo_edm_distribution_food_report_view
                    (distribution_id, application_id, order_code, delivery_date_text )
                    select A.id  ,  B.application_id, B.order_code, B.delivery_date_text
                    from public.ngo_distribution A 
                    inner join public.ngo_distribution_line B  on  A.id= B.distribution_id
                    where A.id = %s
                    """
        self.run_sql(sql, params)
        docs = []
        applicationfordistribute = self.env["report.ngo_edm.distribution_food_report_view"].search(
            [("distribution_id", "=", distribution_id)])
        # return {
        #     'doc_ids': docids,
        #     'doc_model': report.model,
        #     'docs': applicationfordistribute,
        # }
        return {
            'docs': applicationfordistribute,
        }
