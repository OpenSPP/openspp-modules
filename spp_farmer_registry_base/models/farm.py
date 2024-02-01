from odoo import fields, models


class Farm(models.Model):
    _inherit = "res.partner"
    _inherits = {'spp.land.record': 'farm_land_rec_id',
                 'spp.farm.details': 'farm_detail_id'}

    coordinates = fields.Char(string="GPS Coordinates")
    farm_asset_ids = fields.One2many("spp.farm.asset", "asset_farm_id", string="Farm Assets")
    farm_machinery_ids = fields.One2many("spp.farm.asset", "machinery_farm_id", string="Farm Machinery")
    farm_details_ids = fields.One2many("spp.farm.details", "details_farm_id", string="Farm Details")
    farm_land_rec_ids = fields.One2many("spp.land.record", "land_farm_id", string="Land Record")
    farm_extension_ids = fields.One2many("spp.farm.extension", "farm_id", string="Farm Extension Services")
    farm_crop_act_ids = fields.One2many("spp.farm.activity", "crop_farm_id", string="Crop Agricultural Activities")
    farm_live_act_ids = fields.One2many("spp.farm.activity", "live_farm_id", string="Livestock Agricultural Activities")
    farm_aqua_act_ids = fields.One2many("spp.farm.activity", "aqua_farm_id",
                                        string="Aquaculture Agricultural Activities")

    farm_asset_id = fields.Many2one("spp.farm.asset", string="Farm Asset")
    farm_detail_id = fields.Many2one("spp.farm.details", string="Farm Detail")
    farm_land_rec_id = fields.Many2one("spp.land.record", string="Land Record")

    def create_farm_records(self):
        for rec in self:
            farm_land_rec_id = self.env["spp.land.record"].create({"farm_id": rec.id})
            rec.farm_land_rec_id = farm_land_rec_id.id

