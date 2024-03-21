from odoo import api, fields, models


class OpenSPPGisRasterLayer(models.Model):
    _name = "spp.gis.raster.layer"
    _description = "Raster Layer"

    RASTER_TYPE_CHOICES = [
        ("d_wms", "Distant WMS"),
        ("osm", "OpenStreetMap"),
        ("image", "Image"),
    ]

    RASTER_STYLE_CHOICES = [
        ("backdrop", "Backdrop"),
        ("backdrop-dark", "Backdrop-Dark"),
        ("backdrop-light", "Backdrop-Light"),
        ("basic", "Basic"),
        ("basic-dark", "Basic-Dark"),
        ("basic-light", "Basic-Light"),
        ("bright", "Bright"),
        ("bright-dark", "Bright-Dark"),
        ("bright-light", "Bright-Light"),
        ("bright-pastel", "Bright-Pastel"),
        ("dataviz", "Dataviz"),
        ("dataviz-dark", "Dataviz-Dark"),
        ("dataviz-light", "Dataviz-Light"),
        ("hybrid", "Hybrid"),
        ("ocean", "Ocean"),
        ("openstreetmap", "Openstreetmap"),
        ("outdoor", "Outdoor"),
        ("outdoor-dark", "Outdoor-Dark"),
        ("satellite", "Satellite"),
        ("streets", "Streets"),
        ("streets-dark", "Streets-Dark"),
        ("streets-light", "Streets-Light"),
        ("streets-pastel", "Streets-Pastel"),
        ("streets-night", "Streets-Night"),
        ("toner", "Toner"),
        ("toner-background", "Toner-Background"),
        ("toner-lite", "Toner-Lite"),
        ("toner-lines", "Toner-Lines"),
        ("topo", "Topo"),
        ("topo-shiny", "Topo-Shiny"),
        ("topo-pastel", "Topo-Pastel"),
        ("topo-topographique", "Topo-Topographique"),
        ("voyager", "Voyager"),
        ("voyager-dark", "Voyager-Dark"),
        ("voyager-light", "Voyager-Light"),
        ("voyager-vintage", "Voyager-Vintage"),
        ("winter", "Winter"),
        ("winter-dark", "Winter-Dark"),
    ]

    raster_type = fields.Selection(
        RASTER_TYPE_CHOICES,
        string="Raster layer type",
        default="osm",
        required=True,
    )
    name = fields.Char("Layer Name", translate=True, required=True)

    # technical field to display or not wms options
    is_wms = fields.Boolean(compute="_compute_is_wms")

    # wms options
    url = fields.Char("Service URL")
    wms_layer_name = fields.Char("WMS Layer Name")
    opacity = fields.Float(default=1.0)

    # osm options
    raster_style = fields.Selection(
        RASTER_STYLE_CHOICES,
        default="streets",
    )
    visible_on_load = fields.Boolean("Is visible on load?", default=True)

    # image options
    image_url = fields.Char()
    image_opacity = fields.Float(default=1.0)
    x_min = fields.Float(digits=(3, 15))
    x_max = fields.Float(digits=(3, 15))
    y_min = fields.Float(digits=(3, 15))
    y_max = fields.Float(digits=(3, 15))

    view_id = fields.Many2one("ir.ui.view", "Related View", domain=[("type", "=", "gis")], required=True)

    type_id = fields.Many2one("spp.gis.raster.layer.type", "Layer", domain="[('service', '=', raster_type)]")
    type = fields.Char(related="type_id.code")
    sequence = fields.Integer("Layer priority", default=6)

    @api.depends("raster_type")
    def _compute_is_wms(self):
        for rec in self:
            rec.is_wms = rec.raster_type == "d_wms"

    @api.onchange("raster_type")
    def _onchange_raster_type(self):
        for rec in self:
            rec.visible_on_load = rec.raster_type == "osm"
