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
    _name = 'ngo_edm.ngo.distribution.food.portion.report.model'
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

        return self.env.ref('ngo_edm.distribution_food_portion_report').report_action(self, data=data)


class Report_ngo_distribution_food_portion(models.AbstractModel):
    """Abstract Model for report template.
    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """

    _name = 'report.ngo_edm.distribution_food_portion_report_view'

    def run_sql(self, qry, params):
        self._cr.execute(qry, tuple(params))
        _res = self._cr.dictfetchall()
        return _res

    @api.model
    def _get_report_values(self, docids, data=None):
        # report_obj = self.env['ir.actions.report']
        # report = report_obj._get_report_from_name('ngo_edm.distribution_food_portion_report_view')

        distribution_id = data['form']['distribution_id']
        application_id = data['form']['application_id']

        params = [
            application_id,
            distribution_id
        ]

        sql = """select C.id application_id, A.name distribution_name,
                    F.name first_beneficiary, S.name second_beneficiary, dc.name decision
                    from public.ngo_distribution A 
                    inner join public.ngo_distribution_line B  on  A.id= B.distribution_id
                    inner join public.ngo_beneficiary_application C on  B.application_id = C.id
                    inner join public.ngo_beneficiary D on D.application_id = C.ID
                    left join public.ngo_beneficiary  F on F.application_id = C.ID and F.is_first_beneficiary = True
                    left join public.ngo_beneficiary  S on S.application_id = C.ID and S.is_second_beneficiary = True
                    inner join public.ngo_application_decision_list dc on dc.id= C.decision_id
                    where C.id = %s and A.id = %s
                    """
        docs = []
        applicationfordistribute = self.run_sql(sql, params)
        # return {
        #     'doc_ids': docids,
        #     'doc_model': report.model,
        #     'docs': applicationfordistribute,
        # }
        return {
            'docs': applicationfordistribute,
        }
