# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import api, fields, models


class OpenSPPHouseVisit(models.Model):
    _name = "spp.event.house.visit"
    _description = "House Visit"

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
        house_visit = super(OpenSPPHouseVisit, self).create(vals)
        vals_list = [
            {
                "model": "spp.event.house.visit",
                "res_id": house_visit.id,
                "registrar": house_visit.registrant.id,
                "collection_date": date.today(),
            }
        ]
        self.env["spp.event.data"].create(vals_list)
        return house_visit
