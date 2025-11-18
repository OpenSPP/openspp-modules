# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

import logging
from datetime import date

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class SPPCreateEventWizard(models.TransientModel):
    _name = "spp.create.event.wizard"
    _description = "Create Event Wizard"

    @api.model
    def _get_event_data_model_selection(self):
        """
        Dynamically get event types from models marked as event models.
        Returns a list of tuples (model_name, model_display_name).
        Note: Mixins are prevented from registering via guards in their _register_hook.
        """
        # Start with default
        selection = [("default", "None")]

        # Query all models marked as event models
        # Note: We don't filter by state since dynamic models are state='manual'
        # Mixins are prevented from registering themselves via _register_hook guards
        event_models = self.env["ir.model"].search(
            [("is_event_model", "=", True)],
            order="name",
        )

        for event_model in event_models:
            selection.append((event_model.model, event_model.name))
            _logger.debug(
                "Added event type to wizard: %s (%s)",
                event_model.model,
                event_model.name,
            )

        return selection

    event_data_model = fields.Selection(
        selection="_get_event_data_model_selection",
        string="Event Type",
        default="default",
    )
    partner_id = fields.Many2one("res.partner", domain=[("is_registrant", "=", True)])
    registrar = fields.Char()
    collection_date = fields.Date(default=date.today())
    expiry_date = fields.Date()

    def get_event_data_vals(self):
        """
        This returns the event data values
        :return: Event Data Values
        """
        self.ensure_one()
        return {
            "model": self.event_data_model,
            "partner_id": self.partner_id.id,
            "registrar": self.registrar or False,
            "collection_date": self.collection_date or False,
            "expiry_date": self.expiry_date or False,
        }

    def next_page(self):
        """
        These set up the event data model then proceed to its view for the
        next step
        """
        for rec in self:
            if rec.event_data_model and not rec.event_data_model == "default":
                model_name = rec.event_data_model
                # compute wizard model name

                wizard_list = model_name.split(".")
                first_part = wizard_list[0]  # Save first part before popping
                wizard_model = "%s.create." % first_part
                wizard_list.pop(0)
                view_name = self.env["ir.model"].search([("model", "=", model_name)]).name
                for split_wizard in wizard_list:
                    wizard_model += "%s." % split_wizard
                wizard_model += "wizard"

                # Check if specific wizard exists
                wizard_exists = wizard_model in self.env

                if not wizard_exists:
                    # Try to find a generic wizard (for dynamic models)
                    # Dynamic models start with x_ and use underscores, so use 'spp' prefix
                    if first_part.startswith("x_"):
                        generic_wizard = "spp.create.dynamic.event.wizard"
                    else:
                        generic_wizard = "%s.create.dynamic.event.wizard" % first_part

                    if generic_wizard in self.env:
                        wizard_model = generic_wizard
                        _logger.info(
                            "Using generic wizard %s for model %s",
                            wizard_model,
                            model_name,
                        )
                    else:
                        _logger.warning(
                            "No wizard found for model %s, skipping wizard step",
                            model_name,
                        )
                        return

                view_id = rec.get_view_id(wizard_model)

                # create the event data and pass it to event_data_model wizard
                vals_list = rec.get_event_data_vals()
                event_id = self.env["spp.event.data"].create(vals_list)

                wiz = self.env[wizard_model].create({"event_id": event_id.id})

                return {
                    "name": _("Create %s", view_name),
                    "view_mode": "form",
                    "res_model": wizard_model,
                    "res_id": wiz.id,
                    "view_id": view_id,
                    "type": "ir.actions.act_window",
                    "target": "new",
                    "context": self.env.context,
                }

    def get_view_id(self, model_name):
        """
        This retrieves the Model View ID
        :param model_name: The Model.
        :return: Model View ID.
        """
        return self.env["ir.ui.view"].search([("model", "=", model_name), ("type", "=", "form")], limit=1).id
