from odoo import fields, models


class SPPDMSDirectoryCustom(models.Model):
    _inherit = "spp.dms.directory"

    change_request_add_children_id = fields.Many2one("spp.change.request.add.children", "Change request")


class SPPDMSFileCustom(models.Model):
    _inherit = "spp.dms.file"

    change_request_add_children_id = fields.Many2one("spp.change.request.add.children", "Change request")
