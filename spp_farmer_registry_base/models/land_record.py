from odoo import fields, models


# We might move it to its own module
class LandRecord(models.Model):
    _name = "spp.land.record"
    _description = "Land Record Details"

    farm_id = fields.Many2one("res.partner", string="Farm")
    name = fields.Char(string="Parcel Name/ID")
    acreage = fields.Float()

    # TODO: Change to geo_point and geo_polygon
    coordinates = fields.Char()
    geo_polygon = fields.Char()

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
        "spp.species",
        domain="[('species_type', '=', land_use)|(land_use, '=', 'mixed')]",
    )

    cultivation_method = fields.Selection(
        [("irrigated", "Irrigated"), ("rainfed", "Rainfed")],
        help="Relevant if land use is cultivation or mixed",
    )
