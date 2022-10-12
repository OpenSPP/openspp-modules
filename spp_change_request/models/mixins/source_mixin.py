# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ChangeRequestSourceMixin(models.AbstractModel):
    """Change Request Data Source mixin."""

    _name = "spp.change.request.source.mixin"
    _description = "Change Request Data Source Mixin"
    _rec_name = "change_request_id"

    registrant_id = fields.Many2one(
        "res.partner",
        "Registrant",
        domain=[("is_registrant", "=", True)],
        required=True,
    )
    change_request_id = fields.Many2one(
        "spp.change.request", "Change Request", required=True
    )

    def get_request_type_view_id(self):
        """Retrieve form view."""
        return (
            self.env["ir.ui.view"]
            .sudo()
            .search([("model", "=", self._name), ("type", "=", "form")], limit=1)
            .id
        )

    def _get_name(self):
        name = ""
        if self.family_name:
            name += self.family_name + ", "
        if self.given_name:
            name += self.given_name + " "
        if self.addl_name:
            name += self.addl_name + " "
        return name.title()
