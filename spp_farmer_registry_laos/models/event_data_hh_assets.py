from odoo import api, fields, models


class EventDataHHAssets(models.Model):
    _name = "spp.event.hh.assets"
    _description = "V. Household Assets"

    survey_sched = fields.Selection(
        [("1", "Baseline"), ("2", "Midline"), ("3", "Endline")],
        string="Survey Schedule",
    )
    asset_non_agri_tv = fields.Integer("Number of TV")
    asset_non_agri_refrigerator = fields.Integer("Number of Refrigerator")
    asset_non_agri_motobike = fields.Integer("Number of Motobike")
    asset_non_agri_vehicle = fields.Integer("Number of Vehicle/Pickup")
    asset_non_agri_mobile_dev = fields.Integer("Number of Mobile Phone/Tablet")
    asset_non_agri_elec_gas_stove = fields.Integer("Number of Electric/Gas Stove")
    asset_non_agri_computer = fields.Integer("Number of Personal Computer")
    asset_non_agri_solar_panel = fields.Integer("Number of Solar Panel")
    asset_non_agri_generator = fields.Integer("Number of Generator")
    asset_non_agri_charcoal_stove = fields.Integer("Number of Charcoal Stove")
    asset_non_agri_kerosene_stove = fields.Integer("Number of Kerosene/Paraffin Stove")
    asset_non_agri_washing_machine = fields.Integer("Number of Clothes Washing Machine")
    asset_non_agri_elec_pot = fields.Integer("Number of Electric Pot")
    asset_non_agri_elec_water_boiler = fields.Integer("Number of Electric Water Boiler")
    asset_non_agri_rice_cooker = fields.Integer("Number of Electric Rice Cooker")
    asset_non_agri_fan = fields.Integer("Number of Fan")
    asset_non_agri_sewing_machine = fields.Integer("Number of Sewing Machine")

    asset_agri_4wd_tractor = fields.Integer("Number of 4 WD Tractor")
    asset_agri_hand_tractor = fields.Integer("Number of Hand Tractor")
    asset_agri_thresher = fields.Integer("Number of Thresher")
    asset_agri_green_house = fields.Integer("Number of Green House")
    asset_agri_drying_facility = fields.Integer("Number of Drying Facility")
    asset_agri_rice_mill = fields.Integer("Number of Rice Mill")
    asset_agri_harvester = fields.Integer("Number of Harvester")
    asset_agri_water_pump = fields.Integer("Number of Water Pump")
    asset_agri_farm_truck_tractor = fields.Integer("Number of Farm Truck Tractor")
    asset_agri_grass_cutter = fields.Integer("Number of Grass Cutter")
    asset_agri_elec_wood_cutting = fields.Integer("Number of Electric Wood Cutting")
    asset_agri_feed_pellet_extruder = fields.Integer("Number of Feed Pellet Extruder")

    asset_livestock_buffalo = fields.Integer("Number of Buffalo")
    asset_livestock_cow_meat = fields.Integer("Number of Cow (Meat)")
    asset_livestock_cow_milk = fields.Integer("Number of Cow (Milk)")
    asset_livestock_goat = fields.Integer("Number of Goat")
    asset_livestock_pig = fields.Integer("Number of Pig")
    asset_livestock_piglets = fields.Integer("Number of Piglets")
    asset_livestock_paultry = fields.Integer("Number of Poultry (Eggs/Chicken)")
    asset_livestock_aquatic_animals = fields.Integer("Number of Aquatic Animals (Fish, Shrimp)")
    asset_livestock_frog = fields.Integer("Number of Frog")
    asset_livestock_horse = fields.Integer("Number of Horse")

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id


