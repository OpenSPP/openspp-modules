from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SppApiFieldAlias(models.Model):
    _name = "spp_api.field.alias"
    _description = "Field Name Alias"
    _order = "api_path_id DESC, field_id, alias_name"

    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Field",
        required=True,
        ondelete="cascade",
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        related="field_id.model_id",
        store=True,
    )
    api_path_id = fields.Many2one(
        comodel_name="spp_api.path",
        string="API Path",
        ondelete="cascade",
    )
    # NOTE: 63 - PostgreSQL constraint name size capacity, no other special meaning
    alias_name = fields.Char(
        required=True,
        size=63,
    )
    global_alias = fields.Boolean(inverse="_inverse_global_alias")

    _sql_constraints = [
        (
            "field_api_path_uniq",
            "UNIQUE(field_id, api_path_id)",
            "Field only alias once in one API Path!",
        ),
        (
            "alias_name_api_path_uniq",
            "UNIQUE(alias_name, api_path_id)",
            "Alias name only exists once in one API Path!",
        ),
    ]

    @api.depends("alias_name", "field_id")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.alias_name} - {rec.field_id.name}"

    @api.constrains(
        "alias_name",
        "field_id",
    )
    def _check_field_name_alias_name(self):
        for rec in self:
            if rec.alias_name == rec.field_id.name:
                raise ValidationError(_("Alias Name should be different from its field name!"))

    @api.constrains("field_id", "api_path_id")
    def _check_field_duplicate_if_api_path_is_null(self):
        for rec in self:
            if rec.api_path_id:
                continue
            to_check = self.search(
                [
                    ("field_id", "=", rec.field_id.id),
                    ("api_path_id", "=", False),
                    ("id", "!=", rec.id),
                ],
                limit=1,
            )
            if to_check:
                raise ValidationError(_("There is another global alias for this field!"))

    def _inverse_global_alias(self):
        for rec in self:
            if rec.global_alias:
                rec.api_path_id = False
