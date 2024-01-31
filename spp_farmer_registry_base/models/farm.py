from odoo import fields, models


class Farm(models.Model):
    _inherit = "res.partner"

    coordinates = fields.Char(string="GPS Coordinates")
    farm_asset_ids = fields.One2many("spp.farm.asset", "farm_id", string="Farm Assets")
    farm_details_ids = fields.One2many("spp.farm.details", "farm_id", string="Farm Details")
    farm_land_rec_ids = fields.One2many("spp.land.record", "farm_id", string="Land Record")
    farm_extension_ids = fields.One2many("spp.farm.extension", "farm_id", string="Farm Extension Services")
    farm_agri_act_ids = fields.One2many("spp.farm.activity", "farm_id", string="Farm Agricultural Activities")
