from odoo import api, fields, models


class SPPAPIField(models.Model):
    _name = "spp_api.field"
    _order = "sequence"
    _rec_name = "field_name"
    _description = "OpenAPI Field"

    sequence = fields.Integer()
    path_id = fields.Many2one("spp_api.path", required=True, ondelete="cascade")
    model_id = fields.Many2one(related="path_id.model_id", readonly=True)
    field_id = fields.Many2one(
        "ir.model.fields",
        required=True,
        ondelete="cascade",
        domain="[('model_id', '=', model_id),]",
    )
    field_name = fields.Char(related="field_id.name", readonly=True)
    description = fields.Char()
    force_required = fields.Boolean(string="Force Required", related="field_id.required", readonly=True)
    required = fields.Boolean()
    default_value = fields.Char()

    @api.onchange("field_id")
    def on_field_id_change(self):
        self.required = self.field_id.required

    @api.onchange("default_value")
    def on_default_value_change(self):
        if self.default_value:
            self.required = False

    @api.onchange("required")
    def on_required_change(self):
        if self.default_value:
            self.required = False

    def create_api_field_name_alias(self):
        self.ensure_one()
        return self.field_id.with_context(default_api_path_id=self.path_id.id).create_api_field_name_alias()

    def _get_field_name(self):
        self.ensure_one()
        field_alias = self.path_id._get_field_name_alias(self.field_id)
        return field_alias.alias_name if field_alias else self.field_name