class EventDataHHAssetsResPartner(models.Model):
    _inherit = "res.partner"

    active_event_hh_assets = fields.Many2one(
        "spp.event.hh.assets", compute="_compute_active_event_hh_assets", store=True
    )

    v_survey_schedule = fields.Selection(string="Survey Schedule", related="active_event_hh_assets.survey_sched")
    v_asset_non_agri_tv = fields.Integer("Number of TV", related="active_event_hh_assets.asset_non_agri_tv")
    v_asset_non_agri_refrigerator = fields.Integer(
        "Number of Refrigerator", related="active_event_hh_assets.asset_non_agri_refrigerator"
    )
    v_asset_non_agri_motobike = fields.Integer(
        "Number of Motobike", related="active_event_hh_assets.asset_non_agri_motobike"
    )
    v_asset_non_agri_vehicle = fields.Integer(
        "Number of Vehicle/Pickup", related="active_event_hh_assets.asset_non_agri_vehicle"
    )
    v_asset_non_agri_mobile_dev = fields.Integer(
        "Number of Mobile Phone/Tablet", related="active_event_hh_assets.asset_non_agri_mobile_dev"
    )
    v_asset_non_agri_elec_gas_stove = fields.Integer(
        "Number of Electric/Gas Stove", related="active_event_hh_assets.asset_non_agri_elec_gas_stove"
    )
    v_asset_non_agri_computer = fields.Integer(
        "Number of Personal Computer", related="active_event_hh_assets.asset_non_agri_computer"
    )
    v_asset_non_agri_solar_panel = fields.Integer(
        "Number of Solar Panel", related="active_event_hh_assets.asset_non_agri_solar_panel"
    )
    v_asset_non_agri_generator = fields.Integer(
        "Number of Generator", related="active_event_hh_assets.asset_non_agri_generator"
    )
    v_asset_non_agri_charcoal_stove = fields.Integer(
        "Number of Charcoal Stove", related="active_event_hh_assets.asset_non_agri_charcoal_stove"
    )
    v_asset_non_agri_kerosene_stove = fields.Integer(
        "Number of Kerosene/Paraffin Stove", related="active_event_hh_assets.asset_non_agri_kerosene_stove"
    )
    v_asset_non_agri_washing_machine = fields.Integer(
        "Number of Clothes Washing Machine", related="active_event_hh_assets.asset_non_agri_washing_machine"
    )
    v_asset_non_agri_elec_pot = fields.Integer(
        "Number of Electric Pot", related="active_event_hh_assets.asset_non_agri_elec_pot"
    )
    v_asset_non_agri_elec_water_boiler = fields.Integer(
        "Number of Electric Water Boiler", related="active_event_hh_assets.asset_non_agri_elec_water_boiler"
    )
    v_asset_non_agri_rice_cooker = fields.Integer(
        "Number of Electric Rice Cooker", related="active_event_hh_assets.asset_non_agri_rice_cooker"
    )
    v_asset_non_agri_fan = fields.Integer("Number of Fan", related="active_event_hh_assets.asset_non_agri_fan")
    v_asset_non_agri_sewing_machine = fields.Integer(
        "Number of Sewing Machine", related="active_event_hh_assets.asset_non_agri_sewing_machine"
    )

    v_asset_agri_4wd_tractor = fields.Integer(
        "Number of 4 WD Tractor", related="active_event_hh_assets.asset_agri_4wd_tractor"
    )
    v_asset_agri_hand_tractor = fields.Integer(
        "Number of Hand Tractor", related="active_event_hh_assets.asset_agri_hand_tractor"
    )
    v_asset_agri_thresher = fields.Integer("Number of Thresher", related="active_event_hh_assets.asset_agri_thresher")
    v_asset_agri_green_house = fields.Integer(
        "Number of Green House", related="active_event_hh_assets.asset_agri_green_house"
    )
    v_asset_agri_drying_facility = fields.Integer(
        "Number of Drying Facility", related="active_event_hh_assets.asset_agri_drying_facility"
    )
    v_asset_agri_rice_mill = fields.Integer(
        "Number of Rice Mill", related="active_event_hh_assets.asset_agri_rice_mill"
    )
    v_asset_agri_harvester = fields.Integer(
        "Number of Harvester", related="active_event_hh_assets.asset_agri_harvester"
    )
    v_asset_agri_water_pump = fields.Integer(
        "Number of Water Pump", related="active_event_hh_assets.asset_agri_water_pump"
    )
    v_asset_agri_farm_truck_tractor = fields.Integer(
        "Number of Farm Truck Tractor", related="active_event_hh_assets.asset_agri_farm_truck_tractor"
    )
    v_asset_agri_grass_cutter = fields.Integer(
        "Number of Grass Cutter", related="active_event_hh_assets.asset_agri_grass_cutter"
    )
    v_asset_agri_elec_wood_cutting = fields.Integer(
        "Number of Electric Wood Cutting", related="active_event_hh_assets.asset_agri_elec_wood_cutting"
    )
    v_asset_agri_feed_pellet_extruder = fields.Integer(
        "Number of Feed Pellet Extruder", related="active_event_hh_assets.asset_agri_feed_pellet_extruder"
    )

    v_asset_livestock_buffalo = fields.Integer(
        "Number of Buffalo", related="active_event_hh_assets.asset_livestock_buffalo"
    )
    v_asset_livestock_cow_meat = fields.Integer(
        "Number of Cow (Meat)", related="active_event_hh_assets.asset_livestock_cow_meat"
    )
    v_asset_livestock_cow_milk = fields.Integer(
        "Number of Cow (Milk)", related="active_event_hh_assets.asset_livestock_cow_milk"
    )
    v_asset_livestock_goat = fields.Integer("Number of Goat", related="active_event_hh_assets.asset_livestock_goat")
    v_asset_livestock_pig = fields.Integer("Number of Pig", related="active_event_hh_assets.asset_livestock_pig")
    v_asset_livestock_piglets = fields.Integer(
        "Number of Piglets", related="active_event_hh_assets.asset_livestock_piglets"
    )
    v_asset_livestock_paultry = fields.Integer(
        "Number of Poultry (Eggs/Chicken)", related="active_event_hh_assets.asset_livestock_paultry"
    )
    v_asset_livestock_aquatic_animals = fields.Integer(
        "Number of Aquatic Animals (Fish, Shrimp)", related="active_event_hh_assets.asset_livestock_aquatic_animals"
    )
    v_asset_livestock_frog = fields.Integer("Number of Frog", related="active_event_hh_assets.asset_livestock_frog")
    v_asset_livestock_horse = fields.Integer("Number of Horse", related="active_event_hh_assets.asset_livestock_horse")

    @api.depends("event_data_ids")
    def _compute_active_event_hh_assets(self):
        """
        This computes the active Household Member and Labor Availability event of the group
        """
        for rec in self:
            event_data = rec._get_active_event_id("spp.event.hh.assets")
            rec.active_event_hh_assets = None
            if event_data:
                event_data_res_id = self.env["spp.event.data"].search([("id", "=", event_data)], limit=1).res_id
                rec.active_event_hh_assets = (
                    self.env["spp.event.hh.assets"].search([("id", "=", event_data_res_id)], limit=1).id
                )
