from odoo import api, fields, models


# TODO: Look if there is an Odoo object we should extend instead of creating a new one
class FarmAsset(models.Model):
    _name = "spp.farm.asset"
    _description = "Farm Assets and Technology"

    asset_farm_id = fields.Many2one("res.partner", string="Asset Farm")
    machinery_farm_id = fields.Many2one("res.partner", string="Machinery Farm")
    land_id = fields.Many2one(
        "spp.land.record",
        string="Land",
        required=False,
        domain="[('farm_id', '=', farm_id)]",
    )

    asset_type = fields.Many2one("asset.type")
    machinery_type = fields.Many2one("machinery.type")
    technology_used = fields.Char()
    quantity = fields.Integer()
    machine_working_status = fields.Char("Working Status")

    @api.onchange("asset_farm_id")
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
