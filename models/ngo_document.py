# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning


class DocumentList(models.Model):
    _name = 'ngo.document.list'
    _inherit = 'mail.thread'
    _description = "NGO Documents"

    def name_get(self):
        result = []
        for each in self:
            if each.document_type == 'beneficiary':
                name = each.name + '_م'
            elif each.document_type == 'application':
                name = each.name + '_ا'
            elif each.document_type == 'other':
                name = each.name + '_ot'
            result.append((each.id, name))
        return result

    name = fields.Char(string=_(u"Document Name"), copy=False, required=1)
    document_type = fields.Selection([('application', 'مستندات استمارة'),
                                      ('beneficiary', 'مستندات مستفيد'),
                                      ('other', 'مستندات أخرى')], string=_(u"Document Type"), required=1)

    _sql_constraints = [('ngo_document_name', 'unique (name)', _('Document name must be unique!'))]


class NgoBeneficiaryDocument(models.Model):
    _name = 'ngo.beneficiary.document'
    _description = 'Beneficiary Documents'

    def _get_default_code(self):
        sequence_code = 'ngo.beneficiary.document'
        sequence = self.env['ir.sequence'].search(
            [('code', '=', 'ngo.beneficiary.document')])
        next = sequence.get_next_char(sequence.number_next_actual)
        self.env['ir.sequence'].next_by_code(sequence_code)
        return next

    def mail_reminder(self):
        now = datetime.now() + timedelta(days=1)
        date_now = now.date()
        match = self.search([])
        for i in match:
            if i.expiry_date:
                exp_date = i.expiry_date - timedelta(days=7)
                if date_now >= exp_date:
                    mail_content = "  Hello  " + i.beneficiary_id.name + ",<br>Your Document " + i.name + "is going to expire on " + \
                                   str(i.expiry_date) + ". Please renew it before expiry date"
                    main_content = {
                        'subject': _('Document-%s Expired On %s') % (i.name, i.expiry_date),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': i.beneficiary_id.work_email,
                    }
                    self.env['mail.mail'].create(main_content).send()

    @api.constrains('expiry_date')
    def check_expr_date(self):
        for each in self:
            if each.expiry_date:
                exp_date = each.expiry_date
                if exp_date < date.today():
                    raise Warning('Your Document Is Already Expired.')

    name = fields.Char(string=_(u"Document Number"), required=True, copy=False, default=_get_default_code,
                       readonly=True)
    document_name = fields.Many2one('ngo.document.list', string=_(u"Document"), required=True)
    description = fields.Text(string=_(u"Description"), copy=False)
    expiry_date = fields.Date(string=_(u"Expiry Date"), copy=False)
    application_id = fields.Many2one('ngo.beneficiary.application', string=_(u"Application"))
    beneficiary_id = fields.Many2one('ngo.beneficiary', string=_(u"Beneficiary"),
                                     domain="[('application_id','=',application_id)]")
    doc_attachment_id = fields.Binary(string=_(u"Attachment"), attachment=True)
    doc_name = fields.Char(_(u"Attachment Name"))
    issue_date = fields.Date(string=_(u"Issue Date"), default=fields.Date.context_today, copy=False)
    is_available = fields.Selection([('exist', 'موجود'),
                                     ('missing', 'غير موجود'),
                                     ('na', 'غير ممكن الحصول')], string=_(u"Availability"))

    # @api.model
    # def create(self, vals):
    #     sequence_code = 'ngo.beneficiary.document'
    #     sequence = self.env['ir.sequence'].search(
    #         [('code', '=', sequence_code)])

    #     if vals['name'] == sequence.get_next_char(sequence.number_next_actual):
    #         vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code)   

    #     rec = super(NgoBeneficiaryDocument, self).create(vals)
    #     return rec

    # @api.constrains('url_file', 'url_file_fname')
    # def _check_url_file_fname(self):
    # rec = self.search([('url_file_fname', '=', self.url_file_fname)])
    # if len(rec) > 1:
    # raise ValidationError(_(
    # "This file name is already used on an existing record. "
    # "Please use another file name or delete the url_file on :\n"
    # "Model: %s Id: %s" % (self._name, rec.id)
    # ))


