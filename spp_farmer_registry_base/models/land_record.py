from odoo import fields, models, api


# We might move it to its own module
class LandRecord(models.Model):
    _name = "spp.land.record"
    _description = "Land Record Details"
    _record_name = "land_name"

    land_farm_id = fields.Many2one("res.partner", string="Farm")
    land_name = fields.Char(string="Parcel Name/ID")
    land_acreage = fields.Float()

    # TODO: Change to geo_point and geo_polygon
    land_coordinates = fields.Char()
    land_geo_polygon = fields.Char()

    land_use = fields.Selection(
        [
            ("cultivation", "Cultivation"),
            ("livestock", "Livestock"),
            ("aquaculture", "Aquaculture"),
            ("mixed", "Mixed Use"),
            ("fallow", "Fallow"),
            ("leased_out", "Leased Out"),
            ("other", "Other"),
        ],
    )

    # list of `spp.species`` for livestock and aquaculture
    # when land_use is mixed, do not restrict the species
    species = fields.Many2many(
        "spp.farm.species"
        # domain="['|',('species_type', '=', land_use),(land_use, '=', 'mixed')]",
    )
    species_domain = fields.Binary("Species Domain", compute="_compute_species_domain")

    cultivation_method = fields.Selection(
        [("irrigated", "Irrigated"), ("rainfed", "Rainfed")],
        help="Relevant if land use is cultivation or mixed",
    )

    @api.depends('land_use')
    def _compute_species_domain(self):
        for rec in self:
            species_domain = []
            if rec.land_use != 'mixed':
                species_domain = [('species_type', '=', rec.land_use)]

            rec.species_domain = species_domain

