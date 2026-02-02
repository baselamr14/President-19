from odoo import api, fields, models


class AssetMoveWizard(models.TransientModel):
    _name = 'asset.move.wizard'

    asset_id = fields.Many2one(comodel_name="account.asset",)
    current_location_id = fields.Many2one(comodel_name="asset.location",related="asset_id.location_id")
    destination_location_id = fields.Many2one(comodel_name="asset.location",)
    note = fields.Text()

    def move_asset(self):
        self.asset_id.location_id = self.destination_location_id.id
        if self.note:
            self.asset_id.message_post(body=self.note)