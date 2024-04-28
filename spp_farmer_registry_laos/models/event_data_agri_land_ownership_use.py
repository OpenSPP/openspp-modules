from odoo import api, fields, models


class OpenSPPEventDataAgriLandOwnershipAndUse(models.Model):
    _name = "spp.event.agri.land.ownership.use"
    _description = "VI. Agriculture Land Ownership and Use"

    survey_sched = fields.Selection(
        [("1", "Baseline"), ("2", "Midline"), ("3", "Endline")],
        string="Survey Schedule",
    )
    land_ownership_ids = fields.One2many(
        "spp.event.agri.land.ownership.use.lines", "land_ownership_use_id", string="Land Ownerships and Uses"
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

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id


class OpenSPPEventDataAgriLandOwnershipAndUseLines(models.Model):
    _name = "spp.event.agri.land.ownership.use.lines"
    _description = "Agriculture Land Ownership and Use Lines"

    land_ownership_use_id = fields.Many2one("spp.event.agri.land.ownership.use", string="Land Ownership and Use")
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


class OpenSPPEventDataAgriLandOwnershipAndUseResPartner(models.Model):
    _inherit = "res.partner"

    active_event_agri_land_ownership_use = fields.Many2one(
        "spp.event.agri.land.ownership.use",
        compute="_compute_active_event_agri_land_ownership_use",
        store=True
    )

    vi_survey_schedule = fields.Selection(
        string="Survey Schedule", related="active_event_agri_land_ownership_use.survey_sched"
    )
    vi_land_ownership_ids = fields.One2many(
        "spp.event.agri.land.ownership.use.lines", related="active_event_agri_land_ownership_use.land_ownership_ids"
    )
    vi_crops_in_irrigated_land = fields.Selection(
        string="Rice or any other crops in the irrigated/rainfed paddy field during dry season",
        related="active_event_agri_land_ownership_use.crops_in_irrigated_land",
    )
    vi_crops_in_irrigated_land_ha = fields.Float(
        "Area of planting (ha)", related="active_event_agri_land_ownership_use.crops_in_irrigated_land_ha"
    )

    @api.depends("event_data_ids")
    def _compute_active_event_agri_land_ownership_use(self):
        """
        This computes the active Agriculture Land Ownership and Use event of the group
        """
        for rec in self:
            event_data = rec._get_active_event_id("spp.event.agri.land.ownership.use")
            rec.active_event_agri_land_ownership_use = None
            if event_data:
                event_data_res_id = self.env["spp.event.data"].search([("id", "=", event_data)], limit=1).res_id
                rec.active_event_agri_land_ownership_use = (
                    self.env["spp.event.agri.land.ownership.use"].search([("id", "=", event_data_res_id)], limit=1).id
                )
