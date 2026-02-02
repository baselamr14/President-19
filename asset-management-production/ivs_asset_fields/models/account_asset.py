from odoo import api, fields, models


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    original_value = fields.Monetary(string="Original Value", compute='_compute_value',
                                     store=True, states={'draft': [('readonly', False)]},help="Using As Current Value")
    org_val = fields.Monetary(string="Original Value", states={'draft': [('readonly', False)]})

    accumulated_depreciation = fields.Monetary(string="Accumulated Depreciation",
                                               states={'draft': [('readonly', False)]})


