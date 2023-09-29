# -*- coding: utf-8 -*-
# Copyright 2014-2016 Barroux Abbey (http://www.barroux.org)
# Copyright 2014-2016 Akretion France
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# from ngo.report.standard.ledger import NgoReportStandardLedger
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare
from odoo.addons.account import _auto_install_l10n
from random import randrange
from datetime import timedelta
from datetime import datetime
import bisect


class DistributionType(models.Model):
    _name = "ngo.distribution.type"
    _description = "Distribution Type"
    name = fields.Char(string=_("Distribution Type"))

    _sql_constraints = [('distribution_type_unique', 'unique (name)', _('Distribution type must be unique!'))]


class NgoDistribution(models.Model):
    _name = 'ngo.distribution'
    _inherit = ['mail.thread']
    _description = 'NGO Distribution'
    _order = 'id desc'

    @api.model
    def _get_default_code(self):
        sequence = self.env['ir.sequence'].search([('code', '=', 'ngo.distribution')])
        next = sequence.get_next_char(sequence.number_next_actual)
        return next

    @api.depends(
        'product_ids.unit_price', 'product_ids.quantity',
        'product_ids.product_id', 'distribution_date', 'currency_id', 'company_id')
    def _compute_total(self):
        for distribution in self:
            total = 0.0
            distribution_currency = distribution.currency_id
            for line in distribution.product_ids:
                line_total = line.quantity * line.unit_price
                total += line_total

            distribution.amount_total = total
            distribution_currency = \
                distribution.currency_id.with_context(date=distribution.distribution_date)
            company_currency = distribution.company_currency_id
            total_company_currency = distribution_currency.compute(
                total, company_currency)
            distribution.amount_total_company_currency = total_company_currency

    # We don't want a depends on partner_id.country_id, because if the partner
    # moves to another country, we want to keep the old country for
    # past donations to have good statistics
    @api.depends('partner_id')
    def _compute_country_id(self):
        for distribution in self:
            distribution.country_id = distribution.partner_id.country_id

    @api.model
    def _default_currency(self):
        company = self.env['res.company']._company_default_get(
            'ngo.distribution')
        return company.currency_id

    currency_id = fields.Many2one(
        'res.currency',
        string=_(u"Currency"),
        required=True,
        states={'done': [('readonly', True)]},
        track_visibility='onchange',
        ondelete='restrict',
        default=_default_currency
    )
    association_id = fields.Many2one(
        'ngo.association',
        string=_(u"Association"),
        required=True,
        index=True,
        states={'done': [('readonly', True)]},
        track_visibility='onchange',
        ondelete='restrict'
    )

    # partner_id = fields.Many2one(
    # 'res.partner',
    # string=_(u"Donor"),
    # required=True,
    # index=True,
    # states={'done': [('readonly', True)]},
    # track_visibility='onchange',
    # ondelete='restrict'
    # )
    partner_id = fields.Many2one(
        'res.partner',
        string=_(u"Related Partner")
    )

    commercial_partner_id = fields.Many2one(
        related='partner_id.commercial_partner_id',
        string=_(u"Parent Donor"),
        readonly=True,
        store=True,
        index=True,
        compute_sudo=True
    )
    # country_id is here to have stats per country
    # WARNING : I can't put a related field, because when someone
    # writes on the country_id of a partner, it will trigger a write
    # on all it's donations, including donations in other companies
    # which will be blocked by the record rule
    country_id = fields.Many2one(
        'res.country',
        string=_(u"Country"),
        compute='_compute_country_id',
        store=True,
        readonly=True,
        compute_sudo=True
    )
    check_total = fields.Monetary(
        string=_(u"Check Amount"),
        states={'done': [('readonly', True)]},
        currency_field='currency_id',
        track_visibility='onchange'
    )
    amount_total = fields.Monetary(
        compute='_compute_total',
        string=_(u"Amount Total"),
        currency_field='currency_id',
        store=True,
        compute_sudo=True,
        readonly=True,
        track_visibility='onchange'
    )
    amount_total_company_currency = fields.Monetary(
        compute='_compute_total',
        string=_(u"Amount Total in Company Currency"),
        currency_field='company_currency_id',
        compute_sudo=True,
        store=True,
        readonly=True
    )
    distribution_date = fields.Date(
        string=_(u"Distribution Date"),
        required=True,
        states={'done': [('readonly', True)]},
        index=True,
        track_visibility='onchange'
    )
    company_id = fields.Many2one(
        'res.company',
        string=_(u"Company"),
        required=True,
        states={'done': [('readonly', True)]},
        default=lambda self: self.env['res.company']._company_default_get(
            'ngo.distribution'))
    line_ids = fields.One2many(
        'ngo.distribution.line',
        'distribution_id',
        string=_(u"Distribution Lines"),
        states={'done': [('readonly', True)]},
    )

    distribution_beneficiary_ids = fields.One2many(
        'ngo.distribution.beneficiary',
        'distribution_id',
        string=_(u"Beneficiaries"),
        states={'done': [('readonly', True)]},
    )

    product_ids = fields.One2many(
        'ngo.distribution.product',
        'distribution_id',
        string=_(u"Distribution Products"),
        states={'done': [('readonly', True)]},
    )

    move_id = fields.Many2one(
        'account.move',
        string=_(u"Account Move"),
        readonly=True,
        copy=False
    )

    number = fields.Char(
        related='move_id.name',
        readonly=True,
        store=True,
        string=_(u"Distribution Number")
    )
    # journal_id = fields.Many2one(
    # 'account.journal',
    # string=_(u"Payment Method"),
    # required=True,
    # domain=[
    # ('type', 'in', ('bank', 'cash')),
    # ('allow_donation', '=', True)],
    # states={'done': [('readonly', True)]},
    # track_visibility='onchange',
    # default=lambda self: self.env.user.context_donation_journal_id
    # )
    payment_ref = fields.Char(
        string=_(u"Payment Reference"),
        states={'done': [('readonly', True)]}
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('initiate', 'Started'),
        ('processed', 'Done'),
        ('cancel', 'Cancelled')],
        string=_(u"State"),
        readonly=True,
        copy=False,
        default='draft',
        index=True,
        track_visibility='onchange'
    )

    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        string=_(u"Company Currency"),
        readonly=True,
        store=True,
        compute_sudo=True
    )

    code = fields.Char('Code', size=32, required=True, copy=False, default='new')
    name = fields.Char(default=_get_default_code)
    distribution_type_id = fields.Many2one(
        'ngo.distribution.type',
        string=_(u"Distribution Type"),
        track_visibility='onchange',
        ondelete='restrict')
    distribution_address = fields.Char(_('Distribution Address'))
    start_time = fields.Char(_('Start Time'))
    end_time = fields.Char(_('End Time'))
    distribution_intervals = fields.Integer(_('Distribution Intervals'))
    distribution_days = fields.Integer(_('Distribution Intervals'))
    from_date = fields.Date(_('From Date'))
    to_date = fields.Date(_('To Date'))
    guide_ids = fields.Many2many(comodel_name="ngo.guide", string=_(u"Guide"), required=False)
    decision_ids = fields.Many2many('ngo.application.decision.list', string=_(u"Application Decision"))
    application_type_ids = fields.Many2many(comodel_name='ngo.application.type', string=_(u"Application Type"))
    age_from = fields.Float(string=_(u"From Age"))
    age_to = fields.Float(string=_(u"To Age"))
    beneficiary_count_from = fields.Float(string=_(u"From Beneficiary_count"))
    beneficiary_count_to = fields.Float(string=_(u"To Beneficiary Count"))
    family_name = fields.Many2many(comodel_name='partner.family.name', string=_(u"Family Name"))
    distribution_schedule_id = fields.Many2one('ngo.distribution.schedule', string=_(u"Distribution Schedule"),
                                               required=True, )
    expected_distribution_perday = fields.Integer(string=_(u"Expected Disribution per Day"))
    distribution_kind = fields.Selection([('Ibad', 'العباد'),
                                          ('Association', 'جهة')], string=_(u"Distribution Kind"), required=1,
                                         default="Ibad")
    filter_tempate_ids = fields.One2many(
        'ngo.distribution.filter.template',
        'distribution_id',
        string=_(u"Filter Template Lines"),
        states={'done': [('readonly', True)]},
    )

    print_remark = fields.Char(_('Print Remark'))
    beneficiary_count = fields.Float(string=_(u"Beneficiary Count"), compute="_get_beneficiary_count")

    _sql_constraints = [
        ('date_check', "CHECK ( (from_date <= to_date))", "The to date must be greater than the from date.")
    ]

    # campaign_id = fields.Many2one(
    # 'donation.campaign',
    # string=_(u"Donation Campaign"),
    # track_visibility='onchange',
    # ondelete='restrict',
    # default=lambda self: self.env.user.context_donation_campaign_id
    # )

    # def _prepare_each_tax_receipt(self):
    # self.ensure_one()
    # vals = {
    # 'company_id': self.company_id.id,
    # 'currency_id': self.company_currency_id.id,
    # 'donation_date': self.donation_date,
    # 'amount': self.tax_receipt_total,
    # 'type': 'each',
    # 'partner_id': self.commercial_partner_id.id,
    # }
    # return vals

    # def _prepare_move_line_name(self):
    # self.ensure_one()
    # name = _('Donation of %s') % self.partner_id.name
    # return name

    # def _prepare_counterpart_move_line(
    # self, name, amount_total_company_cur, total_amount_currency,
    # currency_id):
    # self.ensure_one()
    # precision = self.env['decimal.precision'].precision_get('Account')
    # if float_compare(
    # amount_total_company_cur, 0, precision_digits=precision) == 1:
    # debit = amount_total_company_cur
    # credit = 0
    # total_amount_currency = self.amount_total
    # else:
    # credit = amount_total_company_cur * -1
    # debit = 0
    # total_amount_currency = self.amount_total * -1
    # vals = {
    # 'debit': debit,
    # 'credit': credit,
    # 'name': name,
    # 'account_id': self.journal_id.default_debit_account_id.id,
    # 'partner_id': self.commercial_partner_id.id,
    # 'currency_id': currency_id,
    # 'amount_currency': (
    # currency_id and total_amount_currency or 0.0),
    # }
    # return vals

    # def _prepare_donation_move(self):
    # self.ensure_one()
    # if not self.journal_id.default_debit_account_id:
    # raise UserError(
    # _("Missing Default Debit Account on journal '%s'.")
    # % self.journal_id.name)

    # movelines = []
    # if self.company_id.currency_id.id != self.currency_id.id:
    # currency_id = self.currency_id.id
    # else:
    # currency_id = False
    ## Note : we can have negative donations for donors that use direct
    ## debit when their direct debit rejected by the bank
    # amount_total_company_cur = 0.0
    # total_amount_currency = 0.0
    # name = self._prepare_move_line_name()

    # aml = {}
    ## key = (account_id, analytic_account_id)
    ## value = {'credit': ..., 'debit': ..., 'amount_currency': ...}
    # precision = self.env['decimal.precision'].precision_get('Account')
    # for donation_line in self.line_ids:
    # if donation_line.in_kind:
    # continue
    # amount_total_company_cur += donation_line.amount_company_currency
    # account = donation_line.with_context(
    # force_company=self.company_id.id).product_id.product_tmpl_id.\
    # _get_product_accounts()['income']
    # account_id = account.id
    # analytic_account_id = donation_line.get_analytic_account_id()
    # amount_currency = 0.0
    # if float_compare(
    # donation_line.amount_company_currency, 0,
    # precision_digits=precision) == 1:
    # credit = donation_line.amount_company_currency
    # debit = 0
    # amount_currency = donation_line.amount * -1
    # else:
    # debit = donation_line.amount_company_currency * -1
    # credit = 0
    # amount_currency = donation_line.amount

    ## TODO Take into account the option group_invoice_lines ?
    # if (account_id, analytic_account_id) in aml:
    # aml[(account_id, analytic_account_id)]['credit'] += credit
    # aml[(account_id, analytic_account_id)]['debit'] += debit
    # aml[(account_id, analytic_account_id)]['amount_currency'] \
    # += amount_currency
    # else:
    # aml[(account_id, analytic_account_id)] = {
    # 'credit': credit,
    # 'debit': debit,
    # 'amount_currency': amount_currency,
    # }

    # if not aml:  # for full in-kind donation
    # return False

    # for (account_id, analytic_account_id), content in aml.items():
    # movelines.append((0, 0, {
    # 'name': name,
    # 'credit': content['credit'],
    # 'debit': content['debit'],
    # 'account_id': account_id,
    # 'analytic_account_id': analytic_account_id,
    # 'partner_id': self.commercial_partner_id.id,
    # 'currency_id': currency_id,
    # 'amount_currency': (
    # currency_id and content['amount_currency'] or 0.0),
    # }))

    ## counter-part
    # ml_vals = self._prepare_counterpart_move_line(
    # name, amount_total_company_cur, total_amount_currency,
    # currency_id)
    # movelines.append((0, 0, ml_vals))

    # vals = {
    # 'journal_id': self.journal_id.id,
    # 'date': self.donation_date,
    # 'ref': self.payment_ref,
    # 'line_ids': movelines,
    # }
    # return vals

    def calculate_checksum(ean):
        """
        Calculates the checksum for an EAN13
        @param list ean: List of 12 numbers for first part of EAN13
        :returns: The checksum for `ean`.
        :rtype: Integer
        """
        assert len(ean) == 12, "EAN must be a list of 12 numbers"
        sum_ = lambda x, y: int(x) + int(y)
        evensum = reduce(sum_, ean[::2])
        oddsum = reduce(sum_, ean[1::2])
        return (10 - ((evensum + oddsum * 3) % 10)) % 10

    def validate(self):
        # check_total = self.env['res.users'].has_group(
        # 'donation.group_donation_check_total')
        for distribution in self:
            if distribution.distribution_date > fields.Date.context_today(self):
                raise UserError(_(
                    'The date of the distribution of %s should be today '
                    'or in the past, not in the future!')
                                % distribution.partner_id.name)
            if not distribution.product_ids:
                raise UserError(_(
                    "Cannot validate the distribution of %s because it doesn't "
                    "have any lines!") % distribution.partner_id.name)

            # if float_is_zero(
            # distribution.amount_total,
            # precision_rounding=distribution.currency_id.rounding):
            # raise UserError(_(
            # "Cannot validate the donation of %s because the "
            # "total amount is 0 !") % distribution.partner_id.name)

            if distribution.state != 'draft':
                raise UserError(_(
                    "Cannot validate the donation of %s because it is not "
                    "in draft state.") % distribution.partner_id.name)

            # if check_total and float_compare(
            # distribution.check_total, distribution.amount_total,
            # precision_rounding=distribution.currency_id.rounding):
            # raise UserError(_(
            # "The amount of the distribution of %s (%s) is different "
            # "from the sum of the distribution lines (%s).") % (
            # distribution.partner_id.name, distribution.check_total,
            # distribution.amount_total))

            vals = {'state': 'done'}

            # if not float_is_zero(
            # distribution.amount_total,
            # precision_rounding=distribution.currency_id.rounding):
            # move_vals = distribution._prepare_donation_move()
            # when we have a full in-kind donation: no account move
            # if move_vals:
            # move = self.env['account.move'].create(move_vals)
            # move.post()
            # vals['move_id'] = move.id
            # else:
            # distribution.message_post(_(
            # 'Full in-kind donation: no account move generated'))

            # receipt = donation.generate_each_tax_receipt()
            # if receipt:
            # vals['tax_receipt_id'] = receipt.id

            distribution.write(vals)
        return

    def generate_12_random_numbers(self):
        numbers = ''
        for x in range(12):
            numbers = numbers + str(randrange(10))
        return numbers

    def action_generate_barcodes(self):
        self.state = 'initiate'
        distribution_lines = self.env['ngo.distribution.line'].search([('distribution_id.id', '=', self.id)])
        for app in distribution_lines:
            if not app.order_code:
                barcode = ''
                barcode = self.generate_12_random_numbers() + self.code[2:len(self.code)]
                while not app.order_code and self.env['ngo.distribution.line'].search_count(
                        [('order_code', '=', barcode), ('distribution_id.id', '=', self.id)]) > 0:
                    barcode = self.generate_12_random_numbers() + self.code[2:len(self.code)]
                app.order_code = barcode

    def action_print(self):
        vals = {'distribution_id': self.id,
                'application_id': self.line_ids[1].application_id.id}
        distributionfoodportion = self.env['ngo_edm.ngo.distribution.food.portion.report.model'].create(vals)
        return distributionfoodportion.get_report()

    def action_print2(self):
        vals = {'distribution_id': self.id}
        if self.distribution_type_id.id == 1:
            distributionfood = self.env['ngo_edm.ngo.distribution.food.report.model'].create(vals)
            return distributionfood.get_report()
        else:
            if self.distribution_type_id.id == 2:
                distributionclothes = self.env['ngo_edm.ngo.distribution.clothes.report.model'].create(vals)
                return distributionclothes.get_report()

        # """Call when button 'Get Report' clicked.
        # """
        # data = {
        #     'model': self._name,
        #     'form': {
        #         'distribution_id': str(self.id),
        #         'application_id': str(self.line_ids[1].application_id.id),
        #     },
        # }

        # return self.env.ref('ngo_edm.distribution_food_portion_report').report_action(self, data=data)    

    def action_get_lines(self):
        self.ensure_one()
        self._compute_data()

    def _compute_data(self):
        # self._pre_compute()
        # self._sql_report_object()
        self._sql_lines()
        self._sql_beneficiaires_lines()
        self.refresh()

    def action_distribute_applications_perdays(self):
        listtodistribute = self.env['ngo.distribution.line'].search([('distribution_id', '=', self.id)],
                                                                    order='application_type_id asc')

        # listtodistribute = self.line_ids.all().order_by('application_type_id')

        if self.distribution_schedule_id:
            schedule = self.env['ngo.distribution.schedule'].search([('id', '=', self.distribution_schedule_id.id)])[0]
            days = []
            if schedule.monday == True:
                days.append(int(2))
            if schedule.tuesday == True:
                days.append(int(3))
            if schedule.wednesday == True:
                days.append(int(4))
            if schedule.thursday == True:
                days.append(int(5))
            if schedule.friday == True:
                days.append(int(6))
            if schedule.saturday == True:
                days.append(int(7))
            if schedule.sunday == True:
                days.append(int(1))
            if schedule.distribution_intervals:
                distribution_intervals = schedule.distribution_intervals
            if self.from_date:
                from_date = self.from_date
            if self.expected_distribution_perday > 0:
                cnt = 0
            interval = 1
            start_time_day_text = self.from_date.strftime("%A")
            start_time_day = int(0)
            if start_time_day_text == "Monday":
                start_time_day = int(2)
                delivery_time = schedule.monday_hour_from
                delivery_totime = schedule.monday_hour_to
                delivery_time2 = schedule.monday_hour_from2
                delivery_totime2 = schedule.monday_hour_to2
            if start_time_day_text == "Tuesday":
                start_time_day = int(3)
                delivery_time = schedule.tuesday_hour_from
                delivery_totime = schedule.tuesday_hour_to
                delivery_time2 = schedule.tuesday_hour_from2
                delivery_totime2 = schedule.tuesday_hour_to2
            if start_time_day_text == "Wednesday":
                start_time_day = int(4)
                delivery_time = schedule.wednesday_hour_from
                delivery_totime = schedule.wednesday_hour_to
                delivery_time2 = schedule.wednesday_hour_from2
                delivery_totime2 = schedule.wednesday_hour_to2
            if start_time_day_text == "Thursday":
                start_time_day = int(5)
                delivery_time = schedule.thursday_hour_from
                delivery_totime = schedule.thursday_hour_to
                delivery_time2 = schedule.thursday_hour_from2
                delivery_totime2 = schedule.thursday_hour_to2
            if start_time_day_text == "Friday":
                start_time_day = int(6)
                delivery_time = schedule.friday_hour_from
                delivery_totime = schedule.friday_hour_to
                delivery_time2 = schedule.friday_hour_from2
                delivery_totime2 = schedule.friday_hour_to2
            if start_time_day_text == "Saturday":
                start_time_day = int(7)
                delivery_time = schedule.saturday_hour_from
                delivery_totime = schedule.saturday_hour_to
                delivery_time2 = schedule.saturday_hour_from2
                delivery_totime2 = schedule.saturday_hour_to2
            if start_time_day_text == "Sunday":
                start_time_day = int(1)
                delivery_time = schedule.sunday_hour_from
                delivery_totime = schedule.sunday_hour_to
                delivery_time2 = schedule.sunday_hour_from2
                delivery_totime2 = schedule.sunday_hour_to2
            DATE_FORMAT = "%Y-%m-%d "

            delivery_date = self.from_date  # .strftime(DATE_FORMAT)

            for application in listtodistribute:
                if cnt < self.expected_distribution_perday:
                    cnt = cnt + 1
                    days.sort

                    # while str(days.index(start_time_day)) not in ('0','1','2','3','4','5','6'):
                    while bisect.bisect_left(days,
                                             start_time_day) == False:  # str(days.index(start_time_day)) not in ('0','1','2','3','4','5','6'):
                        start_time_day = start_time_day + 1
                        if start_time_day == 8:
                            start_time_day = 1
                        delivery_date = delivery_date + timedelta(days=1)

                    application.delivery_date = delivery_date.strftime(DATE_FORMAT)
                    hourstoadd = 0
                    if self.expected_distribution_perday > 0:
                        hourstoadd = int(distribution_intervals * cnt / self.expected_distribution_perday)
                    if (timedelta(hours=delivery_time) - timedelta(hours=hourstoadd)) > (
                    timedelta(hours=delivery_time2)):
                        application.delivery_time = timedelta(hours=delivery_time) + timedelta(
                            hours=delivery_time2) - timedelta(hours=delivery_time) + timedelta(hours=hourstoadd)
                    else:
                        application.delivery_time = timedelta(hours=delivery_time) + timedelta(hours=hourstoadd)
                    if cnt == self.expected_distribution_perday:
                        cnt = 1
                        start_time_day = start_time_day + 1
                        delivery_date = delivery_date + timedelta(days=1)
                        if start_time_day == 8:
                            start_time_day = 1

    def _sql_lines(self):

        query = """
        delete from ngo_distribution_line where distribution_id = %s;
        INSERT INTO ngo_distribution_line
            (distribution_id, create_uid, create_date, application_id, partner_id, receipt_date, first_beneficiary_name, beneficiary_count, decision_id, application_type_id)

        SELECT Distinct
            %s AS distribution_id,
            %s AS create_uid,
            NOW() AS create_date,
            app.id,
            app.partner_id,
            %s as receipt_date,
            app.first_beneficiary_name,
            app.beneficiary_count,
            app.decision_id,
            app.application_type_id 
            FROM
                ngo_beneficiary b INNER JOIN ngo_beneficiary_application app ON b.application_id=app.id
                """

        # WHERE
        # b.guide_id  IN %s
        # AND b.first_name iLIKE %s
        # """

        params = [
            # SELECT
            self.id,
            self.id,
            self.env.uid,
            self.distribution_date
            # ,
            # WHERE
            # tuple(self.guide_ids.ids) if self.guide_ids else (None,),
            # '%'+self.first_name+'%' if self.first_name else (None,)
        ]

        where_select = ''
        guide_select = ''
        where_Template = ''
        template_list = self.env['ngo.distribution.filter.template'].search([('distribution_id.id', '=', self.id)])
        for template in template_list:
            where_Template = ''
            params2 = []
            standardledger = self.env["ngo.report.standard.ledger"].create({
                'name': template.filter_template_id.name})
            standardledger.copy_template(template.filter_template_id)
            where_Template = standardledger.build_where(params2)
            if where_select:
                if where_Template:
                    where_select = where_select + ' or (' + where_Template + ')'
                else:
                    pass
            else:
                if where_Template:
                    where_select = where_select + '(' + where_Template + ')'
                else:
                    pass
            params.extend(params2)
        where_select = ' WHERE ' + where_select if where_select else ''

        query = query + where_select
        # raise UserError (query)

        # self.env.cr.execute(query)
        self.env.cr.execute(query, tuple(params))

    @api.depends('distribution_beneficiary_ids')
    def _get_beneficiary_count(self):
        self.beneficiary_count = len(self.distribution_beneficiary_ids)

    def _sql_beneficiaires_lines(self):

        query = """
        delete from ngo_distribution_beneficiary where distribution_id = %s;
        INSERT INTO ngo_distribution_beneficiary
            (distribution_id, create_uid, create_date, application_id, beneficiary_id)

        SELECT Distinct
            %s AS distribution_id,
            %s AS create_uid,
            NOW() AS create_date,
            b.application_id,
            b.id
            FROM
                ngo_beneficiary b INNER JOIN ngo_distribution_line distributionlines ON b.application_id=distributionlines.application_id and distribution_id = %s
                """

        # WHERE
        # b.guide_id  IN %s
        # AND b.first_name iLIKE %s
        # """

        params = [
            # SELECT
            self.id,
            self.id,
            self.env.uid,
            self.id,
            # ,
            # WHERE
            # tuple(self.guide_ids.ids) if self.guide_ids else (None,),
            # '%'+self.first_name+'%' if self.first_name else (None,)
        ]

        where_select = ''
        guide_select = ''
        where_Template = ''
        template_list = self.env['ngo.distribution.filter.template'].search([('distribution_id.id', '=', self.id)])
        for template in template_list:
            where_Template = ''
            params2 = []
            standardledger = self.env["ngo.report.standard.ledger"].create({
                'name': template.filter_template_id.name})
            standardledger.copy_template(template.filter_template_id)
            where_Template = standardledger.build_where_beneficiary(params2)
            if where_select:
                if where_Template:
                    where_select = where_select + ' or (' + where_Template + ')'
                else:
                    pass
            else:
                if where_Template:
                    where_select = where_select + '(' + where_Template + ')'
                else:
                    pass
            params.extend(params2)
        where_select = ' WHERE ' + where_select if where_select else ''

        query = query + where_select
        # raise UserError (query)

        # self.env.cr.execute(query)
        self.env.cr.execute(query, tuple(params))

    # def generate_each_tax_receipt(self):
    # self.ensure_one()
    # receipt = False
    # if (
    # self.tax_receipt_option == 'each' and
    # not self.tax_receipt_id and
    # not float_is_zero(
    # self.tax_receipt_total,
    # precision_rounding=self.company_currency_id.rounding)):
    # receipt_vals = self._prepare_each_tax_receipt()
    # receipt = self.env['donation.tax.receipt'].create(receipt_vals)
    # return receipt

    # def save_default_values(self):
    # self.ensure_one()
    # self.env.user.write({
    # 'context_donation_journal_id': self.journal_id.id,
    # 'context_donation_campaign_id': self.campaign_id.id,
    # })

    # def done2cancel(self):
    # '''from Done state to Cancel state'''
    # for donation in self:
    # if donation.tax_receipt_id:
    # raise UserError(_(
    # "You cannot cancel this donation because "
    # "it is linked to the tax receipt %s. You should first "
    # "delete this tax receipt (but it may not be legally "
    # "allowed).")
    # % donation.tax_receipt_id.number)
    # if donation.move_id:
    # donation.move_id.button_cancel()
    # donation.move_id.unlink()
    # donation.state = 'cancel'

    # def cancel2draft(self):
    # '''from Cancel state to Draft state'''
    # for donation in self:
    # if donation.move_id:
    # raise UserError(_(
    # "A cancelled donation should not be linked to "
    # "an account move"))
    # if donation.tax_receipt_id:
    # raise UserError(_(
    # "A cancelled donation should not be linked to "
    # "a tax receipt"))
    # donation.state = 'draft'

    def unlink(self):
        for distribution in self:
            if distribution.state == 'done':
                raise UserError(_(
                    "The distribution '%s' is in Done state, so you cannot "
                    "delete it.") % distribution.display_name)
            # if donation.move_id:
            # raise UserError(_(
            # "The donation '%s' is linked to an account move, "
            # "so you cannot delete it.") % donation.display_name)
            # if donation.tax_receipt_id:
            # raise UserError(_(
            # "The donation '%s' is linked to the tax receipt %s, "
            # "so you cannot delete it.")
            # % (donation.display_name, donation.tax_receipt_id.number))
        return super(NgoDistribution, self).unlink()

    # def name_get(self):
    # res = []
    # for distribution in self:
    # if distribution.state == 'draft':
    # name = _('Draft Distribution of %s') % distribution.name
    # elif distribution.state == 'cancel':
    # name = _('Cancelled Distribution of %s') % distribution.name
    # else:
    # name = distribution.number
    # res.append((distribution.id, name))
    # return res

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].search([('code', '=', 'ngo.distribution')])
        sequence_code = 'ngo.distribution'
        vals['code'] = self.env['ir.sequence'].next_by_code(sequence_code)
        rec = super(NgoDistribution, self).create(vals)
        return rec

    # @api.onchange('tax_receipt_option')
    # def tax_receipt_option_change(self):
    # res = {}
    # if (
    # self.partner_id and
    # self.partner_id.tax_receipt_option == 'annual' and
    # self.tax_receipt_option != 'annual'):
    # res = {
    # 'warning': {
    # 'title': _('Error:'),
    # 'message':
    # _('You cannot change the Tax Receipt '
    # 'Option when it is Annual.'),
    # },
    # }
    # self.tax_receipt_option = 'annual'
    # return res

    # @api.model
    # def auto_install_l10n(self):
    # """Helper function for calling a method that is not accessible directly
    # from XML data.
    # """
    # _auto_install_l10n(self.env.cr, None)