class NgoApplicationDocument(models.Model):
    _name = 'ngo.application.document'
    _description = 'Application Documents'

    # def mail_reminder(self):
    # now = datetime.now() + timedelta(days=1)
    # date_now = now.date()
    # match = self.search([])
    # for i in match:
    # if i.expiry_date:
    # exp_date = i.expiry_date - timedelta(days=7)
    # if date_now >= exp_date:
    # mail_content = "  Hello  " + i.beneficiary_id.name + ",<br>Your Document " + i.name + "is going to expire on " + \
    # str(i.expiry_date) + ". Please renew it before expiry date"
    # main_content = {
    # 'subject': _('Document-%s Expired On %s') % (i.name, i.expiry_date),
    # 'author_id': self.env.user.partner_id.id,
    # 'body_html': mail_content,
    # 'email_to': i.beneficiary_id.work_email,
    # }
    # self.env['mail.mail'].create(main_content).send()

    @api.constrains('expiry_date')
    def check_expr_date(self):
        for each in self:
            if each.expiry_date:
                exp_date = each.expiry_date
                if exp_date < date.today():
                    raise Warning('Your Document Is Already Expired.')

    name = fields.Char(string=_(u"Document Number"), required=True, copy=False)
    document_name = fields.Many2one('ngo.document.list', string=_(u"Document"), required=True)
    description = fields.Text(string=_(u"Description"), copy=False)
    expiry_date = fields.Date(string=_(u"Expiry Date"), copy=False)
    application_id = fields.Many2one('ngo.beneficiary.application', string=_(u"Application")
                                    , index=True,auto_join=True)
    beneficiary_id = fields.Many2one('ngo.beneficiary', invisible=1, copy=False)
    doc_attachment_id = fields.Binary(string=_(u"Attachment"), attachment=True)
    doc_name = fields.Char(_(u"Attachment Name"))
    issue_date = fields.Date(string=_(u"Issue Date"), default=fields.Date.context_today, copy=False)
    is_available = fields.Selection([('exist', 'موجود'),
                                     ('missing', 'غير موجود'),
                                     ('na', 'غير ممكن الحصول')], string=_(u"Availability"))


class NgoBeneficiary(models.Model):
    _inherit = 'ngo.beneficiary'

    def _document_count(self):
        for each in self:
            document_ids = self.env['ngo.beneficiary.document'].search([('beneficiary_id', '=', each.id)])
            each.document_count = len(document_ids)

    def document_view(self):
        self.ensure_one()
        domain = [
            ('beneficiary_id', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'ngo.beneficiary.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Documents
                        </p>'''),
            'limit': 80,
            'context': "{'default_beneficiary_id': '%s'}" % self.id
        }

    document_ids = fields.One2many('ngo.beneficiary.document', 'beneficiary_id', string=_(u"Documents"))
    document_count = fields.Integer(compute='_document_count', string=_(u"# Documents"))
    document_ref = fields.Char(string=_(u"Documents"), compute='get_application_documents')

    @api.depends('document_ids', 'document_ids.description')
    def get_application_documents(self):
        doc_ref = ''
        beneficiary_docs = self.env['ngo.document.list'].search([('document_type', '=', 'beneficiary')])
        for doc in beneficiary_docs:
            current_beneficiary_doc = self.document_ids.filtered(lambda x: x.document_name.id == doc.id)
            if current_beneficiary_doc:
                if current_beneficiary_doc.description and current_beneficiary_doc.description != '':
                    doc_ref = doc_ref + doc.name + " " + current_beneficiary_doc.description + " - "
                else:
                    doc_ref = doc_ref + doc.name + " - "
            else:
                doc_ref = doc_ref + doc.name + " - "
        self.document_ref = doc_ref


class NgoApplication(models.Model):
    _inherit = 'ngo.beneficiary.application'

    def _document_count(self):
        for each in self:
            document_ids = self.env['ngo.beneficiary.document'].search([('application_id', '=', each.id)])
            each.document_count = len(document_ids)

    def document_view(self):
        self.ensure_one()
        domain = [
            ('application_id', '=', self.id )]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'ngo.beneficiary.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Documents
                        </p>'''),
            'limit': 80,
            'context': {'default_application_id': self.id}
        }

    document_ids = fields.One2many('ngo.beneficiary.document', 'application_id', string=_(u"Documents"))
    document_count = fields.Integer(compute='_document_count', string=_(u"# Documents"))
    document_ref = fields.Char(string=_(u"Documents"), compute='get_application_documents')
    document_remaining = fields.Char(string=_(u"Remaining Documents"), compute='get_remaianing_application_documents')

    @api.depends('document_ids', 'document_ids.description')
    def get_application_documents(self):
        doc_ref = ''
        application_docs = self.env['ngo.document.list'].search([('document_type', '=', 'application')])
        for doc in application_docs:
            current_app_doc = self.document_ids.filtered(lambda x: x.document_name.id == doc.id)
            if current_app_doc:
                if current_app_doc.description and current_app_doc.description != '':
                    doc_ref = doc_ref + doc.name + " " + current_app_doc.description + " - "
                else:
                    doc_ref = doc_ref + doc.name + " - "
            else:
                doc_ref = doc_ref + doc.name + " - "
        self.document_ref = doc_ref

    @api.depends('document_ids', 'document_ids.description')
    def get_remaianing_application_documents(self):
        doc_ref = []
        doc_exist = []
        application_docs = self.env['ngo.document.list'].search([('document_type', '=', 'application')])
        for doc in application_docs:
            doc_ref.append(doc.name)

        for appdoc in self.document_ids:
            doc_exist.append(appdoc.doc_name)

        doc_remaining = set(doc_ref).difference(doc_exist)

        remaining_docs = ""
        for val in doc_remaining:
            remaining_docs = remaining_docs + val + " - "

        self.document_remaining = remaining_docs


class NgoBeneficiaryAttachment(models.Model):
    _inherit = 'ir.attachment'

    beneficiary_doc_attach_rel = fields.Many2many('ngo.beneficiary.document', 'doc_attachment_id', 'attach_id3',
                                                  'doc_id',
                                                  string=_(u"Attachment"), invisible=1)
