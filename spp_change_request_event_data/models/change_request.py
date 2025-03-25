import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ChangeRequest(models.Model):
    _inherit = "spp.change.request"

    event_data_ids = fields.One2many(
        "spp.event.data",
        "change_request_id",
        string="Event History",
    )

    def write(self, vals):
        """Override to track state changes and create event data"""
        _logger.info("Writing change request: %s with vals: %s", self.name, vals)

        res = super().write(vals)

        # If state is changing to validated or applied, create/update event data
        new_state = vals.get("state")
        if new_state in ["validated", "applied"]:
            for record in self:
                if record.request_type_ref_id:
                    _logger.info("Creating/Updating event data for state change to %s", new_state)

                    # Get model and res_id from request_type_ref_id
                    ref_model = record.request_type_ref_id._name
                    ref_id = record.request_type_ref_id.id

                    # Get the user who performed the action
                    user = self.env.user.name

                    # Check if an event already exists for this change request
                    existing_event = self.env["spp.event.data"].search(
                        [("change_request_id", "=", record.id), ("model", "=", ref_model), ("res_id", "=", ref_id)],
                        limit=1,
                    )

                    event_vals = {
                        "model": ref_model,
                        "res_id": ref_id,
                        "partner_id": record.registrant_id.id,
                        "registrar": user,
                        "state": "active",
                        "change_request_id": record.id,
                        "collection_date": fields.Date.today(),
                        "event_type": new_state.capitalize(),  # 'Validated' or 'Applied'
                    }

                    if existing_event:
                        # Update existing event
                        existing_event.write(event_vals)
                        _logger.info("Updated event data: %s", existing_event.id)
                    else:
                        # Create new event
                        event = self.env["spp.event.data"].create(event_vals)
                        _logger.info("Created event data: %s", event.id)

        return res
