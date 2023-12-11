from odoo import _, api, models
from odoo.exceptions import ValidationError


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    @api.depends_context("default_api_path_id")
    def create_api_field_name_alias(self):
        self.ensure_one()
        api_path_id = self._context.get("default_api_path_id")
        if not api_path_id:
            raise ValidationError(_("API path is not specify!"))
        field_alias_sudo = self.env["spp_api.field.alias"].sudo()
        res = {
            "type": "ir.actions.act_window",
            "name": _("Field Name Alias"),
            "res_model": field_alias_sudo._name,
            "view_mode": "form",
            "target": "new",
            "context": dict(self._context, scoped_alias=True, default_field_id=self.id),
        }
        defined_field_alias = field_alias_sudo.search(
            [
                ("field_id", "=", self.id),
                ("api_path_id", "=", api_path_id),
            ],
            limit=1,
        )
        if defined_field_alias:
            res["res_id"] = defined_field_alias.id
        return res
