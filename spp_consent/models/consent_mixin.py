# Part of Newlogic OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import _, fields, models


class OpenSPPConsentMixin(models.AbstractModel):
    """Consent mixin."""

    _name = "spp.consent.mixin"
    _description = "Consent Mixin"

    consent_ids = fields.Many2many("spp.consent", string="Consent IDS")

    def open_record_consent_wizard(self):
        """
        This method is used to open the consent wizard.
        :param view: The View ID.
        :param wiz: The Wizard.
        :return: This will return the action based on the params.
        """
        view = self.env.ref("spp_consent.record_consent_wizard_form_view")
        wiz = self.env["spp.record.consent.wizard"].create({"signatory_id": self.id})

        if self.is_group:
            view = self.env.ref("spp_consent.record_consent_wizard_form_view")
            wiz = self.env["spp.record.consent.wizard"].create(
                {"group_id": self.id, "is_group": True}
            )

        return {
            "name": _("Record Consent"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "spp.record.consent.wizard",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": wiz.id,
            "context": self.env.context,
        }
