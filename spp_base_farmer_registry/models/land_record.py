from odoo import api, fields, models


class LandRecord(models.Model):
    _inherit = "spp.land.record"

    species = fields.Many2many(
        "spp.farm.species",
        # domain="['|',('species_type', '=', land_use),(land_use, '=', 'mixed')]",
    )
    species_domain = fields.Binary(compute="_compute_species_domain")

    cultivation_method = fields.Selection(
        [("irrigated", "Irrigated"), ("rainfed", "Rainfed")],
        help="Relevant if land use is cultivation or mixed",
    )

    @api.depends("land_use")
    def _compute_species_domain(self):
        for rec in self:
            species_domain = []
            if rec.land_use != "mixed":
                species_domain = [("species_type", "=", rec.land_use)]
            rec.species_domain = species_domain
