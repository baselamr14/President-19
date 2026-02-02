from odoo import api, fields, models


class Sequence(models.Model):
    _inherit = 'ir.sequence'

    is_asset_class = fields.Boolean(string="Asset Class")