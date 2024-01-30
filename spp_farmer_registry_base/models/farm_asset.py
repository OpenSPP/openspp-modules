from odoo import api, fields, models


# TODO: Look if there is an Odoo object we should extend instead of creating a new one
class FarmAsset(models.Model):
    _name = "farm.asset"
    _description = "Farm Assets and Technology"

    farm_id = fields.Many2one("res.partner", string="Farm", required=True)
    land_id = fields.Many2one(
        "spp.land.record",
        string="Land",
        required=False,
        domain="[('farm_id', '=', farm_id)]",
    )

    asset_type = fields.one2many("equipment.type", "farm_asset_id")
    machinery_type = fields.one2many("machinery.type", "farm_asset_id")
    technology_used = fields.Char()
    quantity = fields.Integer()

    @api.onchange("farm_id")
    def _onchange_farm_id(self):
        for rec in self:
            rec.land_id = False


class AssetType(models.Model):
    _name = "asset.type"
    _description = "Asset Type"

    name = fields.Char(string="Asset Type")


class MachineryType(models.Model):
    _name = "machinery.type"
    _description = "Machinery Type"

    name = fields.Char(string="Machinery Type")
