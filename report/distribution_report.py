# -*- coding: utf-8 -*-
# © 2014-2016 Barroux Abbey (http://www.barroux.org)
# © 2014-2016 Akretion France (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import tools
from odoo import models, fields , _


class DistributionReport(models.Model):
    _name = "ngo.distribution.report"
    _description = "Distribution Analysis"
    _auto = False
    _rec_name = 'distribution_date'
    _order = "distribution_date desc"

    distribution_date = fields.Date(
        'Distribution Date',
        readonly=True
    )
    product_id = fields.Many2one(
        'product.product',
        'Product',
        readonly=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Donor',
        readonly=True
    )
    # country_id = fields.Many2one(
        # 'res.country',
        # 'Partner Country',
        # readonly=True
    # )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        readonly=True
    )
    product_categ_id = fields.Many2one(
        'product.category',
        'Category of Product',
        readonly=True
    )
    # campaign_id = fields.Many2one(
        # 'donation.campaign',
        # 'Donation Campaign',
        # readonly=True
    # )
    in_kind = fields.Boolean('In Kind')
    # tax_receipt_ok = fields.Boolean('Eligible for a Tax Receipt')
    company_currency_id = fields.Many2one(
        'res.currency',
        string=_(u"Company Currency"),
        readonly=True
    )
    amount_company_currency = fields.Monetary(
        'Amount',
        readonly=True,
        currency_field='company_currency_id'
    )
    # tax_receipt_amount = fields.Monetary(
        # 'Tax Receipt Eligible Amount',
        # readonly=True,
        # currency_field='company_currency_id'
    # )

    def _select(self):
        # select = """
            # SELECT min(l.id) AS id,
                # d.donation_date AS donation_date,
                # l.product_id AS product_id,
                # l.in_kind AS in_kind,
                # l.tax_receipt_ok AS tax_receipt_ok,
                # pt.categ_id AS product_categ_id,
                # d.company_id AS company_id,
                # d.partner_id AS partner_id,
                # d.country_id AS country_id,
                # d.campaign_id AS campaign_id,
                # d.company_currency_id AS company_currency_id,
                # sum(l.amount_company_currency) AS amount_company_currency,
                # sum(l.tax_receipt_amount) AS tax_receipt_amount
                # """

        select = """
            SELECT min(l.id) AS id,
                d.distribution_date AS distribution_date,
                l.product_id AS product_id,
                l.in_kind AS in_kind,
                pt.categ_id AS product_categ_id,
                d.partner_id AS partner_id,
                sum(l.amount_company_currency) AS amount_company_currency 
                """
        return select

    def _from(self):
        from_sql = """
                ngo_distribution_product l
                LEFT JOIN ngo_distribution d ON (d.id=l.distribution_id)
                LEFT JOIN product_product pp ON (l.product_id=pp.id)
                LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
            """
        return from_sql

    def _where(self):
        where = """
            WHERE d.state='done'
            """
        return where

    def _group_by(self):
        # group_by = """
            # GROUP BY l.product_id,
                # l.in_kind,
                # l.tax_receipt_ok,
                # pt.categ_id,
                # d.donation_date,
                # d.partner_id,
                # d.country_id,
                # d.campaign_id,
                # d.company_id,
                # d.company_currency_id
            # """
        group_by = """
            GROUP BY l.product_id,
                l.in_kind,
                pt.categ_id,
                d.distribution_date,
                d.partner_id
            """

        return group_by

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        sql = "CREATE OR REPLACE VIEW %s AS (%s FROM %s %s %s)" % (
            self._table, self._select(), self._from(),
            self._where(), self._group_by())
        self._cr.execute(sql)
