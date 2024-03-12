from odoo import fields, models


class IrUIView(models.Model):
    _inherit = "ir.ui.view"

    type = fields.Selection(
        selection_add=[("gis", "GIS")],
        ondelete={"gis": "cascade"},
    )

    raster_layer_ids = fields.One2many("spp.gis.raster.layer", "view_id", "Raster layers", required=False)

    data_layer_ids = fields.One2many("spp.gis.data.layer", "view_id", "Data layers", required=True)

    default_center = fields.Char("Default map center", default="[124.74037191, 7.83479874]")
    default_zoom = fields.Integer("Default map zoom", default=14)

    def _is_qweb_based_view(self, view_type):
        if view_type == "gis":
            return True
        return super()._is_qweb_based_view(view_type)
