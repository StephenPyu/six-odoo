# -*- coding: utf-8 -*-
{
    'name': "Estate",

    'summary': """
        Starting module for "Master the Odoo web framework, chapter 1: Build an Estate property"
    """,

    'description': """
        Starting module for "Master the Odoo web framework, chapter 1: Build an Estate property"
    """,

    'author': "Odoo",
    'website': "https://www.odoo.com/",
    'category': 'Real Estate/Brokerage',
    'version': '0.1',
    'application': True,
    'installable': True,
    'depends': ['base', 'web'],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_menus.xml',
        'views/res_users_view.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'estate/static/src/css/custom_style.css',
        ],
    },
    'license': 'AGPL-3'
}
