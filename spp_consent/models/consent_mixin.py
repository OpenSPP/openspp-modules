# Part of Newlogic OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import _, fields, models


class OpenSPPConsentMixin(models.AbstractModel):
    """Consent mixin."""

    _name = "spp.consent.mixin"
    _description = "Consent Mixin"

    consent_ids = fields.Many2many("spp.consent", string="Consent IDS")

    def open_create_consent_wizard(self):
        view = self.env.ref("spp_consent.create_consent_wizard_form_view")
        wiz = self.env["spp.create.consent.wizard"].create({"signatory_id": self.id})
        return {
            "name": _("Create Consent"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "spp.create.consent.wizard",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": wiz.id,
            "context": self.env.context,
        }
