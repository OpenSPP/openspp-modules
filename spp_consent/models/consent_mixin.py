# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
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
        self.ensure_one()
        view = self.env.ref("spp_consent.record_consent_wizard_form_view")
        vals = {}
        if self.is_group:
            vals = {"group_id": self.id, "is_group": True}
        else:
            vals = {"signatory_id": self.id}
        wiz = self.env["spp.record.consent.wizard"].create(vals)

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
