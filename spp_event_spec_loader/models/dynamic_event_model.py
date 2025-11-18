# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DynamicEventModelMixin(models.AbstractModel):
    """
    Mixin for dynamically created event models.
    Provides common functionality for all dynamic event types.
    Inherits from spp.event.mixin for standard event model behavior.
    Note: This mixin itself is not registered as an event type.
    """

    _name = "spp.dynamic.event.mixin"
    _inherit = "spp.event.mixin"
    _description = "Dynamic Event Model Mixin"

    # Common fields that all dynamic event models should have
    name = fields.Char(string="Name", compute="_compute_name", store=True)

    @api.model
    def _register_hook(self):
        """Override to prevent this mixin from registering itself"""
        # Don't register the dynamic mixin itself as an event model
        if self._name == "spp.dynamic.event.mixin":
            return

        # For actual event models, call parent which will register them
        return super()._register_hook()

    def _compute_name(self):
        """Compute a default name for the event"""
        for rec in self:
            # Try to find a summary or description field
            if hasattr(rec, "x_summary") and rec.x_summary:
                rec.name = rec.x_summary
            elif hasattr(rec, "x_name") and rec.x_name:
                rec.name = rec.x_name
            else:
                rec.name = f"{rec._description} - {rec.id}"
