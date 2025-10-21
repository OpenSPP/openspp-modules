from odoo import fields, models


# TODO: Look if there is an Odoo object we should extend instead of creating a new one
class FarmAsset(models.Model):
    _inherit = "spp.farm.asset"
    _description = "Farm Assets and Technology"

    # Aquaculture
    number_active = fields.Integer()
    active_area = fields.Float()
    active_volume = fields.Float()

    number_inactive = fields.Integer()
    inactive_area = fields.Float()
    inactive_volume = fields.Float()
