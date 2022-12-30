# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import _, fields, models


class SPPCreateEventWizard(models.TransientModel):
    _name = "spp.create.event.wizard"
    _description = "Create Event Wizard"

    event_data_model = fields.Selection(
        [("default", "")],
        "Event Type",
        default="default",
    )
    partner_id = fields.Many2one("res.partner", domain=[("is_registrant", "=", True)])
    registrar = fields.Char()
    collection_date = fields.Date(default=date.today())
    expiry_date = fields.Date()

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
                wizard_model = "%s.create." % wizard_list[0]
                wizard_list.pop(0)
                view_name = ""
                for split_wizard in wizard_list:
                    wizard_model += "%s." % split_wizard
                    view_name += "%s " % split_wizard.capitalize()
                wizard_model += "wizard"
                view_id = rec.get_view_id(wizard_model)
                # create the event data and pass it to event_data_model wizard
                vals_list = {
                    "model": model_name,
                    "partner_id": rec.partner_id.id,
                    "registrar": rec.registrar or False,
                    "collection_date": rec.collection_date or False,
                    "expiry_date": rec.expiry_date or False,
                }
                event_id = self.env["spp.event.data"].create(vals_list)

                wiz = self.env[wizard_model].create({"event_id": event_id.id})

                return {
                    "name": _("Create %s Wizard", view_name),
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
        return (
            self.env["ir.ui.view"]
            .search([("model", "=", model_name), ("type", "=", "form")], limit=1)
            .id
        )
