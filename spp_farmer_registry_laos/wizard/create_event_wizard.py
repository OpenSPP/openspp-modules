# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class SPPCreateEventWizard(models.TransientModel):
    _inherit = "spp.create.event.wizard"

    event_data_model = fields.Selection(
        selection_add=[
            ("spp.event.cycle", "Event Cycle"),
            ("spp.event.gen.info", "II. General Information"),
            ("spp.event.poverty.indicator", "III. Poverty Indicators"),
            ("spp.event.hh.labor", "IV. Household Member and Labor Availability"),
            ("spp.event.hh.assets", "V. Household Assets"),
            ("spp.event.agri.land.ownership.use", "VI. Agriculture Land Ownership and Use"),
            ("spp.event.food.security", "VII. Food Security"),
            (
                "spp.event.agri.ws",
                "VIII. Agricultural Production, Sales, and Costs During the WS",
            ),
            (
                "spp.event.agri.tech.ws",
                "IX. Agricultural Technologies During the WS",
            ),
            (
                "spp.event.agri.ds",
                "X. Agricultural Production, Sales, Cost and Technologies During Cold DS",
            ),
            (
                "spp.event.agri.ds.hot",
                "XI. Agricultural Production, Sales, Costs and Technologies During the Hot DS",
            ),
            (
                "spp.event.permanent.crops",
                "XI. Permanent crops production",
            ),
            (
                "spp.event.livestock.farming",
                "XII. Livestock Farming",
            ),
            (
                "spp.event.inc.agri",
                "XIII. Income from Agribusiness (LAK)",
            ),
            (
                "spp.event.inc.non.agri",
                "XIV. Non-Agriculture Annual Income Sources (in LAK)",
            ),
        ]
    )

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
                view_name = self.env["ir.model"].search([("model", "=", model_name)]).name
                for split_wizard in wizard_list:
                    wizard_model += "%s." % split_wizard
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
                    "name": _(view_name),
                    "view_mode": "form",
                    "res_model": wizard_model,
                    "res_id": wiz.id,
                    "view_id": view_id,
                    "type": "ir.actions.act_window",
                    "target": "new",
                    "context": self.env.context,
                }
