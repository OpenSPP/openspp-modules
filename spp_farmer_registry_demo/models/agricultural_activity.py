from odoo import api, fields, models


class AgriculturalActivity(models.Model):
    _inherit = "spp.farm.activity"

    # Fields for Crop Rearing
    cultivation_water_source = fields.Selection(
        [("irrigated", "Irrigated"), ("rainfed", "Rainfed")],
        string="Water source",
    )
    cultivation_production_system = fields.Selection(
        [
            ("Mono-cropping", "Mono-cropping"),
            ("Mixed-cropping", "Mixed-cropping"),
            ("Agroforestry", "Agroforestry"),
            ("Plantation", "Plantation"),
            ("Greenhouse", "Greenhouse"),
        ],
        string="Cultivation Production system",
    )
    cultivation_chemical_interventions = fields.Many2many("spp.farm.chemical", string="Chemical interventions")
    cultivation_fertilizer_interventions = fields.Many2many("spp.fertilizer", string="Fertilizer interventions")

    # Fields for Livestock Rearing
    livestock_production_system = fields.Selection(
        [
            ("ranching", "Ranching"),
            ("communal grazing", "Communal Grazing"),
            ("pastoralism", "Pastoralism"),
            ("rotational grazing", "Rotational Grazing"),
            ("zero grazing", "Zero Grazing"),
            ("semi zero grazing", "Semi Zero Grazing"),
            ("feedlots", "Feedlots"),
            ("free range", "Free Range"),
            ("tethering", "Tethering"),
            ("other", "Other"),
        ],
        string="Livestock Production system",
    )
    livestock_feed_items = fields.Many2many("spp.feed.items", string="Feed items")

    # Fields for Aquaculture
    aquaculture_production_system = fields.Selection(
        [
            ("ponds", "Ponds"),
            ("cages", "Cages"),
            ("tanks", "Tanks"),
            ("raceways", "Raceways"),
            ("recirculating systems", "Recirculating Aquaculture Systems"),
            ("aquaponics", "Aquaponics"),
            ("other", "Other"),
        ],
        string="Aquaculture Production system",
    )
    aquaculture_number_of_fingerlings = fields.Integer(string="Number of fingerlings")

    @api.onchange("live_farm_id")
    def _onchange_farm_id(self):
        for rec in self:
            rec.land_id = False
