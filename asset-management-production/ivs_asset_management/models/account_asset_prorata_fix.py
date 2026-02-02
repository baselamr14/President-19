from odoo import models, fields

class AccountAsset(models.Model):
    _inherit = "account.asset"

    # remove ORM required constraint (server-side)
    prorata_date = fields.Date(required=False)
