# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class SPPEventMixin(models.AbstractModel):
    """
    Mixin for event type models.
    Provides common functionality for all event types.
    """

    _name = "spp.event.mixin"
    _description = "SPP Event Mixin"

    @api.model
    def _register_hook(self):
        """
        Mark this model as an event model automatically.
        All models inheriting from this mixin will be registered as event types.
        """
        super()._register_hook()
        ir_model = self.env["ir.model"].search([("model", "=", self._name)], limit=1)
        if ir_model and not ir_model.is_event_model:
            ir_model.sudo().write({"is_event_model": True})

    def get_view_id(self):
        """
        Retrieve the form view ID for this event model.
        This is used by the event wizard to open the appropriate form.
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id
