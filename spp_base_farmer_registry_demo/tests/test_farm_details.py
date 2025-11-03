# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestFarmDetails(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        # Create test farm (group)
        cls.farm = cls.env["res.partner"].create(
            {
                "name": "Test Farm",
                "is_group": True,
                "is_registrant": True,
            }
        )

    def test_01_farm_details_lease_fields(self):
        """Test farm details lease fields"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "lease_term": 5,
                "lease_agreement_number": "LR-123456",
            }
        )

        self.assertEqual(farm_details.lease_term, 5)
        self.assertEqual(farm_details.lease_agreement_number, "LR-123456")

    def test_02_farm_details_another_farm_field(self):
        """Test another_farm boolean field"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "another_farm": True,
            }
        )

        self.assertTrue(farm_details.another_farm)

    def test_03_farm_details_crop_fields(self):
        """Test crop-related boolean fields"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "growing_crops_subsistence": True,
                "growing_crops_sale": True,
            }
        )

        self.assertTrue(farm_details.growing_crops_subsistence)
        self.assertTrue(farm_details.growing_crops_sale)

    def test_04_farm_details_livestock_fields(self):
        """Test livestock-related boolean fields"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "rearing_livestock_subsistence": True,
                "rearing_livestock_sale": False,
            }
        )

        self.assertTrue(farm_details.rearing_livestock_subsistence)
        self.assertFalse(farm_details.rearing_livestock_sale)

    def test_05_farm_details_tree_farming(self):
        """Test tree farming field"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "tree_farming": True,
            }
        )

        self.assertTrue(farm_details.tree_farming)

    def test_06_livestock_fertilizer_and_pasture(self):
        """Test livestock fertilizer and pasture fields"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "livestock_fertilizer_for_fodder": True,
                "livestock_certified_pasture": False,
            }
        )

        self.assertTrue(farm_details.livestock_fertilizer_for_fodder)
        self.assertFalse(farm_details.livestock_certified_pasture)

    def test_07_livestock_assisted_reproductive_tech(self):
        """Test livestock assisted reproductive technology fields"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "livestock_assisted_reproductive_health_technology_ai": True,
                "livestock_assisted_reproductive_health_technology_animal_horm": True,
                "livestock_assisted_reproductive_health_technology_embryo_transf": False,
            }
        )

        self.assertTrue(farm_details.livestock_assisted_reproductive_health_technology_ai)
        self.assertTrue(farm_details.livestock_assisted_reproductive_health_technology_animal_horm)
        self.assertFalse(farm_details.livestock_assisted_reproductive_health_technology_embryo_transf)

    def test_08_livestock_animal_health_services(self):
        """Test livestock animal health services fields"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "livestock_animal_health_services_routine_vaccination": True,
                "livestock_animal_health_services_disease_control": True,
            }
        )

        self.assertTrue(farm_details.livestock_animal_health_services_routine_vaccination)
        self.assertTrue(farm_details.livestock_animal_health_services_disease_control)

    def test_09_aquaculture_type_field(self):
        """Test aquaculture type selection field"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "aquaculture_type": "freshwater",
            }
        )

        self.assertEqual(farm_details.aquaculture_type, "freshwater")

        # Test other types
        farm_details.write({"aquaculture_type": "marine"})
        self.assertEqual(farm_details.aquaculture_type, "marine")

        farm_details.write({"aquaculture_type": "brackish"})
        self.assertEqual(farm_details.aquaculture_type, "brackish")

    def test_10_aquaculture_subsistence_and_sale(self):
        """Test aquaculture subsistence and sale fields"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "aquaculture_subsistence": True,
                "aquaculture_sale": True,
            }
        )

        self.assertTrue(farm_details.aquaculture_subsistence)
        self.assertTrue(farm_details.aquaculture_sale)

    def test_11_aquaculture_main_inputs(self):
        """Test aquaculture main inputs fields"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "aquaculture_main_inputs_fingerlings": True,
                "aquaculture_main_inputs_feeds": True,
                "aquaculture_main_inputs_fertilizers": False,
            }
        )

        self.assertTrue(farm_details.aquaculture_main_inputs_fingerlings)
        self.assertTrue(farm_details.aquaculture_main_inputs_feeds)
        self.assertFalse(farm_details.aquaculture_main_inputs_fertilizers)

    def test_12_aquaculture_production_level(self):
        """Test aquaculture production level field"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "aquaculture_production_level": "extensive",
            }
        )

        self.assertEqual(farm_details.aquaculture_production_level, "extensive")

        # Test other levels
        for level in ["semi-intensive", "intensive"]:
            farm_details.write({"aquaculture_production_level": level})
            self.assertEqual(farm_details.aquaculture_production_level, level)

    def test_13_aquaculture_esp_beneficiary(self):
        """Test aquaculture ESP beneficiary field"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "aquaculture_beneficiary_esp": True,
            }
        )

        self.assertTrue(farm_details.aquaculture_beneficiary_esp)

    def test_14_farm_technology_power_source(self):
        """Test farm technology power source field"""
        power_sources = [
            "manual labor",
            "animal drought",
            "motorized",
            "wind",
            "solar",
            "grid electricity",
            "other",
        ]

        for source in power_sources:
            farm_details = self.env["spp.farm.details"].create(
                {
                    "details_farm_id": self.farm.id,
                    "farm_technology_power_source": source,
                }
            )
            self.assertEqual(farm_details.farm_technology_power_source, source)

    def test_15_farm_technology_labor_source(self):
        """Test farm technology labor source field"""
        labor_sources = ["family members", "temporary hired help", "permanent hired help"]

        for source in labor_sources:
            farm_details = self.env["spp.farm.details"].create(
                {
                    "details_farm_id": self.farm.id,
                    "farm_technology_labor_source": source,
                }
            )
            self.assertEqual(farm_details.farm_technology_labor_source, source)

    def test_16_farm_technology_own_equipment(self):
        """Test farm technology own equipment field"""
        equipment_owners = ["self", "community", "hirer"]

        for owner in equipment_owners:
            farm_details = self.env["spp.farm.details"].create(
                {
                    "details_farm_id": self.farm.id,
                    "farm_technology_own_equipment": owner,
                }
            )
            self.assertEqual(farm_details.farm_technology_own_equipment, owner)

    def test_17_farm_technology_structures(self):
        """Test farm technology structure boolean fields"""
        structure_fields = {
            "farm_technology_structure_spray_race": True,
            "farm_technology_structure_animal_dip": False,
            "farm_technology_structure_loading_ramp": True,
            "farm_technology_structure_zero_grazing_unit": False,
            "farm_technology_structure_hay_store": True,
            "farm_technology_structure_feed_store": True,
            "farm_technology_structure_sick_bay": False,
            "farm_technology_structure_cattle_boma": True,
            "farm_technology_structure_milking_parlor": False,
            "farm_technology_structure_animal_crush": True,
        }

        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                **structure_fields,
            }
        )

        for field, expected_value in structure_fields.items():
            self.assertEqual(getattr(farm_details, field), expected_value)

    def test_18_more_farm_technology_structures(self):
        """Test additional farm technology structure fields"""
        structure_fields = {
            "farm_technology_structure_traditional_granary": True,
            "farm_technology_structure_modern_granary": False,
            "farm_technology_structure_general_store": True,
            "farm_technology_structure_hay_bailers": False,
            "farm_technology_structure_green_house": True,
            "farm_technology_structure_bee_house": False,
            "farm_technology_structure_hatchery": True,
            "farm_technology_structure_apriary": False,
        }

        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                **structure_fields,
            }
        )

        for field, expected_value in structure_fields.items():
            self.assertEqual(getattr(farm_details, field), expected_value)

    def test_19_land_water_management_practices(self):
        """Test land and water management practice fields"""
        management_fields = {
            "land_water_management_crop_rotation": True,
            "land_water_management_green_cover_crop": False,
            "land_water_management_contour_ploughing": True,
            "land_water_management_deep_ripping": False,
            "land_water_management_grass_strips": True,
            "land_water_management_trash_line": False,
            "land_water_management_cambered_beds": True,
            "land_water_management_biogas_production": False,
            "land_water_management_mulching": True,
            "land_water_management_minimum_tillage": False,
        }

        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                **management_fields,
            }
        )

        for field, expected_value in management_fields.items():
            self.assertEqual(getattr(farm_details, field), expected_value)

    def test_20_more_land_water_management(self):
        """Test additional land and water management fields"""
        management_fields = {
            "land_water_management_manuring_composting": True,
            "land_water_management_organic_farming": False,
            "land_water_management_terracing": True,
            "land_water_management_water_harvesting": False,
            "land_water_management_zai_pits": True,
            "land_water_management_cut_off_drains": False,
            "land_water_management_conservation_agriculture": True,
            "land_water_management_integrated_pest_management": False,
        }

        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                **management_fields,
            }
        )

        for field, expected_value in management_fields.items():
            self.assertEqual(getattr(farm_details, field), expected_value)

    def test_21_land_water_management_subsidized_and_lime(self):
        """Test subsidized fertilizer and lime usage fields"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "land_water_management_subsidized_fertilizer": True,
                "land_water_management_use_lime": False,
                "land_water_management_soil_testing": True,
                "land_water_management_undertake_irrigation": True,
            }
        )

        self.assertTrue(farm_details.land_water_management_subsidized_fertilizer)
        self.assertFalse(farm_details.land_water_management_use_lime)
        self.assertTrue(farm_details.land_water_management_soil_testing)
        self.assertTrue(farm_details.land_water_management_undertake_irrigation)

    def test_22_irrigation_type_field(self):
        """Test irrigation type selection field"""
        irrigation_types = [
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

        for irr_type in irrigation_types:
            farm_details = self.env["spp.farm.details"].create(
                {
                    "details_farm_id": self.farm.id,
                    "land_water_management_irrigation_type": irr_type,
                }
            )
            self.assertEqual(farm_details.land_water_management_irrigation_type, irr_type)

    def test_23_irrigation_source_field(self):
        """Test irrigation source selection field"""
        irrigation_sources = [
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

        for source in irrigation_sources:
            farm_details = self.env["spp.farm.details"].create(
                {
                    "details_farm_id": self.farm.id,
                    "land_water_management_irrigation_source": source,
                }
            )
            self.assertEqual(farm_details.land_water_management_irrigation_source, source)

    def test_24_irrigation_area_and_project(self):
        """Test irrigation area and project fields"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "land_water_management_total_irrigated_area": 25.5,
                "land_water_management_type_of_irrigation_project": "public irrigation scheme",
                "land_water_management_type_of_irrigation_project_name": "Test Project",
            }
        )

        self.assertEqual(farm_details.land_water_management_total_irrigated_area, 25.5)
        self.assertEqual(farm_details.land_water_management_type_of_irrigation_project, "public irrigation scheme")
        self.assertEqual(farm_details.land_water_management_type_of_irrigation_project_name, "Test Project")

    def test_25_irrigation_implementing_body(self):
        """Test irrigation implementing body field"""
        implementing_bodies = [
            "county government",
            "national government",
            "implementing agents",
            "national govt ministry",
            "self",
            "other",
        ]

        for body in implementing_bodies:
            farm_details = self.env["spp.farm.details"].create(
                {
                    "details_farm_id": self.farm.id,
                    "land_water_management_implementing_body": body,
                }
            )
            self.assertEqual(farm_details.land_water_management_implementing_body, body)

    def test_26_irrigation_scheme_membership(self):
        """Test irrigation scheme membership field"""
        memberships = ["full member", "out grower"]

        for membership in memberships:
            farm_details = self.env["spp.farm.details"].create(
                {
                    "details_farm_id": self.farm.id,
                    "land_water_management_irrigation_scheme_membership": membership,
                }
            )
            self.assertEqual(farm_details.land_water_management_irrigation_scheme_membership, membership)

    def test_27_financial_services_main_income_source(self):
        """Test financial services main income source field"""
        income_sources = [
            "sale of farming produce",
            "non-farm trading",
            "salary from employment elsewhere",
            "casual labor elsewhere",
            "pension",
            "remittances",
            "cash transfer",
            "other",
        ]

        for source in income_sources:
            farm_details = self.env["spp.farm.details"].create(
                {
                    "details_farm_id": self.farm.id,
                    "financial_services_main_income_source": source,
                }
            )
            self.assertEqual(farm_details.financial_services_main_income_source, source)

    def test_28_financial_services_income_percentage(self):
        """Test financial services income percentage field"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "financial_services_percentage_of_income_from_farming": 75.5,
            }
        )

        self.assertEqual(farm_details.financial_services_percentage_of_income_from_farming, 75.5)

    def test_29_financial_services_organization_memberships(self):
        """Test financial services organization membership fields"""
        org_fields = {
            "financial_services_vulnerable_marginalized_group": True,
            "financial_services_faith_based_organization": False,
            "financial_services_community_based_organization": True,
            "financial_services_producer_group": False,
            "financial_services_marketing_group": True,
            "financial_services_table_banking_group": False,
            "financial_services_common_interest_group": True,
        }

        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                **org_fields,
            }
        )

        for field, expected_value in org_fields.items():
            self.assertEqual(getattr(farm_details, field), expected_value)

    def test_30_financial_services_finance_sources(self):
        """Test financial services finance source fields"""
        finance_fields = {
            "financial_services_mobile_money_saving_loans": True,
            "financial_services_farmer_organization": False,
            "financial_services_other_money_lenders": True,
            "financial_services_self_salary_or_savings": False,
            "financial_services_family": True,
            "financial_services_commercial_bank": False,
            "financial_services_business_partners": True,
            "financial_services_savings_credit_groups": False,
            "financial_services_cooperatives": True,
            "financial_services_micro_finance_institutions": False,
            "financial_services_non_governmental_donors": True,
        }

        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                **finance_fields,
            }
        )

        for field, expected_value in finance_fields.items():
            self.assertEqual(getattr(farm_details, field), expected_value)

    def test_31_financial_services_insurance_fields(self):
        """Test financial services insurance fields"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "financial_services_crop_insurance": True,
                "financial_services_livestock_insurance": False,
                "financial_services_fish_insurance": True,
                "financial_services_farm_building_insurance": False,
            }
        )

        self.assertTrue(farm_details.financial_services_crop_insurance)
        self.assertFalse(farm_details.financial_services_livestock_insurance)
        self.assertTrue(farm_details.financial_services_fish_insurance)
        self.assertFalse(farm_details.financial_services_farm_building_insurance)

    def test_32_financial_services_records_and_information(self):
        """Test financial services records and information fields"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "financial_services_written_farm_records": True,
                "financial_services_main_source_of_information_on_good_agricultu": "extension services",
                "financial_services_mode_of_extension_service": "face-to-face",
                "financial_services_main_extension_service_provider": "county government",
            }
        )

        self.assertTrue(farm_details.financial_services_written_farm_records)
        self.assertEqual(
            farm_details.financial_services_main_source_of_information_on_good_agricultu, "extension services"
        )
        self.assertEqual(farm_details.financial_services_mode_of_extension_service, "face-to-face")
        self.assertEqual(farm_details.financial_services_main_extension_service_provider, "county government")

    def test_33_create_multiple_farm_details(self):
        """Test creating multiple farm details for different farms"""
        farm1 = self.env["res.partner"].create(
            {
                "name": "Farm 1",
                "is_group": True,
                "is_registrant": True,
            }
        )

        farm2 = self.env["res.partner"].create(
            {
                "name": "Farm 2",
                "is_group": True,
                "is_registrant": True,
            }
        )

        details1 = self.env["spp.farm.details"].create(
            {
                "details_farm_id": farm1.id,
                "lease_term": 5,
            }
        )

        details2 = self.env["spp.farm.details"].create(
            {
                "details_farm_id": farm2.id,
                "lease_term": 10,
            }
        )

        self.assertEqual(details1.lease_term, 5)
        self.assertEqual(details2.lease_term, 10)

    def test_34_update_farm_details(self):
        """Test updating farm details"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "lease_term": 3,
                "aquaculture_type": "freshwater",
            }
        )

        farm_details.write(
            {
                "lease_term": 7,
                "aquaculture_type": "marine",
            }
        )

        self.assertEqual(farm_details.lease_term, 7)
        self.assertEqual(farm_details.aquaculture_type, "marine")

    def test_35_farm_details_comprehensive(self):
        """Test creating farm details with many fields at once"""
        farm_details = self.env["spp.farm.details"].create(
            {
                "details_farm_id": self.farm.id,
                "lease_term": 5,
                "lease_agreement_number": "LR-789012",
                "another_farm": True,
                "growing_crops_subsistence": True,
                "growing_crops_sale": True,
                "rearing_livestock_subsistence": True,
                "rearing_livestock_sale": False,
                "tree_farming": True,
                "aquaculture_type": "freshwater",
                "aquaculture_subsistence": True,
                "farm_technology_power_source": "solar",
                "land_water_management_undertake_irrigation": True,
                "land_water_management_irrigation_type": "drip",
                "financial_services_main_income_source": "sale of farming produce",
                "financial_services_crop_insurance": True,
            }
        )

        # Verify all fields were set correctly
        self.assertEqual(farm_details.lease_term, 5)
        self.assertTrue(farm_details.another_farm)
        self.assertTrue(farm_details.growing_crops_subsistence)
        self.assertEqual(farm_details.aquaculture_type, "freshwater")
        self.assertEqual(farm_details.farm_technology_power_source, "solar")
        self.assertEqual(farm_details.land_water_management_irrigation_type, "drip")
        self.assertTrue(farm_details.financial_services_crop_insurance)
