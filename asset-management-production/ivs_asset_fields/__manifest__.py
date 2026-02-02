# -*- coding: utf-8 -*-

{
    'name': 'Asset Fields',
    'version': '16.0.1',
    'category': 'sales',
    'summary': """
        Asset Fields
    """,
    'description': """Change the field (Original Value) name to (Current Value)
                      Add 2 new optional monetary fields : Original Value,Accumulated Depreciation""",
    'author': 'IValue Solutions Team',
    'depends': ['base','account_asset'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_asset.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}