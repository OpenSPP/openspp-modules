# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class SPPCreateEventWizard(models.TransientModel):
    _name = "spp.create.event.wizard"
    _description = "Create Event Wizard"

    event_data_model = fields.Selection(
        [("default", "")],
        "Event Data Model",
        default="default",
    )
    registrant = fields.Many2one(
        "res.partner", domain=[("is_group", "=", True), ("is_registrant", "=", True)]
    )

    def next_page(self):
        for rec in self:
            if rec.event_data_model:
                if not rec.event_data_model == "default":
                    event_data_model = rec.event_data_model
                    event_data_model = event_data_model.replace(".", "_")
                    model_list = event_data_model.split("_")
                    model_list.pop(0)
                    model_view = "%s.create_" % event_data_model
                    for split_model in model_list:
                        model_view += "%s_" % split_model

                    model_view += "form_view"
                    view = self.env.ref(model_view)

                    wizard_list = event_data_model.split("_")
                    wizard_model = "%s.create." % wizard_list[0]
                    wizard_list.pop(0)
                    view_name = ""
                    for split_wizard in wizard_list:
                        wizard_model += "%s." % split_wizard
                        view_name += "%s " % split_wizard.capitalize()
                    wizard_model += "wizard"

                    vals_list = {"registrant": rec.registrant.id}
                    wiz = self.env[wizard_model].create(vals_list)
                    return {
                        "name": _("Create %s Wizard" % view_name),
                        "view_mode": "form",
                        "res_model": wizard_model,
                        "res_id": wiz.id,
                        "view_id": view.id,
                        "type": "ir.actions.act_window",
                        "target": "new",
                        "context": self.env.context,
                    }
