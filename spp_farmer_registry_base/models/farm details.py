from odoo import fields, models


# TODO: Maybe make it an event data that is displayed as a tab in the Farm
class FarmDetails(models.Model):
    _inherit = "res.partner"

    farm_id = fields.Many2one("res.partner", string="Farm")

    farm_type = fields.Selection(
        [
            ("crop", "Crop"),
            ("livestock", "Livestock"),
            ("aquaculture", "Aquaculture"),
            ("mixed", "Mixed"),
        ],
    )

    farm_total_size = fields.Float(string="Farm Size")
    # Acreage (Total, Under Crops, Under Livestock, Leased Out, Idle)
    # farm_total_size = fields.Float(string='Farm Size')
    farm_size_under_crops = fields.Float(string="Acreage Under Crops")
    farm_size_under_livestock = fields.Float(string="Acreage Under Livestock")
    farm_size_leased_out = fields.Float(string="Acreage Leased Out")
    farm_size_idle = fields.Float(string="Acreage Fallow/Idle")
