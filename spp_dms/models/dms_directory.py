from odoo import fields, models


class SPPDMSDirectory(models.Model):
    _name = "spp.dms.directory"
    _description = "DMS Directory"

    _rec_name = "complete_name"
    _order = "complete_name"

    name = fields.Char("Directory Name", required=True)
