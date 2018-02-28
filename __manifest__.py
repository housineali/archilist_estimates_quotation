# -*- coding: utf-8 -*-
{
    'name': "Estimates and Quotation",

    'summary': """
        That module is for archilist estimations and quotations company""",
    'description': """
That module created for archilist company.
======================================
Key Features:
------------
* Client signup and request service for his property.
* system admin estimate the cost and send it to the client.
* After Client Acceptance admin contact with contractors to get offers to do that work. 
""",
    'author': 'Binary Labs LLC & Mahmoud Elmenshawy',
    'website': 'https://www.linkedin.com/in/mahmoudelmenshawy/',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Real State',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'auth_signup', 'mail', 'web_planner', 'web', 'portal','archilist_product'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/templates.xml',
        'views/setting_views.xml',
        'views/quotation_wizard.xml',
        'views/quotation_views.xml',
        'views/request_views.xml',
        'views/menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'application': True
}
