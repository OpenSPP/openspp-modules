# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import api, fields, models


class OpenSPPPhoneSurvey(models.Model):
    _name = "spp.event.phone.survey"
    _description = "Phone Survey"

    registrant = fields.Many2one(
        "res.partner", domain=[("is_group", "=", True), ("is_registrant", "=", True)]
    )
    summary = fields.Char()
    description = fields.Text()

    def get_view_id(self):
        """Retrieve form view."""
        return (
            self.env["ir.ui.view"]
            .search([("model", "=", self._name), ("type", "=", "form")], limit=1)
            .id
        )

    @api.model
    def create(self, vals):
        phone_survey = super(OpenSPPPhoneSurvey, self).create(vals)
        vals_list = [
            {
                "model": "spp.event.phone.survey",
                "res_id": phone_survey.id,
                "registrar": phone_survey.registrant.id,
                "collection_date": date.today(),
            }
        ]
        self.env["spp.event.data"].create(vals_list)
        return phone_survey
