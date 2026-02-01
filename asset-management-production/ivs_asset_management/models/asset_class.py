from odoo import api, fields, models


class AssetClass(models.Model):
    _name = 'asset.class'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # def _get_default_font_size(self):
    #     font_size = self.width*37.795/10
    #     return font_size

    name = fields.Char(string="Asset Class",required=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    sequence_id = fields.Many2one(comodel_name="ir.sequence", string="Class Coding",
                                  domain="[('is_asset_class','=',True),'|',('company_id','=',False),('company_id','=',company_id)]")
    applicable_on_asset_model = fields.Boolean(string="Asset Model")
    applicable_on_asset = fields.Boolean(string="Asset")
    print_qr = fields.Boolean(string="QR Printing")
    width = fields.Float(default=5)
    height = fields.Float(default=5)
    font_size = fields.Float()
    require_location = fields.Boolean(string="Required Asset Location")

