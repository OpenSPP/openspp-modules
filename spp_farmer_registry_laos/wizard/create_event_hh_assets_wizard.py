# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class SPPCreateEventHHAssetsWizard(models.TransientModel):
    _name = "spp.create.event.hh.assets.wizard"
    _description = "V. Household Assets"

    event_id = fields.Many2one("spp.event.data")

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

    def create_event(self):
        for rec in self:
            vals_list = {
                "asset_non_agri_tv": rec.asset_non_agri_tv,
                "asset_non_agri_refrigerator": rec.asset_non_agri_refrigerator,
                "asset_non_agri_motobike": rec.asset_non_agri_motobike,
                "asset_non_agri_vehicle": rec.asset_non_agri_vehicle,
                "asset_non_agri_mobile_dev": rec.asset_non_agri_mobile_dev,
                "asset_non_agri_elec_gas_stove": rec.asset_non_agri_elec_gas_stove,
                "asset_non_agri_computer": rec.asset_non_agri_computer,
                "asset_non_agri_solar_panel": rec.asset_non_agri_solar_panel,
                "asset_non_agri_generator": rec.asset_non_agri_generator,
                "asset_non_agri_charcoal_stove": rec.asset_non_agri_charcoal_stove,
                "asset_non_agri_kerosene_stove": rec.asset_non_agri_kerosene_stove,
                "asset_non_agri_washing_machine": rec.asset_non_agri_washing_machine,
                "asset_non_agri_elec_pot": rec.asset_non_agri_elec_pot,
                "asset_non_agri_elec_water_boiler": rec.asset_non_agri_elec_water_boiler,
                "asset_non_agri_rice_cooker": rec.asset_non_agri_rice_cooker,
                "asset_non_agri_fan": rec.asset_non_agri_fan,
                "asset_non_agri_sewing_machine": rec.asset_non_agri_sewing_machine,
                "asset_agri_4wd_tractor": rec.asset_agri_4wd_tractor,
                "asset_agri_hand_tractor": rec.asset_agri_hand_tractor,
                "asset_agri_thresher": rec.asset_agri_thresher,
                "asset_agri_green_house": rec.asset_agri_green_house,
                "asset_agri_drying_facility": rec.asset_agri_drying_facility,
                "asset_agri_rice_mill": rec.asset_agri_rice_mill,
                "asset_agri_harvester": rec.asset_agri_harvester,
                "asset_agri_water_pump": rec.asset_agri_water_pump,
                "asset_agri_farm_truck_tractor": rec.asset_agri_farm_truck_tractor,
                "asset_agri_grass_cutter": rec.asset_agri_grass_cutter,
                "asset_agri_elec_wood_cutting": rec.asset_agri_elec_wood_cutting,
                "asset_agri_feed_pellet_extruder": rec.asset_agri_feed_pellet_extruder,
                "asset_livestock_buffalo": rec.asset_livestock_buffalo,
                "asset_livestock_cow_meat": rec.asset_livestock_cow_meat,
                "asset_livestock_cow_milk": rec.asset_livestock_cow_milk,
                "asset_livestock_goat": rec.asset_livestock_goat,
                "asset_livestock_pig": rec.asset_livestock_pig,
                "asset_livestock_piglets": rec.asset_livestock_piglets,
                "asset_livestock_paultry": rec.asset_livestock_paultry,
                "asset_livestock_aquatic_animals": rec.asset_livestock_aquatic_animals,
                "asset_livestock_frog": rec.asset_livestock_frog,
                "asset_livestock_horse": rec.asset_livestock_horse,
            }

            event = self.env["spp.event.hh.assets"].create(vals_list)
            rec.event_id.res_id = event.id

            return event
