from odoo import fields, models


class SPPDMSDirectoryCustom(models.Model):
    _inherit = "spp.dms.directory"

    change_request_add_group_to_group_id = fields.Many2one("spp.change.request.add.group.to.group", "Change request")


class SPPDMSFileCustom(models.Model):
    _inherit = "spp.dms.file"

    change_request_add_group_to_group_id = fields.Many2one("spp.change.request.add.group.to.group", "Change request")
