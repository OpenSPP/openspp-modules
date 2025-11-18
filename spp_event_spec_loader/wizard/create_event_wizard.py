# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class SPPCreateEventWizard(models.TransientModel):
    _inherit = "spp.create.event.wizard"

    @api.model
    def _get_event_data_model_selection(self):
        """Dynamically get event types from deployed event type definitions"""
        # Start with default
        selection = [("default", "None")]

        # Add all deployed event types from spp.event.type.definition
        event_type_defs = self.env["spp.event.type.definition"].search(
            [
                ("state", "=", "deployed"),
                ("model_deployed", "=", True),
            ]
        )

        for event_type in event_type_defs:
            model_name = event_type.technical_name
            # Ensure the model exists
            model_exists = self.env["ir.model"].search([("model", "=", model_name)], limit=1)
            if model_exists:
                selection.append((model_name, event_type.name))
                _logger.debug("Added event type to wizard: %s (%s)", model_name, event_type.name)

        return selection

    event_data_model = fields.Selection(
        selection="_get_event_data_model_selection",
        string="Event Type",
        default="default",
    )

    def next_page(self):
        """Override to handle dynamic event types"""
        for rec in self:
            if rec.event_data_model and not rec.event_data_model == "default":
                model_name = rec.event_data_model

                # Check if this is a dynamically created model
                event_type_def = self.env["spp.event.type.definition"].search(
                    [
                        ("technical_name", "=", model_name),
                        ("state", "=", "deployed"),
                    ],
                    limit=1,
                )

                if event_type_def:
                    # This is a dynamic model - use the generic wizard
                    _logger.info("Using generic wizard for dynamic model: %s", model_name)

                    # Create the event data
                    vals_list = rec.get_event_data_vals()
                    event_id = self.env["spp.event.data"].create(vals_list)

                    # Use generic dynamic event wizard
                    wizard_model = "spp.create.dynamic.event.wizard"
                    view_id = rec.get_view_id(wizard_model)

                    wiz = self.env[wizard_model].create(
                        {
                            "event_id": event_id.id,
                            "event_type_definition_id": event_type_def.id,
                        }
                    )

                    return {
                        "name": _("Create %s", event_type_def.name),
                        "view_mode": "form",
                        "res_model": wizard_model,
                        "res_id": wiz.id,
                        "view_id": view_id,
                        "type": "ir.actions.act_window",
                        "target": "new",
                        "context": self.env.context,
                    }
                else:
                    # Not a dynamic model - use default behavior
                    return super().next_page()

        return super().next_page()
