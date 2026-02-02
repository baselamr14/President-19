from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AssetLocation(models.Model):
    _name = 'asset.location'
    _parent_name = "parent_id"
    _parent_store = True
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Location Name", required=1)
    code = fields.Char(string="Location Code", required=False,copy=False)
    parent_id = fields.Many2one(comodel_name="asset.location", string="Parent Location",domain="[('name','!=',name)]")
    sub_locations = fields.Html('Sub-Locations')
    parent_path = fields.Char(index=True, unaccent=False)
    child_ids = fields.One2many(comodel_name="asset.location", inverse_name="parent_id",)
    asset_ids = fields.One2many(comodel_name="account.asset", inverse_name="location_id",)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    @api.constrains('code')
    def _check_unique_code(self):
        res = self.search_count([('code','=',self.code)])
        if res > 1:
            raise ValidationError("Sorry Location Code already exists.")

    @api.constrains('parent_id','company_id')
    def _check_parent_company(self):
        for rec in self:
            if rec.parent_id and rec.company_id != rec.parent_id.company_id:
                raise ValidationError("Parent Location belong to another Company! ")

    def _onchange_parent_location(self):
        for location in self.child_ids:
            location.write({'company_id': self.company_id.id})


    # < ul >
    # < li > < strong > < span style = "font-size: 18px;" > test < / span > < / strong > < / li >
        # < li class ="oe-nested" >
        #     < ul >
        #     < li > - < / li >
        #     < li > - < / li >
        #     < / ul >
        # < / li >
    # < li > < strong > < span style = "font-size: 18px;" > test 2 < / span > < / strong > < / li >
    #     < li class ="oe-nested" >
    #     < ul >
    #     < li > - < / li >
    #     < li > - < br > < / li >
    #     < / ul >
    #     < / li >
    # < li >
    # < a href="/web#id=2&amp;cids=1&amp;menu_id=246&amp;action=382&amp;model=asset.location&amp;view_type=form" >
    # < span style="font-size: 24px;" > Location1 < / span > < / a >
    # < / li >
    # < / ul > < p style="margin-bottom: 0px;" > < br > < / p > < p style="margin-bottom: 0px;" > < br > < / p >

