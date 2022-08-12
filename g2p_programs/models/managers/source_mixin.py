# Part of Newlogic G2P. See LICENSE file for full copyright and licensing details.
from odoo import api, models


class ManagerSourceMixin(models.AbstractModel):
    """Manager Data Source mixin."""

    _name = "g2p.manager.source.mixin"
    _description = "Manager Data Source Mixin"

    @api.model
    def create(self, vals):
        """Override to update reference to source on the manager."""
        res = super().create(vals)
        # TODO: Seems not required but this causes error when called from the create program wizard.
        # Disable for now
        # if self.env.context.get("active_model"):
        #    # update reference on manager
        #    self.env[self.env.context["active_model"]].browse(
        #        self.env.context["active_id"]
        #    ).manager_id = res.id
        return res

    def get_manager_view_id(self):
        """Retrieve form view."""
        return (
            self.env["ir.ui.view"]
            .search([("model", "=", self._name), ("type", "=", "form")], limit=1)
            .id
        )
