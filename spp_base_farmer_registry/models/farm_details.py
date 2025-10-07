from odoo import fields, models


# TODO: Maybe make it an event data that is displayed as a tab in the Farm
class FarmDetails(models.Model):
    _name = "spp.farm.details"
    _description = "Farm Details"

    details_farm_id = fields.Many2one("res.partner", string="Details Farm")

    details_farm_type = fields.Selection(
        [
            ("crop", "Crop"),
            ("livestock", "Livestock"),
            ("aquaculture", "Aquaculture"),
            ("mixed", "Mixed"),
        ],
        string="Farm Type",
    )

    farm_total_size = fields.Float(string="Farm Size")
    # Acreage (Total, Under Crops, Under Livestock, Leased Out, Idle)
    # farm_total_size = fields.Float(string='Farm Size')
    farm_size_under_crops = fields.Float(string="Acreage Under Crops")
    farm_size_under_livestock = fields.Float(string="Acreage Under Livestock")
    farm_size_leased_out = fields.Float(string="Acreage Leased Out")
    farm_size_idle = fields.Float(string="Acreage Fallow/Idle")

    details_legal_status = fields.Selection(
        [
            ("self", "Owned by self"),
            ("family", "Owned by family"),
            ("extended community", "Owned by extended community"),
            ("cooperative", "Owned by cooperative"),
            ("government", "Owned by Government"),
            ("leased", "Leased from actual owner"),
            ("unknown", "Do not Know"),
        ],
        string="Legal Status",
    )
