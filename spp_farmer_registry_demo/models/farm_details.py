from odoo import fields, models


# TODO: Maybe make it an event data that is displayed as a tab in the Farm
class FarmDetails(models.Model):
    _inherit = "spp.farm.details"

    # If leased (lease term in years)
    lease_term = fields.Integer(string="If leased (lease term in years)")

    # LR/Cert. No/Agreement no
    lease_agreement_number = fields.Char(string="LR/Cert. No/Agreement no")

    another_farm = fields.Boolean(string="Do you have another farm?")

    growing_crops_subsistence = fields.Boolean(string="Growing crops for subsistence?")
    growing_crops_sale = fields.Boolean(string="Growing crops for sale?")
    rearing_livestock_subsistence = fields.Boolean(string="Rearing livestock for subsistence?")
    rearing_livestock_sale = fields.Boolean(string="Rearing livestock for sale?")

    tree_farming = fields.Boolean(string="Tree farming?")

    # Livestock
    livestock_fertilizer_for_fodder = fields.Boolean(string="Do you utilize fertilizer for fodder and pasture?")
    livestock_certified_pasture = fields.Boolean(string="Do you use certified pasture & fodder seeds?")
    livestock_assisted_reproductive_health_technology_ai = fields.Boolean(string="Artificial Insemination (AI)")
    livestock_assisted_reproductive_health_technology_animal_horm = fields.Boolean(string="Animal hormones")
    livestock_assisted_reproductive_health_technology_embryo_transf = fields.Boolean(string="Embryo Transfer")
    livestock_animal_health_services_routine_vaccination = fields.Boolean(string="Routine vaccination")
    livestock_animal_health_services_disease_control = fields.Boolean(string="Disease control / curative measures")

    # Aquaculture
    aquaculture_type = fields.Selection(
        [
            ("freshwater", "Freshwater"),
            ("marine", "Marine"),
            ("brackish", "Brackish"),
        ],
        string="Water Body Type",
    )
    aquaculture_subsistence = fields.Boolean(string="Aquaculture for subsistence?")
    aquaculture_sale = fields.Boolean(string="Aquaculture for sale?")

    aquaculture_main_inputs_fingerlings = fields.Boolean(string="Fingerlings")
    aquaculture_main_inputs_feeds = fields.Boolean(string="Manufactured feeds")
    aquaculture_main_inputs_fertilizers = fields.Boolean(string="Fertilizers")
    aquaculture_utilize_fertilizer = fields.Boolean(string="Do you utilize fertilizer in the ponds?")
    aquaculture_production_level = fields.Selection(
        [
            ("extensive", "Extensive"),
            ("semi-intensive", "Semi-intensive"),
            ("intensive", "Intensive"),
        ],
        string="What is your production level?",
    )
    aquaculture_beneficiary_esp = fields.Boolean(
        string="Are you a beneficiary of the government of Kenya's economic stimulus programme (ESP)?"
    )

    # Farm technology
    farm_technology_power_source = fields.Selection(
        [
            ("manual labor", "Manual labor"),
            ("animal drought", "Animal drought"),
            ("motorized", "Motorized (fossil fuels)"),
            ("wind", "Wind"),
            ("solar", "Solar"),
            ("grid electricity", "Grid electricity"),
            ("other", "Other"),
        ],
        string="What are the sources of power for farm activities?",
    )
    farm_technology_labor_source = fields.Selection(
        [
            ("family members", "Family members"),
            ("temporary hired help", "Temporary hired help"),
            ("permanent hired help", "Permanent Hired Help"),
        ],
        string="For labor, what is the main source?",
    )

    farm_technology_own_equipment = fields.Selection(
        [
            ("self", "Self / Family"),
            ("community", "Community"),
            ("hirer", "Hirer"),
        ],
        string="Who Owns Most Of The Frequently Used Equipment?",
    )

    # Wondering if that should not be part of assets
    farm_technology_structure_spray_race = fields.Boolean(default=False, string="Spray Race")
    farm_technology_structure_animal_dip = fields.Boolean(default=False, string="Animal Dip")
    farm_technology_structure_loading_ramp = fields.Boolean(default=False, string="Loading Ramp")
    farm_technology_structure_zero_grazing_unit = fields.Boolean(default=False, string="Zero Grazing Unit")
    farm_technology_structure_hay_store = fields.Boolean(default=False, string="Hay Store")
    farm_technology_structure_feed_store = fields.Boolean(default=False, string="Feed Store")
    farm_technology_structure_sick_bay = fields.Boolean(default=False, string="Sick Bay")
    farm_technology_structure_cattle_boma = fields.Boolean(default=False, string="Cattle Boma")
    farm_technology_structure_milking_parlor = fields.Boolean(default=False, string="Milking parlor")
    farm_technology_structure_animal_crush = fields.Boolean(default=False, string="Animal crush")
    farm_technology_structure_traditional_granary = fields.Boolean(default=False, string="Traditional Granary")
    farm_technology_structure_modern_granary = fields.Boolean(default=False, string="Modern Granary")
    farm_technology_structure_general_store = fields.Boolean(default=False, string="General Store")
    farm_technology_structure_hay_bailers = fields.Boolean(default=False, string="Hay Bailers")
    farm_technology_structure_green_house = fields.Boolean(default=False, string="Green house")
    farm_technology_structure_bee_house = fields.Boolean(default=False, string="Bee House")
    farm_technology_structure_hatchery = fields.Boolean(default=False, string="Hatchery")
    farm_technology_structure_apriary = fields.Boolean(default=False, string="Apriary")

    # Farm land and water management
    land_water_management_crop_rotation = fields.Boolean(default=False, string="Crop Rotation")
    land_water_management_green_cover_crop = fields.Boolean(default=False, string="Green cover crop")
    land_water_management_contour_ploughing = fields.Boolean(default=False, string="Contour ploughing/Ridging")
    land_water_management_deep_ripping = fields.Boolean(default=False, string="Deep ripping")
    land_water_management_grass_strips = fields.Boolean(default=False, string="Grass strips")
    land_water_management_trash_line = fields.Boolean(default=False, string="Trash line")
    land_water_management_cambered_beds = fields.Boolean(default=False, string="Cambered beds")
    land_water_management_biogas_production = fields.Boolean(default=False, string="Biogas production")
    land_water_management_mulching = fields.Boolean(default=False, string="Mulching")
    land_water_management_minimum_tillage = fields.Boolean(default=False, string="Minimum Tillage")
    land_water_management_manuring_composting = fields.Boolean(default=False, string="Manuring/Composting")
    land_water_management_organic_farming = fields.Boolean(default=False, string="Organic farming")
    land_water_management_terracing = fields.Boolean(default=False, string="Terracing")
    land_water_management_water_harvesting = fields.Boolean(default=False, string="Water harvesting")
    land_water_management_zai_pits = fields.Boolean(default=False, string="Zai pits")
    land_water_management_cut_off_drains = fields.Boolean(default=False, string="Cut-off drains")
    land_water_management_conservation_agriculture = fields.Boolean(default=False, string="Conservation agriculture")
    land_water_management_integrated_pest_management = fields.Boolean(
        default=False, string="Integrated pest management"
    )

    land_water_management_subsidized_fertilizer = fields.Boolean(
        default=False, string="Have you benefited from Govt. Subsidized fertilizer?"
    )
    land_water_management_use_lime = fields.Boolean(default=False, string="Do you use lime on your soil?")
    land_water_management_soil_testing = fields.Boolean(
        default=False, string="Have you done soil testing in the last 3 years?"
    )
    land_water_management_undertake_irrigation = fields.Boolean(default=False, string="Do you undertake irrigation?")

    land_water_management_irrigation_type = fields.Selection(
        [
            ("furrow_canal", "Furrow Canal"),
            ("basin", "Basin"),
            ("bucket", "Bucket"),
            ("centre_pivot", "Centre Pivot"),
            ("drip", "Drip"),
            ("furrow", "Furrow"),
            ("sprinkler", "Sprinkler"),
            ("flooding", "Flooding"),
            ("other", "Other"),
        ],
        string="Type of irrigation",
    )

    land_water_management_irrigation_source = fields.Selection(
        [
            ("locality water supply", "Locality water supply"),
            ("water trucking", "Water trucking"),
            ("rain", "Rain"),
            ("natural rivers and streams", "Natural rivers and streams"),
            ("man made dam", "Man made dam"),
            ("shallow well or borehole", "Shallow well or borehole"),
            ("adjacent water body", "Adjacent water body"),
            ("harvested water", "Harvested water"),
            ("road runoff", "Road runoff"),
            ("water pan", "Water pan"),
        ]
    )
    land_water_management_total_irrigated_area = fields.Float(string="Total irrigated area")
    land_water_management_type_of_irrigation_project = fields.Selection(
        [
            ("public irrigation scheme", "Public irrigation scheme"),
            ("private on farm initiative", "Private on farm initiative"),
            ("community scheme", "Community scheme"),
        ],
        string="Type of irrigation project",
    )
    land_water_management_type_of_irrigation_project_name = fields.Char(
        string="Type of irrigation project name", required=False
    )
    land_water_management_implementing_body = fields.Selection(
        [
            ("county government", "County Government"),
            ("national government", "National Government"),
            ("implementing agents", "Implementing Agents"),
            ("national govt ministry", "National Govt. Ministry"),
            ("self", "Self (Private)"),
            ("other", "Other"),
        ],
        string="Implementing body",
    )
    land_water_management_irrigation_scheme_membership = fields.Selection(
        [
            ("full member", "Full member"),
            ("out grower", "Out grower"),
        ],
        string="Irrigation scheme membership",
    )

    # Financials and Services
    financial_services_main_income_source = fields.Selection(
        [
            ("sale of farming produce", "Sale of farming produce"),
            ("non-farm trading", "Non-farm trading"),
            ("salary from employment elsewhere", "Salary from employment elsewhere"),
            ("casual labor elsewhere", "Casual labor elsewhere"),
            ("pension", "Pension"),
            ("remittances", "Remittances"),
            ("cash transfer", "Cash transfer"),
            ("other", "Other"),
        ],
        string="What is your main source of income by priority?",
    )
    financial_services_percentage_of_income_from_farming = fields.Float(
        string="What percentage of your income comes from farming activities?"
    )

    financial_services_vulnerable_marginalized_group = fields.Boolean(string="Vulnerable/ Marginalized Group")
    financial_services_faith_based_organization = fields.Boolean(string="Faith Based Organization")
    financial_services_community_based_organization = fields.Boolean(string="Community Based Organization")
    financial_services_producer_group = fields.Boolean(string="Producer Group")
    financial_services_marketing_group = fields.Boolean(string="Marketing Group")
    financial_services_table_banking_group = fields.Boolean(string="Table Banking Group")
    financial_services_common_interest_group = fields.Boolean(string="Common Interest Group")

    financial_services_mobile_money_saving_loans = fields.Boolean(string="Mobile Money saving & loans")
    financial_services_farmer_organization = fields.Boolean(string="Farmer Organization")
    financial_services_other_money_lenders = fields.Boolean(string="Other money lenders")
    financial_services_self_salary_or_savings = fields.Boolean(string="Self (Salary or Savings)")
    financial_services_family = fields.Boolean(string="Family")
    financial_services_commercial_bank = fields.Boolean(string="Commercial Bank")
    financial_services_business_partners = fields.Boolean(string="Business partners")
    financial_services_savings_credit_groups = fields.Boolean(string="Savings & Credit groups")
    financial_services_cooperatives = fields.Boolean(string="Cooperatives")
    financial_services_micro_finance_institutions = fields.Boolean(string="Micro-finance institutions")
    financial_services_non_governmental_donors = fields.Boolean(string="Non-governmental donors")

    financial_services_crop_insurance = fields.Boolean(string="Do you insure your crops?")
    financial_services_livestock_insurance = fields.Boolean(string="Do you insure your livestock?")
    financial_services_fish_insurance = fields.Boolean(string="Do you insure your fish?")
    financial_services_farm_building_insurance = fields.Boolean(
        string="Do you insure your farm buildings and other assets?"
    )
    financial_services_written_farm_records = fields.Boolean(string="Do you keep written farm records?")
    financial_services_main_source_of_information_on_good_agricultu = fields.Selection(
        [
            ("newspaper", "Newspaper"),
            ("extension services", "Extension services"),
            ("internet", "Internet"),
            ("radio", "Radio"),
            ("television", "Television"),
            ("public gatherings", "Public gatherings"),
            ("relatives", "Relatives"),
        ],
        string="What is your main source of information on good agricultural practices (GAP)?",
    )
    financial_services_mode_of_extension_service = fields.Selection(
        [
            ("e-extension", "E-Extension"),
            ("face-to-face", "Face-to-face"),
            ("farmer field schools", "Farmer field schools"),
            ("group demonstrations", "Group demonstrations"),
            ("peer-to-peer", "Peer-to-Peer"),
            ("other", "Other"),
        ],
        string="What is the mode of extension service that you receive?",
    )
    financial_services_main_extension_service_provider = fields.Selection(
        [
            ("private", "Private"),
            ("national government", "National Govt."),
            ("county government", "County Government"),
            ("ngo", "NGO"),
            ("other", "Other"),
        ],
        string="What is your main extension service provider?",
    )
