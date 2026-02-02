# -*- coding: utf-8 -*-

{
    'name': 'Asset Management',
    'version': '16.0.1',
    'category': 'Accounting',
    'summary': """
       Asset Management
    """,
    'description': """This Module Manage asset model,asset class and asset location""",
    'author': 'IValue Solutions Team',
    'depends': ['account_accountant', 'account_asset', 'hr','base_automation'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_sequence.xml',
        'data/automated_action.xml',
        'views/ir_sequence.xml',
        'views/account_asset.xml',
        'views/asset_class.xml',
        'views/asset_location.xml',
'views/account_asset_prorata_fix.xml',
        'reports/asset_report.xml',
        'wizards/asset_move_wizard.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}
