from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AssetAdjustmentLine(models.Model):
    _name = 'asset.adjustment.line'
    _rec_name = 'adjustment_id'

    asset_location_id = fields.Many2one(comodel_name="asset.location", )
    asset_id = fields.Many2one(comodel_name="account.asset", domain="[('state','=,'open')]",string="Asset Name")
    asset_code = fields.Char(string="Asset Code")
    different_asset_location_id = fields.Many2one(comodel_name="asset.location", )
    is_exist = fields.Boolean(string="Existing", )
    adjustment_id = fields.Many2one(comodel_name="asset.adjustment", )

    @api.constrains('asset_id')
    def _check_asset_state(self):
        for rec in self:
            if rec.asset_id.state != 'open':
                raise ValidationError("You Can only adjust Asset in Running status")


class AssetAdjustment(models.Model):
    _name = 'asset.adjustment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char()
    location_id = fields.Many2one(comodel_name="asset.location", required=True,domain="[('company_id','=',company_id)]")
    date = fields.Date(default=fields.Date.context_today)
    method = fields.Selection(
        selection=[('current_location', 'Current Location'), ('current_sub_location', 'Current and Sub-Locations'), ],
        required=True, default='current_location')
    state = fields.Selection(selection=[('draft', 'Draft'), ('running', 'Running'), ('confirm', 'Confirmed'),
                                        ('approve', 'Approved'),('cancel', 'Cancelled')], default='draft',
                             tracking=True)
    line_ids = fields.One2many(comodel_name="asset.adjustment.line", inverse_name="adjustment_id", readonly=True)
    active = fields.Boolean(default=True)
    confirmed_user_id = fields.Many2one(comodel_name="res.users", string="Confirmed By",)
    approved_user_id = fields.Many2one(comodel_name="res.users", string="Approved By", )
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('asset.adjustment')
        return super(AssetAdjustment, self).create(vals)

    @api.constrains('active')
    def _check_approved_record(self):
        for rec in self:
            if not rec.active and rec.state == 'approve':
                raise ValidationError("Sorry can not Archive Record in Approved Status")

    def action_start(self):
        self.line_ids.unlink()
        if self.method == 'current_location':
            assets = self.env['account.asset'].search(
                [('state', '=', 'open'), ('location_id', '=', self.location_id.id)])
        else:
            assets = self.env['account.asset'].search(
                [('state', '=', 'open'), '|', ('location_id', '=', self.location_id.id),
                 ('location_id', 'in', self.location_id.child_ids.ids)])
        for asset in assets:
            self.env['asset.adjustment.line'].create({'adjustment_id': self.id,
                                                      'asset_id': asset.id,
                                                      'asset_location_id': asset.location_id.id})
        self.write({'state': 'running'})

    def action_confirm(self):
        self.write({'state': 'confirm',
                    'confirmed_user_id':self.env.user.id})

    def action_approve(self):
        self.write({'state': 'approve',
                    'approved_user_id':self.env.user.id})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    def start_adjustment(self):
        return {
            'name': _('Asset Adjustment'),
            'type': 'ir.actions.act_window',
            'res_model': 'asset.adjustment.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('ivs_asset_adjustment.asset_adjustment_wizard_form_view').id,
            'target': 'new',
            'context': {
                'default_adjustment_id': self.id,
            }
        }

    def unlink(self):
        if self.state in ['approve']:
            raise ValidationError(_('Sorry you can not delete records in Approved Status.'))
        return super(AssetAdjustment, self).unlink()
