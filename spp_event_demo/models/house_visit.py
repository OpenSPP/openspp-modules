# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class OpenSPPHouseVisit(models.Model):
    _name = "spp.event.house.visit"
    _description = "House Visit"

    summary = fields.Char()
    description = fields.Text()

    def get_view_id(self):
        """Retrieve form view."""
        return (
            self.env["ir.ui.view"]
            .search([("model", "=", self._name), ("type", "=", "form")], limit=1)
            .id
        )
