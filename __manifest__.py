# -*- coding: utf-8 -*-
##############################################################################
#   
#    Copyright (C) 2017 Navybits (<http://www.navybits.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "NGO Management",

    'summary': """
        A module to handle the donation management between sponsors and beneficiaries""",

    'description': """
        This module takes into consideration between the sponsors and beneficiaries. 
        This works by creating beneficiaries that go trough supervision and either be accepted or rejected, then creation of sponsors who can guarantee one or many beneficiaries by createing a kafele(warranty) and pay this warranty in the kafele invoice. 
        The goal of this module is to try to make a simpler interface to handle all the accounting works behind the curtains. 
    """,

    'author': "Engineering Design and Manufacturing",
    'website': "http://www.edm.com.lb",

    'category': 'Crm',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'mail', 'resource', 'web'],

    # always loaded
    'data': [
        # 'views/template.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'data/ngo_data.xml',
        'views/application_type.xml',
        # 'data/data_income.xml',
        # 'data/data_expense.xml',
        'data/doc_data.xml',
        'views/ngo_application.xml',
        # # 'views/survey_workflow.xml',
        'views/ngo_beneficiary.xml',
        'views/ngo_sponsor.xml',
        'views/ngo_guide.xml',
        'views/ngo_association.xml',
        # # 'views/donation.xml',
        # # 'views/kafele.xml',
        # # 'views/kafele_invoice.xml',

        'views/res_config_settings.xml',
        'views/ngo_document.xml',
        'views/ngo_menu.xml',
        'views/ngo_distribution.xml',
        'views/ngo_distribution_schedule.xml',
        'views/partner.xml',
        'views/product.xml',
        'views/ngo_distribution_clothes_report_template.xml',
        'views/ngo_distribution_food_portion_report_template.xml',
        'views/ngo_distribution_food_report_template.xml',
        'views/ngo_distribution_receiving.xml',
        'views/application_class_type.xml',
        # # 'wizard/wizard_beneficiary_search_view.xml',
        'report/distribution_report_view.xml',
        'views/ngo_menu.xml',
        'views/ngo_standard.xml',
        'views/ngo_standard_report_template_view.xml',
        'wizard/ngo_standard_report_view.xml',
        'wizard/wizard_beneficiary_search_view.xml'

        # # 'views/donation_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ngo_edm/static/src/css/style.css']
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
