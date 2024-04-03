# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, Command



class SPPCreateEventAgriLandOwnershipAndUseWizard(models.TransientModel):
    _name = "spp.create.event.agri.land.ownership.use.wizard"
    _description = "VI. Agriculture Land Ownership and Use"

    event_id = fields.Many2one("spp.event.data")

    land_ownership_ids = fields.One2many(
        "spp.create.event.agri.land.ownership.use.lines.wizard", "land_ownership_use_id", string="Land Ownerships and Uses"
    )
    crops_in_irrigated_land = fields.Selection(
        [
            ("0", "There is no puddy"),
            ("1", "Did not plant"),
            ("2", "Planted (rice/ any other crops)"),
        ],
        string="Rice or any other crops in the irrigated/rainfed paddy field during dry season",
    )
    crops_in_irrigated_land_ha = fields.Float("Area of planting (ha)")

    def create_event(self):
        for rec in self:
            vals_list = {
                "crops_in_irrigated_land": rec.crops_in_irrigated_land,
                "crops_in_irrigated_land_ha": rec.crops_in_irrigated_land_ha,
            }
            if rec.land_ownership_ids:
                ownership_vals = []
                for ownership in rec.land_ownership_ids:
                    ownership_vals.append(
                        (Command.create(
                            {
                                "land_ownership": ownership.land_ownership,
                                "irrigated_puddy": ownership.irrigated_puddy,
                                "rainfed_puddy": ownership.rainfed_puddy,
                                "upland_agriculture": ownership.upland_agriculture,
                                "coffee_tea_plantation": ownership.coffee_tea_plantation,
                                "cardamom_plantation": ownership.cardamom_plantation,
                                "orchard": ownership.orchard,
                                "pasture": ownership.pasture,
                                "fallow_land": ownership.fallow_land,
                                "forest": ownership.forest,
                                "land_rent_oth_hh": ownership.land_rent_oth_hh,
                                "oth_agri_land_owned_by_hh": ownership.oth_agri_land_owned_by_hh,
                                "total": ownership.total,
                            }
                        ))
                    )

                vals_list.update({"land_ownership_ids": ownership_vals})

            event = self.env["spp.event.agri.land.ownership.use"].create(vals_list)
            rec.event_id.res_id = event.id

            return event


class SPPCreateEventAgriLandOwnershipAndUseLinesWizard(models.TransientModel):
    _name = "spp.create.event.agri.land.ownership.use.lines.wizard"
    _description = "VI. Agriculture Land Ownership and Use Lines"

    land_ownership_use_id = fields.Many2one("spp.create.event.agri.land.ownership.use.wizard",
                                            string="Land Ownership and Use")
    land_ownership = fields.Selection(
        [
            ("1", "Ownership (Land Title)"),
            ("2", "Land Use Certificate"),
            ("3", "Others"),
            ("4", "Land Rent from Other HH"),
        ],
        string="Land Ownership Type",
    )
    irrigated_puddy = fields.Float("Area of Irrigated Puddy (ha)")
    rainfed_puddy = fields.Float("Area of Rainfed Puddy (ha)")
    upland_agriculture = fields.Float("Area of Upland Agriculture (ha)")
    coffee_tea_plantation = fields.Float("Area of Coffee/Tea Plantation (ha)")
    cardamom_plantation = fields.Float("Area of Cardamom Plantation (ha)")
    orchard = fields.Float("Area of Orchard (Fruit Trees) (ha)")
    pasture = fields.Float("Area of Pasture (ha)")
    fallow_land = fields.Float("Area of Fallow Land (ha)")
    forest = fields.Float("Area of Forest (chap chong) (ha)")
    land_rent_oth_hh = fields.Float("Area of Land for Rent to Other HH (ha)")
    oth_agri_land_owned_by_hh = fields.Float("Area of Other Agriculture Land Owned by the HH (ha)")
    total = fields.Float("Total (ha)")
