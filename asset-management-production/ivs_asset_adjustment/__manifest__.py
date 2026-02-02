# -*- coding: utf-8 -*-

{
    'name': 'Asset Adjustment',
    'version': '16.0.1',
    'category': 'Accounting',
    'summary': """
       Asset Adjustment
    """,
    'description': """This Module Manage Asset Adjustment""",
    'author': 'IValue Solutions Team',
    'depends': ['ivs_asset_management'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/asset_adjustment.xml',
        'reports/adjustment_report.xml',
        'wizards/asset_adjustment_wizard.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',
}