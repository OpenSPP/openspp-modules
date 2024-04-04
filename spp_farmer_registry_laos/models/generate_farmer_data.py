import hashlib
import json
import logging
import math
import random
from datetime import date, timedelta

from odoo import Command, api, fields, models

from ..tools import generate_polygon, random_location_in_laos

_logger = logging.getLogger(__name__)

NAMES = [
    "Aguta",
    "Aprot",
    "Arusei",
    "Ayabei",
    "Barkutwo",
    "Barmasai",
    "Barngetuny",
    "Barsosio",
    "Bethwell",
    "Bitok",
    "Busendich",
    "Changeywo",
    "Cheboi",
    "Cheboiboch",
    "Cheboror",
    "Chege",
    "Chelangat",
    "Chelule",
    "Chemjor",
    "Chemlany",
    "Chemoiywo",
    "Chemosin",
    "Chemutai",
    "Chenonge",
    "Chepchirchir",
    "Chepkemei",
    "Chepkesis",
    "Chepkorir",
    "Chepkosgei",
    "Chepkurui",
    "Cheprot",
    "Cheptais",
    "Chepyego",
    "Cherigat",
    "Cherotich",
    "Cheyech",
    "Cheywa",
    "Chirlee",
    "Dickson",
    "Ebuya",
    "Eyapan",
    "Gitahi",
    "Gwako",
    "Jebet",
    "Jebiwott",
    "Jemaiyo",
    "Jepkesho",
    "Jepkirui",
    "Jerop",
    "Kabiga",
    "Kagika",
    "Kamathi",
    "Kamau",
    "Kamworor",
    "Kandie",
    "Kaptich",
    "Karoki",
    "Kasimili",
    "Kataron",
    "Kibore",
    "Kibowen",
    "Kilel",
    "Kimani",
    "Kimeli",
    "Kimemia",
    "Kimobwa",
    "Kimurgor",
    "Kimwei",
    "Kinuthia",
    "Kinyanjui",
    "Kinyor",
    "Kiogora",
    "Kipkoskei",
    "Kiplitany",
    "Kipsiele",
    "Kipterege",
    "Kirwa",
    "Kisorio",
    "Kithuka",
    "Kitur",
    "Kitwara",
    "Kiyara",
    "Kiyeng",
    "Kogo",
    "Koinange",
    "Komen",
    "Korikwiang",
    "Kororia",
    "Koskei",
    "Kotut",
    "Kurgat",
    "Kuria",
    "Kwalia",
    "Kwambai",
    "Kwemoi",
    "Larabal",
    "Lelei",
    "Lesuuda",
    "Limo",
    "Longosiwa",
    "Loroupe",
    "Loyanae",
    "Magut",
    "Maina",
    "Makau",
    "Malakwen",
    "Masai",
    "Mburu",
    "Moiben",
    "Mugo",
    "Mumbi",
    "Musyoki",
    "Mutahi",
    "Mutai",
    "Mwangangi",
    "Mwangi",
    "Ndungu",
    "Ngugi",
    "Njenga",
    "Njeri",
    "Nyambura",
    "Oduya",
    "Onyango",
    "Sigei",
    "Songok",
    "Tergat",
    "Wacera",
    "Wairimu",
    "Waithaka",
    "Wambui",
    "Wangari",
    "Wanjiku",
    "Wanjiru",
]