class NgoDistributionLine(models.Model):
    _name = 'ngo.distribution.line'

    partner_id = fields.Many2one('res.partner', string=_(u"Related Partner"),
                                 domain=[('is_application', '=', True)])  # ADD DOMAIN
    application_id = fields.Many2one('ngo.beneficiary.application', string=_(u"Application"))  # ADD DOMAIN
    distribution_id = fields.Many2one('ngo.distribution', string=_(u"Distribution"), required=True)
    order_code = fields.Char(string=_(u"Order Code"))
    first_beneficiary_name = fields.Char(string=_(u"First Beneficiary"), readonly=True)
    application_type_id = fields.Many2one('ngo.application.type', string=_(u"Application Type"))  # ADD DOMAIN
    decision_id = fields.Many2one('ngo.application.decision.list', string=_(u"Decision Number"), readonly=True)
    delivery_date = fields.Date(string=_(u"Delivery Date"))
    delivery_time = fields.Char(string=_(u"Delivery Time"))
    receipt_date = fields.Datetime(string=_(u"Receipt Date"))
    delivery_date_text = fields.Char(string=_(u"Delivery Date text"), compute='get_delivery_date_text', store=True, )
    beneficiary_count = fields.Integer(string=_(u"Member Count"), readonly=True)
    print_count = fields.Integer(string=_(u"Print Count"), default=0)
    is_printed = fields.Boolean(string=_(u"Print"), default=False)

    state = fields.Selection([
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')],
        string=_(u"State"),
        readonly=True,
        copy=False,
        default='pending',
        index=True,
    )

    # @api.depends('application_id')
    @api.onchange('application_id')
    def _compute_application_info(self):
        for application in self:
            if application.application_id:
                application_rec = application.env['ngo.beneficiary.application'].search(
                    [('id', '=', application.application_id.id)], limit=1)
                if application_rec:
                    application.first_beneficiary_name = application_rec.first_beneficiary_name
                    application.decision_id = application_rec.decision_id
                    application.beneficiary_count = application_rec.beneficiary_count
                    application.application_type_id = application_rec.application_type_id

    def dayofweekarabic(self, i):
        switcher = {
            6: 'الأحد',
            0: 'الإثنين',
            1: 'الثلثاء',
            2: 'الأربعاء',
            3: 'الخميس',
            4: 'الجمعة',
            5: 'السبت'
        }
        return switcher.get(i, "Invalid day of week")

    def montharabic(self, i):
        switcher = {
            1: 'كانوناالثاني',
            2: 'شباط',
            3: 'أذار',
            4: 'نيسان',
            5: 'أيار',
            6: 'حذيران',
            7: 'تموز',
            8: 'أب',
            9: 'أيلول',
            10: 'تشرين أول',
            11: 'تشرين ثاني',
            12: 'كانون أول'
        }
        return switcher.get(i, "Invalid month")

    @api.depends('delivery_date', 'delivery_time')
    def get_delivery_date_text(self):
        for record in self:
            if record.delivery_date:
                receiptdate = record.delivery_date
                dayoftheweekreceiptdate = record.delivery_date.weekday()
                dayreceiptdate = record.delivery_date.strftime("%d")
                monthreceiptdate = int(record.delivery_date.strftime("%m"))
                yearreceiptdate = record.delivery_date.strftime("%Y")
                # timereceiptdate  =   record.delivery_time.strftime("%H") +":"+ record.delivery_time.strftime("%M")
                timereceiptdate = record.delivery_time[:5]
                delivery_date_text = self.dayofweekarabic(dayoftheweekreceiptdate) + " في " + str(
                    dayreceiptdate) + " " + self.montharabic(monthreceiptdate) + " " + str(
                    yearreceiptdate) + " الساعة " + str(timereceiptdate)
                record.delivery_date_text = delivery_date_text


class NgoDistributionfiltertemplate(models.Model):
    _name = 'ngo.distribution.filter.template'
    _description = 'Distribution Filters'

    distribution_id = fields.Many2one('ngo.distribution', string=_(u"Distribution"), required=True)
    filter_template_id = fields.Many2one('ngo.report.template', 'template')
    total_benefeciaries_count = fields.Integer(string=_(u"Beneficiaries Members Count"))

    @api.onchange('filter_template_id')
    def onchange_filter_template_id(self):
        if self.filter_template_id:
            standardledger = self.env["ngo.report.standard.ledger"].create({
                'name': 'templatefilter'})
            # standardledger = NgoReportStandardLedger()
            standardledger.copy_template(self.filter_template_id)
            value = standardledger._sql_lines_count()
            self.total_benefeciaries_count = value


class NgoDistributionProduct(models.Model):
    _name = 'ngo.distribution.product'
    _description = 'Distribution Products'
    _rec_name = 'product_id'

    @api.depends(
        'unit_price', 'quantity', 'product_id', 'distribution_id.currency_id',
        'distribution_id.distribution_date', 'distribution_id.company_id')
    def _compute_amount(self):
        for line in self:
            amount = line.quantity * line.unit_price
            line.amount = amount
            distribution_currency = line.distribution_id.currency_id.with_context(
                date=line.distribution_id.distribution_date)
            amount_company_currency = distribution_currency.compute(
                amount, line.distribution_id.company_id.currency_id)
            line.amount_company_currency = amount_company_currency

    distribution_id = fields.Many2one(
        'ngo.distribution',
        'Distribution',
        ondelete='cascade'
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='distribution_id.currency_id',
        readonly=True,
        compute_sudo=True
    )
    company_currency_id = fields.Many2one(
        'res.currency',
        related='distribution_id.company_id.currency_id',
        readonly=True,
        compute_sudo=True
    )
    product_id = fields.Many2one(
        'product.product',
        'Product',
        required=True,
        ondelete='restrict'
    )
    quantity = fields.Float('Quantity')
    # quantity_share = fields.Float('Share Quantity')
    unit_price = fields.Monetary(
        string=_(u"Unit Price"),
        currency_field='currency_id'
    )
    amount = fields.Monetary(
        compute='_compute_amount',
        string=_(u"Amount"),
        compute_sudo=True,
        currency_field='currency_id',
        store=True,
        readonly=True
    )
    amount_company_currency = fields.Monetary(
        compute='_compute_amount',
        string=_(u"Amount in Company Currency"),
        compute_sudo=True,
        currency_field='company_currency_id',
        store=True,
        readonly=True
    )

    sequence = fields.Integer(_(u"Sequence"))

    in_kind = fields.Boolean(
        related='product_id.in_kind_donation',
        readonly=True,
        store=True,
        string=_(u"In Kind"),
        compute_sudo=True
    )

    @api.onchange('product_id')
    def product_id_change(self):
        for line in self:
            if line.product_id and line.product_id.list_price:
                # We should change that one day...
                line.unit_price = line.product_id.list_price

    @api.model
    def get_analytic_account_id(self):
        return self.analytic_account_id.id or False


class ngo_distribution_beneficiaries(models.Model):
    _name = 'ngo.distribution.beneficiary'

    distribution_id = fields.Many2one('ngo.distribution', string=_(u"Application"))
    application_id = fields.Many2one('ngo.beneficiary.application', string=_(u"Application"))
    beneficiary_id = fields.Many2one('ngo.beneficiary', string=_(u"Beneficiary"))
