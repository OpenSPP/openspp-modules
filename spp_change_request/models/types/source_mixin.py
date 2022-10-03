# Part of OpenG2P. See LICENSE file for full copyright and licensing details.
from odoo import models


class ChangeRequestSourceMixin(models.AbstractModel):
    """Change Request Data Source mixin."""

    _name = "spp.change.request.source.mixin"
    _description = "Change Request Data Source Mixin"

    def get_request_type_view_id(self):
        """Retrieve form view."""
        return (
            self.env["ir.ui.view"]
            .search([("model", "=", self._name), ("type", "=", "form")], limit=1)
            .id
        )
