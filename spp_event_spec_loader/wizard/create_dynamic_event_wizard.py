# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SPPCreateDynamicEventWizard(models.TransientModel):
    """Generic wizard for dynamically created event types"""

    _name = "spp.create.dynamic.event.wizard"
    _description = "Create Dynamic Event Wizard"

    event_id = fields.Many2one("spp.event.data", required=True)
    event_type_definition_id = fields.Many2one("spp.event.type.definition")

    # Generic fields that can be used for any event type
    x_name = fields.Char(string="Name")
    x_summary = fields.Char(string="Summary")
    x_description = fields.Text(string="Description")

    @api.model
    def _get_dynamic_fields_for_model(self, model_name):
        """Get field definitions for a dynamic model"""
        event_type_def = self.env["spp.event.type.definition"].search(
            [
                ("technical_name", "=", model_name),
                ("state", "=", "deployed"),
            ],
            limit=1,
        )

        if event_type_def and event_type_def.field_definitions:
            try:
                return json.loads(event_type_def.field_definitions)
            except json.JSONDecodeError:
                _logger.warning("Invalid field definitions for %s", model_name)

        return []

    def create_event(self):
        """Create the event record"""
        self.ensure_one()

        if not self.event_id:
            raise UserError(_("Event data record is required"))

        model_name = self.event_id.model

        if not model_name or model_name == "default":
            raise UserError(_("Please select an event type"))

        # Check if model exists
        model_obj = self.env["ir.model"].search([("model", "=", model_name)], limit=1)
        if not model_obj:
            raise UserError(_("Event type model '%s' not found", model_name))

        # Prepare values for the event record
        vals = {
            "x_name": self.x_name or self.x_summary or "New Event",
            "x_summary": self.x_summary or "",
            "x_description": self.x_description or "",
        }

        # Get dynamic field definitions
        event_type_def = self.env["spp.event.type.definition"].search(
            [
                ("technical_name", "=", model_name),
            ],
            limit=1,
        )

        if event_type_def and event_type_def.field_definitions:
            try:
                field_defs = json.loads(event_type_def.field_definitions)

                # For each defined field, try to get the value from the wizard
                for field_def in field_defs:
                    field_name = field_def.get("name")
                    if not field_name.startswith("x_"):
                        field_name = f"x_{field_name}"

                    # Check if this wizard has the field
                    if hasattr(self, field_name):
                        field_value = getattr(self, field_name)
                        if field_value is not None:
                            vals[field_name] = field_value
            except json.JSONDecodeError:
                _logger.warning("Invalid field definitions for %s", model_name)

        # Create the event record
        try:
            event = self.env[model_name].create(vals)
            self.event_id.res_id = event.id

            _logger.info("Created event record (ID: %s) for model %s", event.id, model_name)

            # Close the wizard
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Success"),
                    "message": _("Event created successfully"),
                    "type": "success",
                    "sticky": False,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        except Exception as e:
            _logger.exception("Failed to create event for model %s", model_name)
            raise UserError(_("Failed to create event: %s", str(e))) from e
