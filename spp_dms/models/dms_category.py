from odoo import fields, models


class SPPDMSCategory(models.Model):
    _name = "spp.dms.category"
    _description = "DMS Category"

    _order = "name asc"

    name = fields.Char(required=True, index="btree")
    file_ids = fields.One2many(
        comodel_name="spp.dms.file",
        inverse_name="category_id",
        string="Files",
        auto_join=False,
        copy=False,
    )
