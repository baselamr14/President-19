from odoo import api, fields, models, _
import xlrd
import base64
from io import BytesIO
import xlsxwriter
from odoo.exceptions import UserError, ValidationError
from odoo import http
from odoo.http import request

class AssetAdjustmentWizard(models.TransientModel):
    _name = 'asset.adjustment.wizard'

    def _get_default_message(self):
        if self.env.user.lang == 'ar_001':
            message = "اذا كنت تستخدم جهاز الليزر لجرد الأصل، يمكنك اختيار 'يدوي' والمسح باستخدام الليزر"
        else:
            message = "If you are using a Handheld device, you may select the 'Manual' option, and scan using the laser beam."
        return message

    adjustment_id = fields.Many2one(comodel_name="asset.adjustment", )
    adjustment_method_web = fields.Selection(string="Method", selection=[('manual', 'Manually'), ('import', 'Excel Import')],
                                             required=True,default='manual')
    adjustment_method = fields.Selection(string="Method", selection=[('manual', 'Manually'), ('import', 'Excel Import'),
                            ('qr_scan', 'QR Scanning')], required=True,default='manual')
    code = fields.Char()
    excel_file = fields.Binary()
    sample_excel_file = fields.Binary()
    file_name = fields.Char('File Name')
    asset_id = fields.Many2one(comodel_name="account.asset", domain="[('state','=','open')]")
    asset_name = fields.Char('Asset Name')
    scanned_asset_ids = fields.Many2many(comodel_name="account.asset",string="Assets Name", )
    device = fields.Char('device Name')
    message = fields.Char(string='message',default=_get_default_message)
                          # default="If you are using a Handheld device, you may select the 'Manual' option, and scan using the laser beam.")

    @api.onchange('adjustment_method_web')
    @api.constrains('adjustment_method_web')
    def _set_adjustment_method(self):
        device_type = request.httprequest.user_agent.platform
        self.device = device_type
        if not device_type in ['ipad','iphone','android']:
            self.adjustment_method = self.adjustment_method_web

    @api.onchange('asset_id')
    def _scan_asset(self):
        if self.asset_id and self.adjustment_method == 'qr_scan':
            self.action_done()
            self.scanned_asset_ids = [(4, self.asset_id.id)]
            self.asset_id = False

    def _check_asset_code(self, code):
        asset_line = self.adjustment_id.line_ids.filtered(lambda x: x.asset_id.asset_code == code)
        if asset_line and asset_line.asset_location_id:
            asset_line.write({'asset_code': code,
                              'is_exist': True})
        elif asset_line.asset_id.location_id.id == self.adjustment_id.location_id.id or asset_line.asset_id.location_id.id in self.adjustment_id.location_id.child_ids.ids:
            asset_line.write({'asset_code': code,
                              'asset_location_id': asset_line.asset_id.location_id.id,
                              'different_asset_location_id': False,
                              'is_exist': True})
        elif asset_line:
            asset_line.write({'asset_code': code})
        else:
            asset = self.env['account.asset'].search([('asset_code', '=', code)], limit=1)
            if asset:
                self.env['asset.adjustment.line'].create({'asset_id': asset.id,
                                                          'asset_code': code,
                                                          'different_asset_location_id': asset.location_id.id,
                                                          'adjustment_id': self.adjustment_id.id})

    def generate_sample_excel_file(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Assets')
        sheet.set_column(0, 1, 20)
        header = workbook.add_format({
            'bold': 1,
            'border': 1,
            'font_size': '12',
            'align': 'center',
        })
        sheet.write(0, 0, 'Asset Code', header)
        for row in range(1, 12, 3):
            sheet.write(row, 0, 'TV/0001', )
            row += 1
            sheet.write(row, 0, 'TV/0002', )
            row += 1
            sheet.write(row, 0, 'TV/0003', )
            row += 1
        workbook.close()
        output.seek(0)
        # self.write({'sample_excel_file': base64.encodestring(output.getvalue())})
        self.write({'sample_excel_file': base64.b64encode(output.read())})
        return {
            'type': 'ir.actions.act_url',
            'name': 'Sample Adjustment Sheet',
            'url': '/web/content/asset.adjustment.wizard/%s/sample_excel_file/SampleSheet.xlsx?download=true' % (
                self.id),
            'target': 'self'
        }

    @api.constrains('file_name')
    def check_import_excel_file(self):
        if self.file_name:
            extension = self.file_name.split(".")
            if extension and extension[-1] != 'xlsx':
                raise ValidationError("Sorry File extension should be .xlsx !")

    def import_adjustment_sheet(self):
        if self.excel_file:
            book = xlrd.open_workbook(file_contents=base64.b64decode(self.excel_file))
            sheet = book.sheet_by_index(0)
            for row in range(1, sheet.nrows):
                self._check_asset_code(sheet.cell(row, 0).value)

    def action_done(self):
        if self.adjustment_method == 'manual':
            self._check_asset_code(self.code)
        elif self.adjustment_method == 'qr_scan':
            self._check_asset_code(self.asset_id.asset_code)
        return {
            'name': _('Asset Adjustment'),
            'type': 'ir.actions.act_window',
            'res_model': 'asset.adjustment.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('ivs_asset_adjustment.asset_adjustment_wizard_form_view').id,
            'target': 'new',
            'context': {
                'default_adjustment_id': self.adjustment_id.id,
                'default_adjustment_method': self.adjustment_method,
            }
        }
