from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpenSPPGisDataLayer(models.Model):
    _name = "spp.gis.data.layer"
    _description = "Data Layer"
    _order = "sequence ASC, name"

    geo_repr = fields.Selection(
        [
            ("basic", "Basic"),
        ],
        default="basic",
        string="Representation mode",
        required=True,
    )

    name = fields.Char("Layer Name", translate=True, required=True)
    begin_color = fields.Char("Data Color ", required=False, help="hex value")
    geo_field_id = fields.Many2one(
        "ir.model.fields",
        "Geo field",
        required=True,
        ondelete="cascade",
        domain=[("ttype", "ilike", "geo_")],
    )
    model_id = fields.Many2one(
        "ir.model",
        "Model to use",
        store=True,
        readonly=False,
        compute="_compute_model_id",
    )
    model_name = fields.Char(related="model_id.model", readonly=True)

    view_id = fields.Many2one("ir.ui.view", "Related View", domain=[("type", "=", "gis")], required=True)
    sequence = fields.Integer("Layer Priority", default=6)
    active_on_startup = fields.Boolean(help="Layer will be shown on startup if checked.")
    layer_opacity = fields.Float(default=1.0)
    model_view_id = fields.Many2one(
        "ir.ui.view",
        "Model view",
        domain=[("type", "=", "gis")],
        compute="_compute_model_view_id",
        readonly=False,
    )
    layer_transparent = fields.Boolean()

    @api.constrains("geo_field_id", "model_id")
    def _check_geo_field_id(self):
        for rec in self:
            if rec.model_id:
                if not rec.geo_field_id.model_id == rec.model_id:
                    raise ValidationError(
                        _(
                            "The geo_field_id must be a field in %s model",
                            rec.model_id.display_name,
                        )
                    )

    @api.depends("model_id")
    def _compute_model_view_id(self):
        for rec in self:
            if rec.model_id:
                for view in rec.model_id.view_ids:
                    if view.type == "gis":
                        rec.model_view_id = view
            else:
                rec.model_view_id = ""

    @api.depends("geo_field_id", "view_id")
    def _compute_model_id(self):
        for rec in self:
            if rec.view_id and rec.geo_field_id:
                if rec.view_id.model == rec.geo_field_id.model:
                    rec.model_id = rec.geo_field_id.model_id
                else:
                    rec.model_id = ""
            else:
                rec.model_id = ""