FARMER_GROUP_NAMES = [
    "FarmMates",
    "AgriAllies",
    "CropComrades",
    "SeedSquad",
    "HarvestHelpers",
    "PlowPals",
    "SowBuddies",
    "GrowGuild",
    "MeadowMates",
    "TerraTroop",
    "CultivateCrew",
    "FieldFriends",
    "EarthEntourage",
    "PasturePosse",
    "TillerTeam",
    "GrainGang",
    "AgricAmigos",
    "PlantPioneers",
    "SoilSiblings",
    "OrchardOrder",
    "RuralRangers",
    "HomesteadHomies",
    "FertileFellows",
    "BountyBuddies",
    "SproutSquad",
    "CropCohort",
    "AgriAffiliates",
    "FarmFaction",
    "HarvestHorde",
    "CultivarClan",
    "YieldYielders",
    "GreenGuardians",
    "TillTribe",
    "MeadowMilitia",
    "SeedlingSociety",
    "CropCircleCrew",
    "FarmForce",
    "AgronomyAlliance",
    "EarthbornEchelon",
    "GrowGroup",
    "PastoralPack",
    "SoilSquadrons",
    "PlowPartners",
    "HarvestHive",
    "RuralRebels",
    "FieldFaction",
    "PlantingParty",
    "TerraTribe",
    "GrowthGroupies",
    "AgrarianArmy",
    "SeedSoldiers",
    "FieldForce",
    "CropCollective",
    "HarvestHuddle",
    "PlantPals",
    "MeadowMenagerie",
    "AgriAllstars",
    "BountyBrigade",
    "PasturePals",
    "SowSquadrons",
    "FieldFellows",
    "EarthEmissaries",
    "TillageTroopers",
    "SproutSquadron",
    "HarvestHeroes",
    "CropCrusaders",
    "GreenGroveGroupies",
    "SoilSoldiers",
    "MeadowMavens",
    "FarmFellows",
    "SeedlingSquad",
    "GrowerGang",
    "OrchardOutfit",
    "PlantingPlatoon",
    "CultivarCompanions",
    "AgriArtisans",
    "TillerTribe",
    "FarmFrontiers",
    "HarvestHenchmen",
    "AgrarianAdvocates",
    "CropCommandos",
    "PastoralPioneers",
    "FieldFrontiersmen",
    "SoilSavants",
    "Growers'Guildsmen",
    "EarthwiseElite",
    "MeadowMasters",
    "RuralRanks",
    "HarvestHonorables",
    "CropConsortium",
    "FarmFrontFaction",
    "PloughPatrol",
    "SowerSquadrons",
    "PasturePartisans",
    "TerraTroopers",
    "YieldYodas",
    "AgriAssortment",
    "GreenfieldGuard",
    "SoilSentries",
    "FarmsteadFellowship",
]

PRODUCTS = [
    {
        "id": 1,
        "name_eng": "Vegetable",
        "name_lao": "ຜັກ",
    },
    {
        "id": 2,
        "name_eng": "Rice",
        "name_lao": "ເຂົ້າ",
    },
    {
        "id": 3,
        "name_eng": "Onion",
        "name_lao": "ຜັກບົ່ວ",
    },
    {
        "id": 4,
        "name_eng": "Cabbage",
        "name_lao": "ກະລໍ່າປີ",
    },
    {
        "id": 5,
        "name_eng": "Peanuts",
        "name_lao": "ຖົ່ວດິນ",
    },
    {
        "id": 6,
        "name_eng": "Cucumber",
        "name_lao": "ໝາກແຕງ",
    },
    {
        "id": 7,
        "name_eng": "Garlic",
        "name_lao": "ຜັກທຽມ",
    },
    {
        "id": 9,
        "name_eng": "Cassava",
        "name_lao": "ມັນຕົ້ນ",
    },
    {
        "id": 10,
        "name_eng": "Chili",
        "name_lao": "ໝາກເຜັດ",
    },
    {
        "id": 11,
        "name_eng": "Tea",
        "name_lao": "ຊາ",
    },
    {
        "id": 12,
        "name_eng": "Maize",
        "name_lao": "ສາລີ",
    },
    {
        "id": 13,
        "name_eng": "Sugarcane, banana",
        "name_lao": "ອ້ອຍ, ກ້ວຍ",
    },
    {
        "id": 14,
        "name_eng": "Job'tears",
        "name_lao": "ນໍ້າຕາຂອງໂຢບ",
    },
    {
        "id": 15,
        "name_eng": "Grass planting for forage",
        "name_lao": "ການປູກຫຍ້າລ້ຽງສັດ",
    },
    {
        "id": 16,
        "name_eng": "Sesame",
        "name_lao": "ໝາກງາ",
    },
    {
        "id": 17,
        "name_eng": "Bean",
        "name_lao": "ຖົ່ວ",
    },
    {
        "id": 19,
        "name_eng": "Pig",
        "name_lao": "ຫມູ",
    },
    {
        "id": 20,
        "name_eng": "Chicken",
        "name_lao": "ໄກ່",
    },
    {
        "id": 21,
        "name_eng": "Goat",
        "name_lao": "ແບ້",
    },
    {
        "id": 22,
        "name_eng": "Other 1",
        "name_lao": "ອື່ນໆ 1",
    },
]

EVENT_TYPE = [
    "fgmemr1",
    "wumem",
    "fgmemr2",
    "impagri",
    "implive",
]

EVENT_DATA_TYPES = [
    "spp.event.gen.info",
    "spp.event.poverty.indicator",
    "spp.event.hh.labor",
    "spp.event.hh.assets",
    "spp.event.agri.land.ownership.use",
    "spp.event.food.security",
    "spp.event.agri.ws",
    "spp.event.agri.tech.ws",
    "spp.event.agri.ds",
    "spp.event.agri.ds.hot",
    "spp.event.permanent.crops",
    "spp.event.livestock.farming",
    "spp.event.inc.agri",
    "spp.event.inc.non.agri",
    "spp.event.wash.ind",
    "spp.event.hh.resilience.index",
    "spp.event.min.dietary.score",
]


