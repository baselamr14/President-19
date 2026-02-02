from odoo import models, fields

class AccountAsset(models.Model):
    _inherit = "account.asset"

    # Override base field to remove ORM required constraint
    prorata_date = fields.Date(required=False)

    # (Optional but recommended) ensure computation has a valid default in v19
    prorata_computation_type = fields.Selection(
        selection_add=[],
        default="none",
        required=False,
    )
