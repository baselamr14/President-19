from odoo import api, fields, models,_
import qrcode
import base64
from io import BytesIO
from odoo.osv import expression
from odoo.exceptions import ValidationError, UserError



class AccountAsset(models.Model):
    _inherit = 'account.asset'

    image_1920 = fields.Image("Image", )
    #Many2one → relational field Points to model called asset.class.
    model_class_id = fields.Many2one(comodel_name="asset.class", string="Class",
                               domain="[('applicable_on_asset_model','=',True)]")
    #fields inside account.asset inside notebook
    description = fields.Text()
    responsible_id = fields.Many2one(comodel_name="hr.employee",)
    asset_class_id = fields.Many2one(comodel_name="asset.class", string="Asset Class",domain="[('applicable_on_asset', '=', True)]")
    location_id = fields.Many2one(comodel_name="asset.location", string="Asset Location",tracking=True)
    ##########################################################################################
    have_model_class = fields.Boolean()
    required_location = fields.Boolean(related="asset_class_id.require_location")
    print_qr = fields.Boolean(related="asset_class_id.print_qr")
    asset_code = fields.Char(copy=False)
    qr_code = fields.Binary("QR Code", attachment=True, store=True)
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company
    )

    _sql_constraints = [
        ('asset_code_uniq', 'unique(asset_code, company_id)', 'Asset Code must be unique per company!'),
    ]

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', operator, name), ('asset_code', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.asset_code)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_code = qr_image
        return qr_image

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'parent_id' in vals and vals['parent_id']:
                parent_asset = self.browse(vals['parent_id'])
                vals.update({'description':parent_asset.description,
                             'location_id':parent_asset.location_id.id,
                             'asset_class_id':parent_asset.asset_class_id.id,
                             'model_class_id':parent_asset.model_class_id.id,
                             'model_id':parent_asset.model_id.id,
                             'responsible_id':parent_asset.responsible_id.id,
                             })
        return super(AccountAsset, self).create(vals_list)

    def write(self, vals):
        result = super().write(vals)
        for child in self.children_ids:
            if 'description' in vals:
                child.description = vals['description']
            if 'responsible_id' in vals:
                child.responsible_id = vals['responsible_id']
            if 'account_asset_id' in vals:
                child.account_asset_id = vals['account_asset_id']
            if 'account_depreciation_id' in vals:
                child.account_depreciation_id = vals['account_depreciation_id']
            if 'account_depreciation_expense_id' in vals:
                child.account_depreciation_expense_id = vals['account_depreciation_expense_id']
        return result




    def validate(self):
        for rec in self:
            if not rec.asset_code and rec.asset_class_id:
                rec.asset_code = rec.asset_class_id.sequence_id.next_by_id()
        return super().validate()

    def action_validate(self):
        for rec in self:
            if rec.state == 'draft':
                rec.validate()

    @api.constrains('model_id')
    @api.onchange('model_id')
    def onchange_asset_model(self):
        if self.model_id.model_class_id:
            self.asset_class_id = self.model_id.model_class_id.id
            self.have_model_class = True
        else:
            self.have_model_class = False
            # return {'domain': {'asset_class_id': [('applicable_on_asset', '=', True)]}}

    def action_print_asset(self):
        records = self.filtered(lambda x: x.asset_class_id.print_qr)
        if any(rec.state != 'open' for rec in records):
            raise ValidationError(_('Sorry you can not Print records not in Running Status.'))
        return self.env.ref('ivs_asset_management.asset_qr_report').report_action(records)

    def action_asset_move(self):
        return {
            'name': _('Move Asset'),
            'type': 'ir.actions.act_window',
            'res_model': 'asset.move.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('ivs_asset_management.asset_move_form_view').id,
            'target': 'new',
            'context': {
                'default_asset_id': self.id,
            }
        }



