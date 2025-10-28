# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import datetime
import logging
import random

from faker import Faker

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SPPDemoDataGenerator(models.Model):
    _inherit = "spp.demo.data.generator"

    # Farmer Registry specific fields
    percentage_with_farm_details = fields.Integer(
        string="% with Farm Details",
        default=80,
        required=True,
        help="Percentage of farmers that will have farm details",
    )
    percentage_with_land_records = fields.Integer(
        string="% with Land Records",
        default=70,
        required=True,
        help="Percentage of farmers that will have land records",
    )
    percentage_with_farm_assets = fields.Integer(
        string="% with Farm Assets", default=60, required=True, help="Percentage of farmers that will have farm assets"
    )
    percentage_with_agricultural_activities = fields.Integer(
        string="% with Agricultural Activities",
        default=85,
        required=True,
        help="Percentage of farmers that will have agricultural activities",
    )
    percentage_with_extension_services = fields.Integer(
        string="% with Extension Services",
        default=40,
        required=True,
        help="Percentage of farmers that will have extension services",
    )
    max_farm_size = fields.Float(
        string="Maximum Farm Size (acres)",
        default=100.0,
        required=True,
        help="Maximum farm size in acres for generated data",
    )
    min_farm_size = fields.Float(
        string="Minimum Farm Size (acres)",
        default=0.5,
        required=True,
        help="Minimum farm size in acres for generated data",
    )
    max_land_parcels_per_farm = fields.Integer(
        string="Maximum Land Parcels per Farm", default=5, required=True, help="Maximum number of land parcels per farm"
    )
    max_assets_per_farm = fields.Integer(
        string="Maximum Assets per Farm", default=10, required=True, help="Maximum number of assets per farm"
    )
    max_activities_per_farm = fields.Integer(
        string="Maximum Activities per Farm",
        default=8,
        required=True,
        help="Maximum number of agricultural activities per farm",
    )
    
    # Season configuration fields
    season_name = fields.Char(
        string="Season Name",
        default=lambda self: f"Demo Season {fields.Date.today().year}",
        required=True,
        help="Name of the agricultural season to use or create",
    )
    season_start_date = fields.Date(
        string="Season Start Date",
        default=lambda self: fields.Date.today().replace(month=1, day=1),
        required=True,
        help="Start date of the agricultural season",
    )
    season_end_date = fields.Date(
        string="Season End Date",
        default=lambda self: fields.Date.today().replace(month=12, day=31),
        required=True,
        help="End date of the agricultural season",
    )

    @api.constrains("season_start_date", "season_end_date")
    def _check_season_dates(self):
        """Validate that season end date is after start date"""
        for record in self:
            if record.season_end_date and record.season_start_date:
                if record.season_end_date < record.season_start_date:
                    raise ValidationError(_("Season end date must be after start date"))

    # Selection options for farmer registry
    FARM_TYPES = [
        ("crop", "Crop"),
        ("livestock", "Livestock"),
        ("aquaculture", "Aquaculture"),
        ("mixed", "Mixed"),
    ]

    LAND_USES = [
        ("cultivation", "Cultivation"),
        ("livestock", "Livestock"),
        ("aquaculture", "Aquaculture"),
        ("mixed", "Mixed Use"),
        ("fallow", "Fallow"),
        ("leased_out", "Leased Out"),
        ("other", "Other"),
    ]

    CULTIVATION_METHODS = [
        ("irrigated", "Irrigated"),
        ("rainfed", "Rainfed"),
    ]

    LEGAL_STATUSES = [
        ("self", "Owned by self"),
        ("family", "Owned by family"),
        ("extended community", "Owned by extended community"),
        ("cooperative", "Owned by cooperative"),
        ("government", "Owned by Government"),
        ("leased", "Leased from actual owner"),
        ("unknown", "Do not Know"),
    ]

    ACTIVITY_TYPES = [
        ("crop", "Crop Cultivation"),
        ("livestock", "Livestock Rearing"),
        ("aquaculture", "Aquaculture"),
    ]

    PRODUCTION_PURPOSES = [
        ("subsistence", "Subsistence"),
        ("commercial", "Commercial"),
        ("both", "Both"),
    ]

    def generate_demo_data(self):
        """Override to include farmer registry specific data generation"""
        # Generate reference data first
        fake = Faker(self.locale_origin.faker_locale or "en_US")
        self._generate_species_data(fake)
        self._generate_chemical_data(fake)
        self._generate_fertilizer_data(fake)
        self._generate_feed_items_data(fake)
        
        # Pre-initialize the season early (will be cached and reused by _get_random_season)
        season_id = self._get_random_season()
        if not season_id:
            raise ValidationError(
                _("Failed to create or find an active agricultural season. "
                  "Please check the season configuration and try again.")
            )
        
        _logger.info(
            f"Demo data generation initialized with season: {self._active_season.name} "
            f"({self._active_season.date_start} to {self._active_season.date_end})"
        )

        result = super().generate_demo_data()
        return result

    def get_group_vals(self, fake):
        """Override to include farmer registry fields in group data"""
        # Get base group values from parent
        group_vals = super().get_group_vals(fake)

        # Add farmer registry specific fields
        group_vals.update(
            {
                "household_size": random.randint(1, 15),
                "experience_years": random.randint(0, 50),
                "formal_agricultural_training": random.choice([True, False]),
                "farmer_household_size": group_vals.get("household_size", random.randint(1, 15)),
                "farmer_postal_address": fake.address(),
                "marital_status": random.choice(
                    ["single", "widowed", "married", "separated", "married_monogamous", "married_polygamous"]
                ),
                "highest_education_level": random.choice(
                    ["none", "primary", "secondary", "certificate", "diploma", "university", "tertiary"]
                ),
            }
        )

        # Specific Head Farmer details on Group
        farmer_family_name = fake.last_name()
        group_vals.update(
            {
                "farmer_family_name": farmer_family_name,
                "name": farmer_family_name,
                "farmer_given_name": fake.first_name(),
                "farmer_addtnl_name": fake.first_name() if random.choice([True, False]) else None,
                "farmer_mobile_tel": self.generate_phone_number(fake),
                "farmer_sex": self.get_gender_id(random.choice(self.GENDERS)),
                "farmer_birthdate": self.get_random_date(
                    fake,
                    datefrom=fields.Date.today().replace(year=fields.Date.today().year - 70),
                    dateto=fields.Date.today().replace(year=fields.Date.today().year - 18),
                ),
                "farmer_household_size": group_vals.get("household_size", random.randint(1, 15)),
                "farmer_postal_address": fake.address(),
                "farmer_email": fake.email(),
                "farmer_formal_agricultural": random.choice([True, False]),
                "farmer_highest_education_level": random.choice(["none", "primary", "secondary", "tertiary"]),
                "farmer_marital_status": random.choice(["single", "married", "widowed", "separated"]),
            }
        )

        return group_vals

    def get_individual_vals(self, fake):
        """Override to include farmer registry fields in individual data"""
        # Get base individual values from parent
        individual_vals = super().get_individual_vals(fake)

        # Add farmer registry specific fields
        individual_vals.update(
            {
                "experience_years": random.randint(0, 40),
                "formal_agricultural_training": random.choice([True, False]),
                "farmer_household_size": random.randint(1, 10),
                "farmer_postal_address": fake.address(),
                "marital_status": random.choice(
                    ["single", "widowed", "married", "separated", "married_monogamous", "married_polygamous"]
                ),
                "highest_education_level": random.choice(
                    ["none", "primary", "secondary", "certificate", "diploma", "university", "tertiary"]
                ),
            }
        )

        return individual_vals

    def head_member_getter(self, group):
        return True

    def generate_groups(self, fake):
        """Override to include farmer registry related data creation"""
        # Call parent method to create the group
        group = super().generate_groups(fake)

        # Add farmer registry specific related data
        if random.uniform(0, 100) <= self.percentage_with_farm_details:
            self._generate_farm_details(fake, group)

        return group

    def generate_individuals(self, fake):
        """Override to include farmer registry related data creation"""
        # Call parent method to create the individual
        individual = super().generate_individuals(fake)

        # Individual farmer registry data is already included in get_individual_vals()
        # No additional related records needed for individuals

        return individual

    def _generate_demo_data(self, fake):
        """Override to include farmer registry specific data generation"""
        # Call parent method first
        super()._generate_demo_data(fake)

        # Farm details are now handled in generate_groups() method
        # No additional processing needed here

    def _generate_farm_details(self, fake, group):
        """Generate farm details for a group"""
        # Create farm details
        farm_detail_vals = self._get_farm_details_vals(fake)
        farm_detail_vals.update(
            {
                "details_farm_id": group.id,
            }
        )
        farm_detail = self.env["spp.farm.details"].create(farm_detail_vals)

        # Link to group
        group.farm_detail_id = farm_detail.id

        # Generate land records if applicable
        if random.uniform(0, 100) <= self.percentage_with_land_records:
            self._generate_land_records(fake, group)

        # Generate farm assets if applicable
        if random.uniform(0, 100) <= self.percentage_with_farm_assets:
            self._generate_farm_assets(fake, group)

        # Generate agricultural activities if applicable
        if random.uniform(0, 100) <= self.percentage_with_agricultural_activities:
            self._generate_agricultural_activities(fake, group)

        # Generate extension services if applicable
        # if random.uniform(0, 100) <= self.percentage_with_extension_services:
        #     self._generate_extension_services(fake, group)

    def _get_farm_details_vals(self, fake):
        """Get farm details values"""
        farm_type = random.choice(self.FARM_TYPES)
        farm_size = round(random.uniform(self.min_farm_size, self.max_farm_size), 2)

        vals = {
            "details_farm_type": farm_type[0],
            "farm_total_size": farm_size,
            "farm_size_under_crops": round(farm_size * random.uniform(0.1, 0.8), 2),
            "farm_size_under_livestock": round(farm_size * random.uniform(0.1, 0.6), 2),
            "farm_size_leased_out": round(farm_size * random.uniform(0, 0.3), 2),
            "farm_size_idle": round(farm_size * random.uniform(0, 0.2), 2),
            "details_legal_status": random.choice(self.LEGAL_STATUSES)[0],
        }

        # Add demo-specific farm details fields
        vals.update(self._get_demo_farm_details_vals(fake, farm_type[0]))

        return vals

    def _get_demo_farm_details_vals(self, fake, farm_type):
        """Get demo-specific farm details values"""
        vals = {}

        # Lease information
        if random.choice([True, False]):
            vals.update(
                {
                    "lease_term": random.randint(1, 20),
                    "lease_agreement_number": fake.bothify(text="LR-#######"),
                }
            )

        # Farm operations
        vals.update(
            {
                "another_farm": random.choice([True, False]),
                "growing_crops_subsistence": random.choice([True, False]),
                "growing_crops_sale": random.choice([True, False]),
                "rearing_livestock_subsistence": random.choice([True, False]),
                "rearing_livestock_sale": random.choice([True, False]),
                "tree_farming": random.choice([True, False]),
            }
        )

        # Livestock-specific fields
        if farm_type in ["livestock", "mixed"]:
            vals.update(
                {
                    "livestock_fertilizer_for_fodder": random.choice([True, False]),
                    "livestock_certified_pasture": random.choice([True, False]),
                    "livestock_assisted_reproductive_health_technology_ai": random.choice([True, False]),
                    "livestock_assisted_reproductive_health_technology_animal_horm": random.choice([True, False]),
                    "livestock_assisted_reproductive_health_technology_embryo_transf": random.choice([True, False]),
                    "livestock_animal_health_services_routine_vaccination": random.choice([True, False]),
                    "livestock_animal_health_services_disease_control": random.choice([True, False]),
                }
            )

        # Aquaculture-specific fields
        if farm_type in ["aquaculture", "mixed"]:
            vals.update(
                {
                    "aquaculture_type": random.choice(["freshwater", "marine", "brackish"]),
                    "aquaculture_subsistence": random.choice([True, False]),
                    "aquaculture_sale": random.choice([True, False]),
                    "aquaculture_main_inputs_fingerlings": random.choice([True, False]),
                    "aquaculture_main_inputs_feeds": random.choice([True, False]),
                    "aquaculture_main_inputs_fertilizers": random.choice([True, False]),
                    "aquaculture_utilize_fertilizer": random.choice([True, False]),
                    "aquaculture_production_level": random.choice(["extensive", "semi-intensive", "intensive"]),
                    "aquaculture_beneficiary_esp": random.choice([True, False]),
                }
            )

        # Farm technology
        vals.update(
            {
                "farm_technology_power_source": random.choice(
                    ["manual labor", "animal drought", "motorized", "wind", "solar", "grid electricity", "other"]
                ),
                "farm_technology_labor_source": random.choice(
                    ["family members", "temporary hired help", "permanent hired help"]
                ),
                "farm_technology_own_equipment": random.choice(["self", "community", "hirer"]),
            }
        )

        # Farm structures (randomly select some)
        structure_fields = [
            "farm_technology_structure_spray_race",
            "farm_technology_structure_animal_dip",
            "farm_technology_structure_loading_ramp",
            "farm_technology_structure_zero_grazing_unit",
            "farm_technology_structure_hay_store",
            "farm_technology_structure_feed_store",
            "farm_technology_structure_sick_bay",
            "farm_technology_structure_cattle_boma",
            "farm_technology_structure_milking_parlor",
            "farm_technology_structure_animal_crush",
            "farm_technology_structure_traditional_granary",
            "farm_technology_structure_modern_granary",
            "farm_technology_structure_general_store",
            "farm_technology_structure_hay_bailers",
            "farm_technology_structure_green_house",
            "farm_technology_structure_bee_house",
            "farm_technology_structure_hatchery",
            "farm_technology_structure_apriary",
        ]
        for field in structure_fields:
            vals[field] = random.choice([True, False])

        # Land and water management
        land_management_fields = [
            "land_water_management_crop_rotation",
            "land_water_management_green_cover_crop",
            "land_water_management_contour_ploughing",
            "land_water_management_deep_ripping",
            "land_water_management_grass_strips",
            "land_water_management_trash_line",
            "land_water_management_cambered_beds",
            "land_water_management_biogas_production",
            "land_water_management_mulching",
            "land_water_management_minimum_tillage",
            "land_water_management_manuring_composting",
            "land_water_management_organic_farming",
            "land_water_management_terracing",
            "land_water_management_water_harvesting",
            "land_water_management_zai_pits",
            "land_water_management_cut_off_drains",
            "land_water_management_conservation_agriculture",
            "land_water_management_integrated_pest_management",
        ]
        for field in land_management_fields:
            vals[field] = random.choice([True, False])

        # Additional land management fields
        vals.update(
            {
                "land_water_management_subsidized_fertilizer": random.choice([True, False]),
                "land_water_management_use_lime": random.choice([True, False]),
                "land_water_management_soil_testing": random.choice([True, False]),
                "land_water_management_undertake_irrigation": random.choice([True, False]),
            }
        )

        # Irrigation details (if irrigation is undertaken)
        if vals.get("land_water_management_undertake_irrigation"):
            vals.update(
                {
                    "land_water_management_irrigation_type": random.choice(
                        [
                            "furrow_canal",
                            "basin",
                            "bucket",
                            "centre_pivot",
                            "drip",
                            "furrow",
                            "sprinkler",
                            "flooding",
                            "other",
                        ]
                    ),
                    "land_water_management_irrigation_source": random.choice(
                        [
                            "locality water supply",
                            "water trucking",
                            "rain",
                            "natural rivers and streams",
                            "man made dam",
                            "shallow well or borehole",
                            "adjacent water body",
                            "harvested water",
                            "road runoff",
                            "water pan",
                        ]
                    ),
                    "land_water_management_total_irrigated_area": round(random.uniform(0.1, 10), 2),
                    "land_water_management_type_of_irrigation_project": random.choice(
                        ["public irrigation scheme", "private on farm initiative", "community scheme"]
                    ),
                    "land_water_management_type_of_irrigation_project_name": fake.company(),
                    "land_water_management_implementing_body": random.choice(
                        [
                            "county government",
                            "national government",
                            "implementing agents",
                            "national govt ministry",
                            "self",
                            "other",
                        ]
                    ),
                    "land_water_management_irrigation_scheme_membership": random.choice(["full member", "out grower"]),
                }
            )

        # Financial services
        vals.update(
            {
                "financial_services_main_income_source": random.choice(
                    [
                        "sale of farming produce",
                        "non-farm trading",
                        "salary from employment elsewhere",
                        "casual labor elsewhere",
                        "pension",
                        "remittances",
                        "cash transfer",
                        "other",
                    ]
                ),
                "financial_services_percentage_of_income_from_farming": round(random.uniform(0, 100), 1),
            }
        )

        # Organization memberships
        org_fields = [
            "financial_services_vulnerable_marginalized_group",
            "financial_services_faith_based_organization",
            "financial_services_community_based_organization",
            "financial_services_producer_group",
            "financial_services_marketing_group",
            "financial_services_table_banking_group",
            "financial_services_common_interest_group",
        ]
        for field in org_fields:
            vals[field] = random.choice([True, False])

        # Financial services
        financial_fields = [
            "financial_services_mobile_money_saving_loans",
            "financial_services_farmer_organization",
            "financial_services_other_money_lenders",
            "financial_services_self_salary_or_savings",
            "financial_services_family",
            "financial_services_commercial_bank",
            "financial_services_business_partners",
            "financial_services_savings_credit_groups",
            "financial_services_cooperatives",
            "financial_services_micro_finance_institutions",
            "financial_services_non_governmental_donors",
        ]
        for field in financial_fields:
            vals[field] = random.choice([True, False])

        # Insurance and records
        vals.update(
            {
                "financial_services_crop_insurance": random.choice([True, False]),
                "financial_services_livestock_insurance": random.choice([True, False]),
                "financial_services_fish_insurance": random.choice([True, False]),
                "financial_services_farm_building_insurance": random.choice([True, False]),
                "financial_services_written_farm_records": random.choice([True, False]),
                "financial_services_main_source_of_information_on_good_agricultu": random.choice(
                    [
                        "newspaper",
                        "extension services",
                        "internet",
                        "radio",
                        "television",
                        "public gatherings",
                        "relatives",
                    ]
                ),
                "financial_services_mode_of_extension_service": random.choice(
                    [
                        "e-extension",
                        "face-to-face",
                        "farmer field schools",
                        "group demonstrations",
                        "peer-to-peer",
                        "other",
                    ]
                ),
                "financial_services_main_extension_service_provider": random.choice(
                    ["private", "national government", "county government", "ngo", "other"]
                ),
            }
        )

        return vals

    def _generate_land_records(self, fake, group):
        """Generate land records for a farm"""
        num_parcels = random.randint(1, self.max_land_parcels_per_farm)

        for _ in range(num_parcels):
            land_vals = self._get_land_record_vals(fake, group)
            land_record = self.env["spp.land.record"].create(land_vals)

            # Link to group
            if hasattr(group, "farm_land_rec_id"):
                group.farm_land_rec_id = land_record.id

    def _get_land_record_vals(self, fake, group):
        """Get land record values"""
        land_use = random.choice(self.LAND_USES)

        # Get species based on land use
        species_ids = []
        if land_use[0] in ["cultivation", "mixed"]:
            species_id = self._get_random_species("crop")
            if species_id:
                species_ids.append(species_id)
        elif land_use[0] == "livestock":
            species_id = self._get_random_species("livestock")
            if species_id:
                species_ids.append(species_id)
        elif land_use[0] == "aquaculture":
            species_id = self._get_random_species("aquaculture")
            if species_id:
                species_ids.append(species_id)
        elif land_use[0] == "mixed":
            # For mixed use, add multiple species types
            for species_type in ["crop", "livestock", "aquaculture"]:
                if random.choice([True, False]):  # 50% chance for each type
                    species_id = self._get_random_species(species_type)
                    if species_id:
                        species_ids.append(species_id)

        return {
            "land_farm_id": group.id,
            "land_name": f"Parcel-{fake.bothify(text='??###')}",
            "land_acreage": round(random.uniform(0.1, 50), 2),
            "land_use": land_use[0],
            "species": [(6, 0, species_ids)] if species_ids else [(6, 0, [])],
            "owner_id": group.id,
            "lease_start": fake.date_between_dates(
                date_start=fields.Date.today() - datetime.timedelta(days=365 * 5), date_end=fields.Date.today()
            )
            if random.choice([True, False])
            else None,
            "lease_end": fake.date_between_dates(
                date_start=fields.Date.today(), date_end=fields.Date.today() + datetime.timedelta(days=365 * 10)
            )
            if random.choice([True, False])
            else None,
        }

    def _generate_farm_assets(self, fake, group):
        """Generate farm assets and machinery"""
        num_assets = random.randint(1, self.max_assets_per_farm)

        for _ in range(num_assets):
            # Generate farm assets
            asset_vals = self._get_farm_asset_vals(fake, group)
            self.env["spp.farm.asset"].create(asset_vals)

            # Generate machinery (50% chance)
            if random.choice([True, False]):
                machinery_vals = self._get_machinery_vals(fake, group)
                self.env["spp.farm.asset"].create(machinery_vals)

    def _get_farm_asset_vals(self, fake, group):
        """Get farm asset values"""
        return {
            "asset_farm_id": group.id,
            "asset_type": self._get_random_asset_type(),
            "technology_used": fake.word(),
            "quantity": random.randint(1, 10),
        }

    def _get_machinery_vals(self, fake, group):
        """Get machinery values"""
        return {
            "machinery_farm_id": group.id,
            "machinery_type": self._get_random_machinery_type(),
            "technology_used": fake.word(),
            "quantity": random.randint(1, 5),
            "machine_working_status": random.choice(["Working", "Needs Repair", "Broken"]),
        }

    def _generate_agricultural_activities(self, fake, group):
        """Generate agricultural activities"""
        # Ensure season is available
        season_id = self._get_random_season()
        if not season_id:
            _logger.warning(f"No active season available for group {group.id}. Skipping agricultural activities.")
            return
        
        season = self.env["spp.farm.season"].browse(season_id)
        _logger.debug(f"Generating agricultural activities for group {group.id} using season: {season.name}")
            
        num_activities = random.randint(1, self.max_activities_per_farm)

        for _ in range(num_activities):
            activity_vals = self._get_agricultural_activity_vals(fake, group, season_id)
            try:
                self.env["spp.farm.activity"].create(activity_vals)
            except Exception as e:
                _logger.error(f"Failed to create agricultural activity for group {group.id}: {str(e)}")

    def _get_agricultural_activity_vals(self, fake, group, season_id):
        """Get agricultural activity values"""
        activity_type = random.choice(self.ACTIVITY_TYPES)

        vals = {
            "activity_type": activity_type[0],
            "purpose": random.choice(self.PRODUCTION_PURPOSES)[0],
            "season_id": season_id,
        }

        # Set the appropriate farm field based on activity type
        if activity_type[0] == "crop":
            vals["crop_farm_id"] = group.id
            # Add crop-specific fields
            vals.update(self._get_crop_activity_vals(fake))
        elif activity_type[0] == "livestock":
            vals["live_farm_id"] = group.id
            # Add livestock-specific fields
            vals.update(self._get_livestock_activity_vals(fake))
        elif activity_type[0] == "aquaculture":
            vals["aqua_farm_id"] = group.id
            # Add aquaculture-specific fields
            vals.update(self._get_aquaculture_activity_vals(fake))

        return vals

    def _get_crop_activity_vals(self, fake):
        """Get crop-specific activity values"""
        return {
            "species_id": self._get_random_species("crop"),
            "cultivation_water_source": random.choice(["irrigated", "rainfed"]),
            "cultivation_production_system": random.choice(
                ["Mono-cropping", "Mixed-cropping", "Agroforestry", "Plantation", "Greenhouse"]
            ),
            "cultivation_chemical_interventions": self._get_random_chemicals(2),
            "cultivation_fertilizer_interventions": self._get_random_fertilizers(2),
        }

    def _get_livestock_activity_vals(self, fake):
        """Get livestock-specific activity values"""
        return {
            "species_id": self._get_random_species("livestock"),
            "livestock_production_system": random.choice(
                [
                    "ranching",
                    "communal grazing",
                    "pastoralism",
                    "rotational grazing",
                    "zero grazing",
                    "semi zero grazing",
                    "feedlots",
                    "free range",
                    "tethering",
                    "other",
                ]
            ),
            "livestock_feed_items": self._get_random_feed_items(3),
        }

    def _get_aquaculture_activity_vals(self, fake):
        """Get aquaculture-specific activity values"""
        return {
            "species_id": self._get_random_species("aquaculture"),
            "aquaculture_production_system": random.choice(
                ["ponds", "cages", "tanks", "raceways", "recirculating systems", "aquaponics", "other"]
            ),
            "aquaculture_number_of_fingerlings": random.randint(100, 10000),
        }

    def _generate_extension_services(self, fake, group):
        """Generate farm extension services"""
        num_services = random.randint(1, 3)

        for _ in range(num_services):
            extension_vals = self._get_extension_service_vals(fake, group)
            self.env["spp.farm.extension"].create(extension_vals)

    def _get_extension_service_vals(self, fake, group):
        """Get extension service values"""
        return {
            "farm_id": group.id,
            "extension_services_type": fake.word(),
            "service_provider": fake.company(),
            "service_date": fake.date_between_dates(
                date_start=fields.Date.today() - datetime.timedelta(days=365), date_end=fields.Date.today()
            ),
            "service_description": fake.text(max_nb_chars=200),
        }

    def _get_random_asset_type(self):
        """Get a random asset type"""
        asset_types = self.env["asset.type"].search([])
        if asset_types:
            return random.choice(asset_types).id
        return None

    def _get_random_machinery_type(self):
        """Get a random machinery type"""
        machinery_types = self.env["machinery.type"].search([])
        if machinery_types:
            return random.choice(machinery_types).id
        return None

    def _generate_species_data(self, fake):
        """Generate species data for the demo"""
        # Create some sample species if they don't exist
        species_data = [
            # Crop species
            {"name": "Rice", "species_type": "crop", "description": "Oryza sativa - staple food crop"},
            {"name": "Wheat", "species_type": "crop", "description": "Triticum aestivum - cereal crop"},
            {"name": "Maize", "species_type": "crop", "description": "Zea mays - corn crop"},
            {"name": "Soybean", "species_type": "crop", "description": "Glycine max - legume crop"},
            {"name": "Tomato", "species_type": "crop", "description": "Solanum lycopersicum - vegetable crop"},
            {"name": "Potato", "species_type": "crop", "description": "Solanum tuberosum - tuber crop"},
            # Livestock species
            {"name": "Cattle", "species_type": "livestock", "description": "Bos taurus - dairy and beef cattle"},
            {"name": "Sheep", "species_type": "livestock", "description": "Ovis aries - wool and meat production"},
            {"name": "Goat", "species_type": "livestock", "description": "Capra hircus - milk and meat production"},
            {"name": "Pig", "species_type": "livestock", "description": "Sus scrofa domesticus - pork production"},
            {
                "name": "Chicken",
                "species_type": "livestock",
                "description": "Gallus gallus domesticus - poultry production",
            },
            # Aquaculture species
            {
                "name": "Tilapia",
                "species_type": "aquaculture",
                "description": "Oreochromis niloticus - freshwater fish",
            },
            {"name": "Catfish", "species_type": "aquaculture", "description": "Clarias gariepinus - freshwater fish"},
            {"name": "Carp", "species_type": "aquaculture", "description": "Cyprinus carpio - freshwater fish"},
            {"name": "Shrimp", "species_type": "aquaculture", "description": "Penaeus vannamei - marine crustacean"},
        ]

        for species_info in species_data:
            existing = self.env["spp.farm.species"].search([("name", "=", species_info["name"])])
            if not existing:
                self.env["spp.farm.species"].create(species_info)

    def _generate_chemical_data(self, fake):
        """Generate chemical intervention data for the demo"""
        chemical_data = [
            {"name": "Herbicide"},
            {"name": "Insecticide"},
            {"name": "Fungicide"},
            {"name": "Pesticide"},
            {"name": "Weed Control"},
            {"name": "Pest Control"},
        ]

        for chemical_info in chemical_data:
            existing = self.env["spp.farm.chemical"].search([("name", "=", chemical_info["name"])])
            if not existing:
                self.env["spp.farm.chemical"].create(chemical_info)

    def _generate_fertilizer_data(self, fake):
        """Generate fertilizer data for the demo"""
        fertilizer_data = [
            {"name": "Organic Fertilizer"},
            {"name": "NPK Fertilizer"},
            {"name": "Urea"},
            {"name": "Compost"},
            {"name": "Manure"},
            {"name": "Lime"},
        ]

        for fertilizer_info in fertilizer_data:
            existing = self.env["spp.fertilizer"].search([("name", "=", fertilizer_info["name"])])
            if not existing:
                self.env["spp.fertilizer"].create(fertilizer_info)

    def _generate_feed_items_data(self, fake):
        """Generate feed items data for the demo"""
        feed_data = [
            {"name": "Grass"},
            {"name": "Hay"},
            {"name": "Silage"},
            {"name": "Grain"},
            {"name": "Concentrate Feed"},
            {"name": "Mineral Supplements"},
        ]

        for feed_info in feed_data:
            existing = self.env["spp.feed.items"].search([("name", "=", feed_info["name"])])
            if not existing:
                self.env["spp.feed.items"].create(feed_info)

    def _generate_season_data(self, fake):
        """Generate or find agricultural season data for the demo"""
        try:
            # Search for existing season matching name, dates, and active state
            existing_season = self.env["spp.farm.season"].search([
                ("name", "=", self.season_name),
                ("date_start", "=", self.season_start_date),
                ("date_end", "=", self.season_end_date),
                ("state", "=", "active"),
            ], limit=1)
            
            if existing_season:
                _logger.info(f"Using existing active season: {existing_season.name} (ID: {existing_season.id})")
                return existing_season
            
            # Search for season with same name but different dates or status
            existing_season_by_name = self.env["spp.farm.season"].search([
                ("name", "=", self.season_name),
            ], limit=1)
            
            if existing_season_by_name:
                # Update existing season if it's not closed
                if existing_season_by_name.state != "closed":
                    _logger.info(f"Updating existing season: {existing_season_by_name.name}")
                    existing_season_by_name.write({
                        "date_start": self.season_start_date,
                        "date_end": self.season_end_date,
                    })
                    if existing_season_by_name.state == "draft":
                        existing_season_by_name.action_activate()
                    _logger.info(f"Season updated and activated: {existing_season_by_name.name} (ID: {existing_season_by_name.id})")
                    return existing_season_by_name
                else:
                    _logger.warning(f"Season '{self.season_name}' exists but is closed. Creating new season with modified name.")
                    # Create new season with modified name
                    season_vals = {
                        "name": f"{self.season_name} (Demo)",
                        "description": f"Demo agricultural season created on {fields.Date.today()}",
                        "date_start": self.season_start_date,
                        "date_end": self.season_end_date,
                        "state": "draft",
                    }
                    new_season = self.env["spp.farm.season"].create(season_vals)
                    new_season.action_activate()
                    _logger.info(f"Created and activated new season: {new_season.name} (ID: {new_season.id})")
                    return new_season
            
            # Create new season if none exists
            season_vals = {
                "name": self.season_name,
                "description": f"Demo agricultural season created on {fields.Date.today()}",
                "date_start": self.season_start_date,
                "date_end": self.season_end_date,
                "state": "draft",
            }
            new_season = self.env["spp.farm.season"].create(season_vals)
            new_season.action_activate()
            _logger.info(f"Created and activated new season: {new_season.name} (ID: {new_season.id})")
            return new_season
            
        except Exception as e:
            _logger.error(f"Failed to generate/find season: {str(e)}")
            raise ValidationError(_(f"Failed to create or find agricultural season: {str(e)}"))

    def _get_random_species(self, species_type):
        """Get a random species of the specified type"""
        species = self.env["spp.farm.species"].search([("species_type", "=", species_type)])
        if species:
            return random.choice(species).id
        return None

    def _get_random_chemicals(self, limit=3):
        """Get random chemical interventions"""
        chemicals = self.env["spp.farm.chemical"].search([])
        if chemicals:
            selected = random.sample(chemicals.ids, min(limit, len(chemicals)))
            return [(6, 0, selected)]
        return [(6, 0, [])]

    def _get_random_fertilizers(self, limit=3):
        """Get random fertilizer interventions"""
        fertilizers = self.env["spp.fertilizer"].search([])
        if fertilizers:
            selected = random.sample(fertilizers.ids, min(limit, len(fertilizers)))
            return [(6, 0, selected)]
        return [(6, 0, [])]

    def _get_random_feed_items(self, limit=3):
        """Get random feed items"""
        feed_items = self.env["spp.feed.items"].search([])
        if feed_items:
            selected = random.sample(feed_items.ids, min(limit, len(feed_items)))
            return [(6, 0, selected)]
        return [(6, 0, [])]

    def _get_random_season(self):
        """Get the configured active season, creating it if necessary"""
        # Use cached season if available
        if hasattr(self, '_active_season') and self._active_season:
            _logger.debug(f"Using cached season: {self._active_season.name} (ID: {self._active_season.id})")
            return self._active_season.id
        
        # Generate/find the season if not already cached
        _logger.info("Season not cached, generating/finding season now")
        fake = Faker(self.locale_origin.faker_locale or "en_US") if self.locale_origin else Faker("en_US")
        self._active_season = self._generate_season_data(fake)
        
        if self._active_season:
            _logger.info(f"Using season: {self._active_season.name} (ID: {self._active_season.id})")
            return self._active_season.id
        
        _logger.error("Failed to generate/find active season! Agricultural activities cannot be created.")
        return None
