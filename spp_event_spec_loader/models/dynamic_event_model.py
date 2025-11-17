# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class DynamicEventModelMixin(models.AbstractModel):
    """
    Mixin for dynamically created event models.
    Provides common functionality for all dynamic event types.
    """

    _name = "spp.dynamic.event.mixin"
    _description = "Dynamic Event Model Mixin"

    # Common fields that all dynamic event models should have
    name = fields.Char(string="Name", compute="_compute_name", store=True)

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

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        Compatible with spp_event_demo pattern
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id
