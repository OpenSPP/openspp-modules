from odoo import fields, models


class SPPDMSDirectoryCustom(models.Model):
    _inherit = "spp.dms.directory"

    change_request_change_info_id = fields.Many2one("spp.change.request.change.info", "Change request")


class SPPDMSFileCustom(models.Model):
    _inherit = "spp.dms.file"

    change_request_change_info_id = fields.Many2one("spp.change.request.change.info", "Change request")
