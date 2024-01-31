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
        string="Production system",
    )

    cultivation_chemical_interventions = fields.Selection(
        [
            ("fungicides", "Fungicides"),
            ("herbicides", "Herbicides"),
            ("insecticides", "Insecticides"),
            ("rodenticides", "Rodenticides"),
            ("other", "Other"),
        ],
        string="Chemical interventions",
    )

    cultivation_fertilizer_interventions = fields.Selection(
        [
            ("amonia anhydrous", "Amonia Anhydrous"),
            ("ammonium hydroxide", "Ammonium Hydroxide"),
            ("calcium nitrate", "Calcium Nitrate"),
            ("can", "CAN"),
            ("dap", "DAP"),
            ("double super phosphate", "Double Super Phosphate"),
            ("magnesium nitrate", "Magnesium Nitrate"),
            ("map", "MAP"),
            ("mop", "MOP"),
            ("npk", "NPK"),
            ("phosphate rock", "Phosphate Rock"),
            ("potassium nitrate", "Potassium Nitrate"),
            ("potassium sulphate", "Potassium Sulphate"),
            ("sulphate of ammonia", "Sulphate of Ammonia"),
            ("superphosphate", "Superphosphate"),
            ("tsp", "TSP"),
            ("urea", "Urea"),
            ("organic manure", "Organic Manure"),
            ("organic liquid fertilizer", "Organic Liquid Fertilizer"),
            ("other", "Other"),
        ],
        string="Fertilizer interventions",
    )

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
        string="Production system",
    )

    livestock_feed_items = fields.Selection(
        [
            ("natural pasture", "Natural Pasture"),
            ("improved pasture", "Improved Pasture"),
            ("own grown hay", "Own Grown Hay"),
            ("purchased hay", "Purchased Hay"),
            ("manufactured meals", "Manufactured Meals"),
            ("home-made feed mix", "Home-made Feed Mix"),
            ("chick mash", "Chick Mash"),
            ("calf pellets", "Calf Pellets"),
            ("mineral salts", "Mineral Salts"),
            ("purchased fodder", "Purchased Fodder"),
            ("pig starter-finisher", "Pig Starter-finisher"),
            ("other", "Other"),
        ],
        string="Feed items",
    )

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
        string="Production system",
    )
    aquaculture_number_of_fingerlings = fields.Integer(string="Number of fingerlings")

    @api.onchange("farm_id")
    def _onchange_farm_id(self):
        for rec in self:
            rec.land_id = False
