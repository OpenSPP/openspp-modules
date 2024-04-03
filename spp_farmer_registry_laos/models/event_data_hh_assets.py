from odoo import fields, models


class EventDataHHAssets(models.Model):
    _name = "spp.event.hh.assets"
    _description = "Event Household Assets"

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
