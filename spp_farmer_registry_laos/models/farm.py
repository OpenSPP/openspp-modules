import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class Farm(models.Model):
    _inherit = "res.partner"

    farm_prod_ids = fields.One2many("spp.farm.activity", "prod_farm_id", string="Products")
    active_event_cycle = fields.Many2one("spp.event.data", compute="_compute_active_event_cycle")

    @api.depends("event_data_ids")
    def _compute_active_event_cycle(self):
        """
        This computes the active farm event of the group
        """
        for rec in self:
            rec.active_event_cycle = rec._get_active_event_id("spp.event.cycle")

    # overwrite for now since we will not create an individual per group in this module
    def create_update_farmer(self, farm):
        pass

    def open_create_event_wizard(self):
        for rec in self:
            model_name = "spp.event.cycle"
            # compute wizard model name

            wizard_list = model_name.split(".")
            wizard_model = "%s.create." % wizard_list[0]
            wizard_list.pop(0)
            view_name = self.env["ir.model"].search([("model", "=", model_name)]).name
            for split_wizard in wizard_list:
                wizard_model += "%s." % split_wizard
            wizard_model += "wizard"
            view_id = self.env.ref("spp_farmer_registry_laos.create_event_cycle_form_view").id
            # create the event data and pass it to event_data_model wizard
            vals_list = {
                "model": model_name,
                "partner_id": rec.id,
            }
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