class SPPLaosGenerateFarmerData(models.Model):
    _name = "spp.laos.generate.farmer.data"
    _description = "Generate Farm Data For Laos"

    name = fields.Char()
    num_groups = fields.Integer("Number of Farmer Groups", default=1)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("generate", "Generated"),
        ],
        default="draft",
    )

    def generate_sample_data(self):
        batches = math.ceil(self.num_groups / 1000)

        for _ in range(0, batches):
            # self.with_delay()._generate_sample_data(res=self)
            self._generate_sample_data(res=self)

    @api.model
    def _generate_sample_data(self, **kwargs):
        res = kwargs.get("res")

        kind_farmer_group_id = self.env.ref("spp_farmer_registry_laos.kind_farmer_group").id
        kind_farm_id = self.env.ref("spp_farmer_registry_base.kind_farm").id
        num_groups = min(res.num_groups, 1000)

        for i in range(1, num_groups + 1):
            # Generate Farmer Group data
            farmer_group_name = f"Farmer Group {random.choice(FARMER_GROUP_NAMES)}"
            farmer_group_id = res._generate_group_data(i, kind_farmer_group_id, farmer_group_name)
            self._generate_event_datas(farmer_group_id)
            land_record_id = res._generate_land_record_record(farmer_group_id)
            farmer_group_id.farm_land_rec_id = land_record_id.id
            farmer_group_id.coordinates = land_record_id.land_coordinates
            product = random.choice(PRODUCTS)
            res._generate_farm_activity(farmer_group_id, product)

            for j in range(random.randint(1, 5)):
                # Generate Farm data
                group_name = f"{random.choice(NAMES)} Farm"
                group_id = res._generate_group_data(j, kind_farm_id, group_name)
                self._generate_event_datas(group_id)
                land_record_id = res._generate_land_record_record(group_id)
                group_id.farm_land_rec_id = land_record_id.id
                group_id.coordinates = land_record_id.land_coordinates
                product = random.choice(PRODUCTS)
                res._generate_farm_activity(group_id, product)

                self.env["g2p.group.membership"].create(
                    {
                        "group": farmer_group_id.id,
                        "individual": group_id.id,
                    }
                )

        if res.state == "draft":
            res.update({"state": "generate"})

        msg = "Task Queue called task: model [{}] and method [{}].".format(
            self._name,
            "_generate_sample_data",
        )

        return {"result": msg, "res_model": self._name, "res_ids": [res.id]}

    def _generate_group_data(self, index, kind_id, group_name):
        id_group = "demo." + hashlib.md5(f"{group_name} {index}".encode()).hexdigest()

        group_vals = {
            "id": id_group,
            "name": group_name,
            "kind": kind_id,
            "is_registrant": True,
            "is_group": True,
        }

        return self.env["res.partner"].create(group_vals)

    def _generate_land_record_record(self, group_id):
        latitude, longitude = random_location_in_laos()

        land_coordinates = {"type": "Point", "coordinates": [longitude, latitude]}

        points = generate_polygon(latitude, longitude, random.randrange(50, 500))

        land_geo_polygon = {"type": "Polygon", "coordinates": [points]}

        return self.env["spp.land.record"].create(
            {
                "land_farm_id": group_id.id,
                "land_name": group_id.name,
                "land_coordinates": json.dumps(land_coordinates),
                "land_geo_polygon": json.dumps(land_geo_polygon),
            }
        )

    def _generate_farm_activity(self, group_id, product):
        product_id = product.get("id")
        product_name_eng = product.get("name_eng")
        product_name = product.get("name_lao")
        target_year = str(random.randint(2000, 2050))

        self.env["spp.farm.activity"].create(
            {
                "prod_farm_id": group_id.id,
                "product_id": product_id,
                "product_name_eng": product_name_eng,
                "product_name": product_name,
                "target_year": target_year,
            }
        )

    def _generate_random_phone_number(self):
        # Generates a random phone number of the format: (XXX) XXX-XXXX
        area_code = random.randint(100, 999)
        exchange_code = random.randint(100, 999)
        subscriber_number = random.randint(1000, 9999)

        phone_number = f"({area_code}) {exchange_code}-{subscriber_number}"
        return phone_number

    def _generate_random_date(self, start_date, end_date):
        """
        Generates a random date between start_date and end_date.

        :param start_date: A datetime.date object representing the start date.
        :param end_date: A datetime.date object representing the end date.
        :return: A string representing a random date between start_date and end_date in the format 'YYYY-MM-DD'.
        """
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + timedelta(days=random_number_of_days)
        return random_date

    def _create_event_data(self, model_name, group_id):
        vals_list = {
            "model": model_name,
            "partner_id": group_id.id,
        }
        event_id = self.env["spp.event.data"].create(vals_list)
        return event_id

    def call_method_by_name(self, method_name, event_id):
        # Dynamically call a method based on its name
        _logger.info(method_name)
        method = getattr(self, method_name, None)
        if method:
            return method(event_id)
        else:
            return None

    def _generate_event_datas(self, registrant):
        for event_data in EVENT_DATA_TYPES:
            event_id = self._create_event_data(event_data, registrant)
            event_data_model = "_generate_" + event_data.lstrip("spp.").replace(".", "_")
            self.call_method_by_name(event_data_model, event_id)

    def _generate_event_gen_info(self, event_id):
        ethnic_group = self.env["spp.ethnic.group"].search([]).mapped("id")
        # land_record_id = self._generate_land_record_record(event_id.partner_id)
        vals_list = {
            "interviewees_name": f"{random.choice(NAMES)}",
            "ethnic_group_id": random.choice(ethnic_group),
            "sex": str(random.randint(1, 2)),
            "marital_status": str(random.randint(1, 4)),
            "age": random.randint(20, 80),
            "educational_qualification": str(random.randint(1, 6)),
            "head_of_household": str(random.randint(1, 2)),
            "poverty_status": str(random.randint(1, 3)),
            # "gps_location": land_record_id.land_coordinates,
            "phone_number1": self._generate_random_phone_number(),
            "phone_number2": self._generate_random_phone_number(),
            "participating": str(random.randint(1, 2)),
            "date_participated": self._generate_random_date(date.today() - timedelta(days=50), date.today()),
            "grp_act_supported_by_project_agri": str(random.randint(0, 16)),
            "grp_act_supported_by_project_livestock_fisheries": random.choice(["0", "19", "20", "21"]),
            "tech_supported_by_project_org_fert": str(random.randint(1, 2)),
            "tech_supported_by_project_greenhouse": str(random.randint(1, 2)),
            "tech_supported_by_project_mulching": str(random.randint(1, 2)),
            "tech_supported_by_project_gravity_irrig": str(random.randint(1, 2)),
            "tech_supported_by_project_water_pump": str(random.randint(1, 2)),
            "tech_supported_by_project_drip_irrig": str(random.randint(1, 2)),
            "tech_supported_by_project_drip_sprinkler": str(random.randint(1, 2)),
            "tech_supported_by_project_machine_harvest": str(random.randint(1, 2)),
            "tech_supported_by_project_dry_processing": str(random.randint(1, 2)),
            "tech_supported_by_project_agri_oth": str(random.randint(1, 2)),
            "tech_supported_by_project_concent_feed": str(random.randint(1, 2)),
            "tech_supported_by_project_grass_planting": str(random.randint(1, 2)),
            "tech_supported_by_project_vaccination": str(random.randint(1, 2)),
            "tech_supported_by_project_livestock_oth": random.choice(FARMER_GROUP_NAMES),
            "irrigation_area_supported": random.randint(1, 999),
            "participation_oth_proj": str(random.randint(1, 2)),
            "hhq_number_baseline_survey": random.randint(1, 999),
            "survey_sched": str(random.randint(1, 3)),
        }

        event = self.env["spp.event.gen.info"].create(vals_list)
        event_id.res_id = event.id

    def _generate_event_poverty_indicator(self, event_id):
        vals_list = {
            "type_of_housing": str(random.randint(1, 3)),
            "atleast_1household_member_completed_sch": str(random.randint(1, 2)),
            "there_are_children_attend_pri_sch": str(random.randint(1, 3)),
            "there_are_children_attend_mid_sch": str(random.randint(1, 3)),
            "access_to_electricity": str(random.randint(1, 3)),
            "access_to_basic_health_care": str(random.randint(1, 2)),
            "access_to_internet": str(random.randint(1, 3)),
            "survey_sched": str(random.randint(1, 3)),
        }

        event = self.env["spp.event.poverty.indicator"].create(vals_list)
        event_id.res_id = event.id

    def _generate_event_hh_labor(self, event_id):
        vals_list = {
            "no_hh_members_women": random.randint(1, 50),
            "no_hh_members_men": random.randint(1, 50),
            "hh_labor_availability_15_35_women": random.randint(1, 50),
            "hh_labor_availability_15_35_men": random.randint(1, 50),
            "hh_labor_availability_36_60_women": random.randint(1, 50),
            "hh_labor_availability_36_60_men": random.randint(1, 50),
            "labor_availability_agri_15_35_women": random.randint(1, 50),
            "labor_availability_agri_15_35_men": random.randint(1, 50),
            "labor_availability_agri_36_60_women": random.randint(1, 50),
            "labor_availability_agri_36_60_men": random.randint(1, 50),
            "survey_sched": str(random.randint(1, 3)),
        }

        event = self.env["spp.event.hh.labor"].create(vals_list)
        event_id.res_id = event.id

    def _generate_event_hh_assets(self, event_id):
        vals_list = {
            "asset_non_agri_tv": random.randint(1, 50),
            "asset_non_agri_refrigerator": random.randint(1, 50),
            "asset_non_agri_motobike": random.randint(1, 50),
            "asset_non_agri_vehicle": random.randint(1, 50),
            "asset_non_agri_mobile_dev": random.randint(1, 50),
            "asset_non_agri_elec_gas_stove": random.randint(1, 50),
            "asset_non_agri_computer": random.randint(1, 50),
            "asset_non_agri_solar_panel": random.randint(1, 50),
            "asset_non_agri_generator": random.randint(1, 50),
            "asset_non_agri_charcoal_stove": random.randint(1, 50),
            "asset_non_agri_kerosene_stove": random.randint(1, 50),
            "asset_non_agri_washing_machine": random.randint(1, 50),
            "asset_non_agri_elec_pot": random.randint(1, 50),
            "asset_non_agri_elec_water_boiler": random.randint(1, 50),
            "asset_non_agri_rice_cooker": random.randint(1, 50),
            "asset_non_agri_fan": random.randint(1, 50),
            "asset_non_agri_sewing_machine": random.randint(1, 50),
            "asset_agri_4wd_tractor": random.randint(1, 50),
            "asset_agri_hand_tractor": random.randint(1, 50),
            "asset_agri_thresher": random.randint(1, 50),
            "asset_agri_green_house": random.randint(1, 50),
            "asset_agri_drying_facility": random.randint(1, 50),
            "asset_agri_rice_mill": random.randint(1, 50),
            "asset_agri_harvester": random.randint(1, 50),
            "asset_agri_water_pump": random.randint(1, 50),
            "asset_agri_farm_truck_tractor": random.randint(1, 50),
            "asset_agri_grass_cutter": random.randint(1, 50),
            "asset_agri_elec_wood_cutting": random.randint(1, 50),
            "asset_agri_feed_pellet_extruder": random.randint(1, 50),
            "asset_livestock_buffalo": random.randint(1, 50),
            "asset_livestock_cow_meat": random.randint(1, 50),
            "asset_livestock_cow_milk": random.randint(1, 50),
            "asset_livestock_goat": random.randint(1, 50),
            "asset_livestock_pig": random.randint(1, 50),
            "asset_livestock_piglets": random.randint(1, 50),
            "asset_livestock_paultry": random.randint(1, 50),
            "asset_livestock_aquatic_animals": random.randint(1, 50),
            "asset_livestock_frog": random.randint(1, 50),
            "asset_livestock_horse": random.randint(1, 50),
            "survey_sched": str(random.randint(1, 3)),
        }

        event = self.env["spp.event.hh.assets"].create(vals_list)
        event_id.res_id = event.id

    def _generate_event_agri_land_ownership_use(self, event_id):
        vals_list = {
            "crops_in_irrigated_land": str(random.randint(0, 2)),
            "crops_in_irrigated_land_ha": random.randint(1, 50),
            "survey_sched": str(random.randint(1, 3)),
            "land_ownership_ids": [
                Command.create(
                    {
                        "land_ownership": str(random.randint(1, 4)),
                        "irrigated_puddy": random.randint(1, 50),
                        "rainfed_puddy": random.randint(1, 50),
                        "upland_agriculture": random.randint(1, 50),
                        "coffee_tea_plantation": random.randint(1, 50),
                        "cardamom_plantation": random.randint(1, 50),
                        "orchard": random.randint(1, 50),
                        "pasture": random.randint(1, 50),
                        "fallow_land": random.randint(1, 50),
                        "forest": random.randint(1, 50),
                        "land_rent_oth_hh": random.randint(1, 50),
                        "oth_agri_land_owned_by_hh": random.randint(1, 50),
                        "total": random.randint(1, 50),
                    }
                )
            ],
        }

        event = self.env["spp.event.agri.land.ownership.use"].create(vals_list)
        event_id.res_id = event.id

    def _generate_event_food_security(self, event_id):
        vals_list = {
            "hungry_season_past_12": random.randint(1, 50),
            "shortage_january": random.randint(1, 50),
            "shortage_february": random.randint(1, 50),
            "shortage_march": random.randint(1, 50),
            "shortage_april": random.randint(1, 50),
            "shortage_may": random.randint(1, 50),
            "shortage_june": random.randint(1, 50),
            "shortage_july": random.randint(1, 50),
            "shortage_august": random.randint(1, 50),
            "shortage_september": random.randint(1, 50),
            "shortage_october": random.randint(1, 50),
            "shortage_november": random.randint(1, 50),
            "shortage_december": random.randint(1, 50),
            "survey_sched": str(random.randint(1, 3)),
        }

        event = self.env["spp.event.food.security"].create(vals_list)
        event_id.res_id = event.id

    def _generate_event_agri_ws(self, event_id):
        crops = self.env["spp.farm.species"].search([("species_type", "=", "crop")]).mapped("id")
        vals_list = {
            "experience_dryspell_flood": random.randint(1, 50),
            "experience_dryspell_flood_dates": str(
                self._generate_random_date(date.today() - timedelta(days=50), date.today())
            ),
            "experience_pest_disease_outbreak": random.randint(1, 50),
            "experience_pest_disease_outbreak_dates": str(
                self._generate_random_date(date.today() - timedelta(days=50), date.today())
            ),
            "experience_pest_disease_outbreak_type": random.choice(FARMER_GROUP_NAMES),
            "experience_pest_disease_outbreak_affected": str(random.randint(1, 50)),
            "survey_sched": str(random.randint(1, 3)),
            "agri_ws_produce_ids": [
                Command.create(
                    {
                        "crop_id": random.choice(crops),
                        "cropping_period_sowing": str(
                            self._generate_random_date(date.today() - timedelta(days=50), date.today())
                        ),
                        "cropping_period_harvest": str(
                            self._generate_random_date(date.today() - timedelta(days=50), date.today())
                        ),
                        "harvest_area": random.randint(1, 50),
                        "harvest_amount": random.randint(1, 50),
                        "harvest_share": random.randint(1, 50),
                        "sales_qty": random.randint(1, 50),
                        "sales_price": random.randint(1, 50),
                        "sales_value": random.randint(1, 50),
                        "contract_farming": random.randint(1, 50),
                        "name_of_partner": random.choice(FARMER_GROUP_NAMES),
                    }
                )
            ],
            "agri_ws_cost_ids": [
                Command.create(
                    {
                        "crop_id": random.choice(crops),
                        "labor_input": random.randint(1, 50),
                        "preparation_farmland": random.randint(1, 50),
                        "seeds": random.randint(1, 50),
                        "labor_cost": random.randint(1, 50),
                        "fertilizer": random.randint(1, 50),
                        "pesticide": random.randint(1, 50),
                        "herbicide": random.randint(1, 50),
                        "water_fee": random.randint(1, 50),
                        "tool_equipment": random.randint(1, 50),
                        "other_fees": random.randint(1, 50),
                        "total_production": random.randint(1, 50),
                    }
                )
            ],
        }

        event = self.env["spp.event.agri.ws"].create(vals_list)
        event_id.res_id = event.id

    def _generate_event_agri_tech_ws(self, event_id):
        crops = self.env["spp.farm.species"].search([("species_type", "=", "crop")]).mapped("id")
        vals_list = {
            "survey_sched": str(random.randint(1, 3)),
            "agri_prod_sales_cost_tech_ids": [
                Command.create(
                    {
                        "crop_id": random.choice(crops),
                        "org_felt_pest_herb": str(random.randint(0, 1)),
                        "greenhouse": str(random.randint(0, 1)),
                        "multing": str(random.randint(0, 1)),
                        "irrigation_normal": str(random.randint(0, 1)),
                        "water_pump": str(random.randint(0, 1)),
                        "drip_irrigation": str(random.randint(0, 1)),
                        "sprinkler": str(random.randint(0, 1)),
                        "machine_harvest": str(random.randint(0, 1)),
                        "dry_processing": str(random.randint(0, 1)),
                        "post_harvest_treatment": str(random.randint(0, 1)),
                        "other": random.choice(FARMER_GROUP_NAMES),
                    }
                )
            ],
        }

        event = self.env["spp.event.agri.tech.ws"].create(vals_list)
        event_id.res_id = event.id

    def _generate_event_agri_ds(self, event_id):
        crops = self.env["spp.farm.species"].search([("species_type", "=", "crop")]).mapped("id")
        vals_list = {
            "survey_sched": str(random.randint(1, 3)),
            "agri_prod_ids": [
                Command.create(
                    {
                        "crop_id": random.choice(crops),
                        "harvest_area": random.randint(1, 50),
                        "harvest_amt_kg": random.randint(1, 50),
                        "sales_qty_kg": random.randint(1, 50),
                        "sales_price_lak_kg": random.randint(1, 50),
                        "sales_value": random.randint(1, 50),
                        "contract_farming": str(random.randint(1, 2)),
                        "partner_name": random.choice(FARMER_GROUP_NAMES),
                    }
                )
            ],
            "agri_cost_ids": [
                Command.create(
                    {
                        "crop_id": random.choice(crops),
                        "labor_input_days": random.randint(1, 50),
                        "preparation_farmland": random.randint(1, 50),
                        "seeds": random.randint(1, 50),
                        "labor_cost": random.randint(1, 50),
                        "fertilizer": random.randint(1, 50),
                        "pesticide": random.randint(1, 50),
                        "herbicide_oth": random.randint(1, 50),
                        "water_fee": random.randint(1, 50),
                        "total_equipment": random.randint(1, 50),
                        "oth_fees": random.randint(1, 50),
                        "total_prod_cost": random.randint(1, 50),
                    }
                )
            ],
            "agri_tech_ids": [
                Command.create(
                    {
                        "crop_id": random.choice(crops),
                        "organic_fertilizer": str(random.randint(0, 1)),
                        "greenhouse": str(random.randint(0, 1)),
                        "multing": str(random.randint(0, 1)),
                        "irrigation": str(random.randint(0, 1)),
                        "water_pump": str(random.randint(0, 1)),
                        "drip_irrigation": str(random.randint(0, 1)),
                        "sprinkler": str(random.randint(0, 1)),
                        "machine_harvest": str(random.randint(0, 1)),
                        "dry_processing": str(random.randint(0, 1)),
                        "post_harvest_treatment": str(random.randint(0, 1)),
                        "other": random.choice(FARMER_GROUP_NAMES),
                    }
                )
            ],
        }

        event = self.env["spp.event.agri.ds"].create(vals_list)
        event_id.res_id = event.id

    def _generate_event_agri_ds_hot(self, event_id):
        crops = self.env["spp.farm.species"].search([("species_type", "=", "crop")]).mapped("id")
        vals_list = {
            "survey_sched": str(random.randint(1, 3)),
            "agri_prod_ids": [
                Command.create(
                    {
                        "crop_id": random.choice(crops),
                        "harvest_area": random.randint(1, 50),
                        "harvest_amt_kg": random.randint(1, 50),
                        "sales_qty_kg": random.randint(1, 50),
                        "sales_price_lak_kg": random.randint(1, 50),
                        "sales_value": random.randint(1, 50),
                        "contract_farming": str(random.randint(1, 2)),
                        "partner_name": random.choice(FARMER_GROUP_NAMES),
                    }
                )
            ],
            "agri_cost_ids": [
                Command.create(
                    {
                        "crop_id": random.choice(crops),
                        "labor_input_days": random.randint(1, 50),
                        "preparation_farmland": random.randint(1, 50),
                        "seeds": random.randint(1, 50),
                        "labor_cost": random.randint(1, 50),
                        "fertilizer": random.randint(1, 50),
                        "pesticide": random.randint(1, 50),
                        "herbicide_oth": random.randint(1, 50),
                        "water_fee": random.randint(1, 50),
                        "total_equipment": random.randint(1, 50),
                        "oth_fees": random.randint(1, 50),
                        "total_prod_cost": random.randint(1, 50),
                    }
                )
            ],
            "agri_tech_ids": [
                Command.create(
                    {
                        "crop_id": random.choice(crops),
                        "organic_fertilizer": str(random.randint(0, 1)),
                        "greenhouse": str(random.randint(0, 1)),
                        "multing": str(random.randint(0, 1)),
                        "irrigation": str(random.randint(0, 1)),
                        "water_pump": str(random.randint(0, 1)),
                        "drip_irrigation": str(random.randint(0, 1)),
                        "sprinkler": str(random.randint(0, 1)),
                        "machine_harvest": str(random.randint(0, 1)),
                        "dry_processing": str(random.randint(0, 1)),
                        "post_harvest_treatment": str(random.randint(0, 1)),
                        "other": random.choice(FARMER_GROUP_NAMES),
                    }
                )
            ],
        }

        event = self.env["spp.event.agri.ds.hot"].create(vals_list)
        event_id.res_id = event.id

    def _generate_event_permanent_crops(self, event_id):
        crops = self.env["spp.farm.species"].search([("species_type", "=", "crop")]).mapped("id")
        vals_list = {
            "survey_sched": str(random.randint(1, 3)),
            "crop_prod_ids": [
                Command.create(
                    {
                        "crop_id": random.choice(crops),
                        "harvest_area": random.randint(1, 50),
                        "harvest_amt_kg": random.randint(1, 50),
                        "sales_qty_kg": random.randint(1, 50),
                        "sales_price_lak_kg": random.randint(1, 50),
                        "sales_value": random.randint(1, 50),
                        "contract_farming": str(random.randint(1, 2)),
                        "partner_name": random.choice(FARMER_GROUP_NAMES),
                    }
                )
            ],
            "crop_cost_ids": [
                Command.create(
                    {
                        "crop_id": random.choice(crops),
                        "labor_input_days": random.randint(1, 50),
                        "preparation_farmland": random.randint(1, 50),
                        "seeds": random.randint(1, 50),
                        "labor_cost": random.randint(1, 50),
                        "fertilizer": random.randint(1, 50),
                        "pesticide": random.randint(1, 50),
                        "herbicide_oth": random.randint(1, 50),
                        "water_fee": random.randint(1, 50),
                        "total_equipment": random.randint(1, 50),
                        "oth_fees": random.randint(1, 50),
                        "total_prod_cost": random.randint(1, 50),
                    }
                )
            ],
            "crop_tech_ids": [
                Command.create(
                    {
                        "crop_id": random.choice(crops),
                        "organic_fertilizer": str(random.randint(0, 1)),
                        "greenhouse": str(random.randint(0, 1)),
                        "multing": str(random.randint(0, 1)),
                        "irrigation": str(random.randint(0, 1)),
                        "water_pump": str(random.randint(0, 1)),
                        "drip_irrigation": str(random.randint(0, 1)),
                        "sprinkler": str(random.randint(0, 1)),
                        "machine_harvest": str(random.randint(0, 1)),
                        "dry_processing": str(random.randint(0, 1)),
                        "post_harvest_treatment": str(random.randint(0, 1)),
                        "other": random.choice(FARMER_GROUP_NAMES),
                    }
                )
            ],
        }

        event = self.env["spp.event.permanent.crops"].create(vals_list)
        event_id.res_id = event.id

    def _generate_event_data_cycle(self, group_id):
        event_id = self._create_event_data("spp.event.cycle", group_id)
        vals = self._generate_event_data_vals()

        event = self.env["spp.event.cycle"].create(vals)
        event_id.res_id = event.id

    def _generate_event_data_vals(self):
        event_type = random.choice(EVENT_TYPE)
        cycle_vals = {}
        if event_type in ("fgmemr1", "wumem", "fgmemr2"):
            no_hh_member = random.randint(1, 100)
            no_indigenous = random.randint(1, no_hh_member)
            percent_indigenous = no_indigenous / no_hh_member * 100
            no_15_35 = random.randint(1, no_indigenous)
            percent_15_35 = no_15_35 / no_hh_member * 100
            cycle_vals = {
                "no_woman_headed": 0,
                "no_better_off": 0,
                "no_medium": 0,
                "no_poor": 0,
            }
            total_member = no_hh_member
            for val in cycle_vals:
                if total_member > 0:
                    value = random.randint(0, total_member)
                    cycle_vals[val] = value
                    total_member -= value

            cycle_vals2 = {
                "no_male": 0,
                "no_female": 0,
                "no_both": 0,
            }
            total_member = no_hh_member
            for val in cycle_vals2:
                if total_member > 0:
                    value = random.randint(0, total_member)
                    cycle_vals2[val] = value
                    total_member -= value

            cycle_vals.update(cycle_vals2)

            cycle_vals.update(
                {
                    "event_type": event_type,
                    "no_hh_member": no_hh_member,
                    "no_indigenous": no_indigenous,
                    "percent_indigenous": percent_indigenous,
                    "no_15_35": no_15_35,
                    "percent_15_35": percent_15_35,
                }
            )

        elif event_type == "impagri":
            cycle_vals = {
                "event_type": event_type,
                "no_implemented": random.randint(0, 100),
                "no_on_going": random.randint(0, 100),
                "no_not_implemented": random.randint(0, 100),
                "production_area": random.randint(0, 100),
                "agricultural_yield": random.randint(0, 100),
                "agricultural_productivity": random.randint(0, 100),
            }
        else:
            cycle_vals = {
                "event_type": event_type,
                "no_livestock_project": random.randint(0, 100),
                "no_livestock_present": random.randint(0, 100),
                "no_livestock_consumption": random.randint(0, 100),
                "no_livestock_sold": random.randint(0, 100),
                "no_livestock_increase": random.randint(0, 100),
            }

        if cycle_vals:
            return cycle_vals
