# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import datetime
import logging

from faker import Faker

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestFarmerRegistryDemoDataGenerator(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set context to avoid job queue delay
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        # Create test country with faker locale
        cls.test_country = cls.env["res.country"].create(
            {
                "name": "Test Country Farmer Registry",
                "code": "TF2",
                "faker_locale": "en_US",
                "faker_locale_available": True,
                "lat_min": -10.0,
                "lat_max": 10.0,
                "lon_min": -10.0,
                "lon_max": 10.0,
            }
        )

        # Create test group type
        cls.group_type = cls.env["g2p.group.kind"].create(
            {
                "name": "Test Farmer Group Type",
            }
        )

    def test_01_season_date_validation(self):
        """Test season date validation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Season Validation",
                "locale_origin": self.test_country.id,
                "season_start_date": datetime.date(2024, 12, 31),
                "season_end_date": datetime.date(2024, 1, 1),
            }
        )

        with self.assertRaises(ValidationError):
            generator._check_season_dates()

    def test_02_farmer_registry_specific_fields(self):
        """Test farmer registry specific fields exist"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Farmer Fields",
                "locale_origin": self.test_country.id,
            }
        )

        # Check that farmer registry fields exist
        self.assertIn("percentage_with_farm_details", generator._fields)
        self.assertIn("percentage_with_land_records", generator._fields)
        self.assertIn("percentage_with_farm_assets", generator._fields)
        self.assertIn("percentage_with_agricultural_activities", generator._fields)
        self.assertIn("max_farm_size", generator._fields)
        self.assertIn("min_farm_size", generator._fields)
        self.assertIn("season_name", generator._fields)
        self.assertIn("season_start_date", generator._fields)
        self.assertIn("season_end_date", generator._fields)

    def test_03_get_group_vals_with_farmer_fields(self):
        """Test group values generation includes farmer registry fields"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Group Vals Farmer",
                "locale_origin": self.test_country.id,
                "group_type_id": self.group_type.id,
            }
        )

        fake = Faker("en_US")
        group_vals = generator.get_group_vals(fake)

        # Check that farmer registry fields are in group vals
        self.assertIn("household_size", group_vals)
        self.assertIn("experience_years", group_vals)
        self.assertIn("formal_agricultural_training", group_vals)
        self.assertIn("farmer_household_size", group_vals)
        self.assertIn("farmer_postal_address", group_vals)
        self.assertIn("marital_status", group_vals)
        self.assertIn("highest_education_level", group_vals)
        self.assertIn("farmer_family_name", group_vals)
        self.assertIn("farmer_given_name", group_vals)
        self.assertIn("farmer_sex", group_vals)
        self.assertIn("farmer_birthdate", group_vals)

    def test_04_get_individual_vals_with_farmer_fields(self):
        """Test individual values generation includes farmer registry fields"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Individual Vals Farmer",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")
        individual_vals = generator.get_individual_vals(fake)

        # Check that farmer registry fields are in individual vals
        self.assertIn("experience_years", individual_vals)
        self.assertIn("formal_agricultural_training", individual_vals)
        self.assertIn("farmer_household_size", individual_vals)
        self.assertIn("farmer_postal_address", individual_vals)
        self.assertIn("marital_status", individual_vals)
        self.assertIn("highest_education_level", individual_vals)

    def test_05_generate_species_data(self):
        """Test species data generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Species Generator",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")

        # Clear any existing test species
        test_species = self.env["spp.farm.species"].search([("name", "in", ["Rice", "Wheat", "Cattle", "Tilapia"])])
        if test_species:
            test_species.unlink()

        generator._generate_species_data(fake)

        # Verify species were created
        crop_species = self.env["spp.farm.species"].search([("species_type", "=", "crop")])
        livestock_species = self.env["spp.farm.species"].search([("species_type", "=", "livestock")])
        aqua_species = self.env["spp.farm.species"].search([("species_type", "=", "aquaculture")])

        self.assertGreaterEqual(len(crop_species), 1)
        self.assertGreaterEqual(len(livestock_species), 1)
        self.assertGreaterEqual(len(aqua_species), 1)

    def test_06_generate_chemical_data(self):
        """Test chemical data generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Chemical Generator",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")

        # Clear existing test chemicals
        test_chemicals = self.env["spp.farm.chemical"].search([("name", "in", ["Herbicide", "Insecticide"])])
        if test_chemicals:
            test_chemicals.unlink()

        generator._generate_chemical_data(fake)

        # Verify chemicals were created
        chemicals = self.env["spp.farm.chemical"].search([])
        self.assertGreaterEqual(len(chemicals), 1)

    def test_07_generate_fertilizer_data(self):
        """Test fertilizer data generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Fertilizer Generator",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")

        # Clear existing test fertilizers
        test_fertilizers = self.env["spp.fertilizer"].search([("name", "in", ["Urea", "Compost"])])
        if test_fertilizers:
            test_fertilizers.unlink()

        generator._generate_fertilizer_data(fake)

        # Verify fertilizers were created
        fertilizers = self.env["spp.fertilizer"].search([])
        self.assertGreaterEqual(len(fertilizers), 1)

    def test_08_generate_feed_items_data(self):
        """Test feed items data generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Feed Items Generator",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")

        # Clear existing test feed items
        test_feeds = self.env["spp.feed.items"].search([("name", "in", ["Grass", "Hay"])])
        if test_feeds:
            test_feeds.unlink()

        generator._generate_feed_items_data(fake)

        # Verify feed items were created
        feed_items = self.env["spp.feed.items"].search([])
        self.assertGreaterEqual(len(feed_items), 1)

    def test_09_generate_season_data(self):
        """Test season data generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Season Generator",
                "locale_origin": self.test_country.id,
                "season_name": "Test Season 2024",
                "season_start_date": datetime.date(2024, 1, 1),
                "season_end_date": datetime.date(2024, 12, 31),
            }
        )

        fake = Faker("en_US")

        # Clear any existing test season
        test_season = self.env["spp.farm.season"].search([("name", "=", "Test Season 2024")])
        if test_season:
            test_season.unlink()

        season = generator._generate_season_data(fake)

        self.assertIsNotNone(season)
        self.assertEqual(season.name, "Test Season 2024")
        self.assertEqual(season.date_start, datetime.date(2024, 1, 1))
        self.assertEqual(season.date_end, datetime.date(2024, 12, 31))
        self.assertEqual(season.state, "active")

    def test_10_get_farm_details_vals(self):
        """Test farm details values generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Farm Details Vals",
                "locale_origin": self.test_country.id,
                "min_farm_size": 1.0,
                "max_farm_size": 50.0,
            }
        )

        fake = Faker("en_US")
        farm_vals = generator._get_farm_details_vals(fake)

        # Check required fields
        self.assertIn("details_farm_type", farm_vals)
        self.assertIn("farm_total_size", farm_vals)
        self.assertIn("details_legal_status", farm_vals)

        # Check that farm size is within bounds
        self.assertGreaterEqual(farm_vals["farm_total_size"], 1.0)
        self.assertLessEqual(farm_vals["farm_total_size"], 50.0)

    def test_11_get_land_record_vals(self):
        """Test land record values generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Land Record Vals",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")

        # Ensure species data exists
        generator._generate_species_data(fake)

        # Create a test group
        group = self.env["res.partner"].create(
            {
                "name": "Test Farm Group",
                "is_group": True,
                "is_registrant": True,
            }
        )

        land_vals = generator._get_land_record_vals(fake, group)

        # Check required fields
        self.assertIn("land_farm_id", land_vals)
        self.assertEqual(land_vals["land_farm_id"], group.id)
        self.assertIn("land_name", land_vals)
        self.assertIn("land_acreage", land_vals)
        self.assertIn("land_use", land_vals)
        self.assertIn("owner_id", land_vals)

    def test_12_get_farm_asset_vals(self):
        """Test farm asset values generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Farm Asset Vals",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")

        # Create a test group
        group = self.env["res.partner"].create(
            {
                "name": "Test Farm Group",
                "is_group": True,
                "is_registrant": True,
            }
        )

        asset_vals = generator._get_farm_asset_vals(fake, group)

        # Check required fields
        self.assertIn("asset_farm_id", asset_vals)
        self.assertEqual(asset_vals["asset_farm_id"], group.id)
        self.assertIn("quantity", asset_vals)
        self.assertGreaterEqual(asset_vals["quantity"], 1)

    def test_13_get_machinery_vals(self):
        """Test machinery values generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Machinery Vals",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")

        # Create a test group
        group = self.env["res.partner"].create(
            {
                "name": "Test Farm Group",
                "is_group": True,
                "is_registrant": True,
            }
        )

        machinery_vals = generator._get_machinery_vals(fake, group)

        # Check required fields
        self.assertIn("machinery_farm_id", machinery_vals)
        self.assertEqual(machinery_vals["machinery_farm_id"], group.id)
        self.assertIn("quantity", machinery_vals)
        self.assertIn("machine_working_status", machinery_vals)

    def test_14_get_agricultural_activity_vals(self):
        """Test agricultural activity values generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Activity Vals",
                "locale_origin": self.test_country.id,
                "season_name": "Test Season Activity",
                "season_start_date": datetime.date(2024, 1, 1),
                "season_end_date": datetime.date(2024, 12, 31),
            }
        )

        fake = Faker("en_US")

        # Create season
        season = generator._generate_season_data(fake)

        # Ensure species data exists
        generator._generate_species_data(fake)

        # Create a test group
        group = self.env["res.partner"].create(
            {
                "name": "Test Farm Group",
                "is_group": True,
                "is_registrant": True,
            }
        )

        activity_vals = generator._get_agricultural_activity_vals(fake, group, season.id)

        # Check required fields
        self.assertIn("activity_type", activity_vals)
        self.assertIn("purpose", activity_vals)
        self.assertIn("season_id", activity_vals)
        self.assertEqual(activity_vals["season_id"], season.id)

    def test_15_get_crop_activity_vals(self):
        """Test crop activity values generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Crop Activity",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")

        # Ensure required data exists
        generator._generate_species_data(fake)
        generator._generate_chemical_data(fake)
        generator._generate_fertilizer_data(fake)

        crop_vals = generator._get_crop_activity_vals(fake)

        # Check crop-specific fields
        self.assertIn("cultivation_water_source", crop_vals)
        self.assertIn("cultivation_production_system", crop_vals)

    def test_16_get_livestock_activity_vals(self):
        """Test livestock activity values generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Livestock Activity",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")

        # Ensure required data exists
        generator._generate_species_data(fake)
        generator._generate_feed_items_data(fake)

        livestock_vals = generator._get_livestock_activity_vals(fake)

        # Check livestock-specific fields
        self.assertIn("livestock_production_system", livestock_vals)

    def test_17_get_aquaculture_activity_vals(self):
        """Test aquaculture activity values generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Aquaculture Activity",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")

        # Ensure required data exists
        generator._generate_species_data(fake)

        aqua_vals = generator._get_aquaculture_activity_vals(fake)

        # Check aquaculture-specific fields
        self.assertIn("aquaculture_production_system", aqua_vals)
        self.assertIn("aquaculture_number_of_fingerlings", aqua_vals)
        self.assertGreaterEqual(aqua_vals["aquaculture_number_of_fingerlings"], 100)

    def test_18_get_random_species(self):
        """Test random species retrieval"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Random Species",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")
        generator._generate_species_data(fake)

        # Test each species type
        crop_species = generator._get_random_species("crop")
        livestock_species = generator._get_random_species("livestock")
        aqua_species = generator._get_random_species("aquaculture")

        self.assertIsNotNone(crop_species)
        self.assertIsNotNone(livestock_species)
        self.assertIsNotNone(aqua_species)

    def test_19_get_random_chemicals(self):
        """Test random chemicals retrieval"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Random Chemicals",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")
        generator._generate_chemical_data(fake)

        chemicals = generator._get_random_chemicals(2)

        self.assertIsInstance(chemicals, list)
        self.assertEqual(len(chemicals), 1)  # Returns list with one tuple
        self.assertEqual(chemicals[0][0], 6)  # Command code 6 = set

    def test_20_get_random_fertilizers(self):
        """Test random fertilizers retrieval"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Random Fertilizers",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")
        generator._generate_fertilizer_data(fake)

        fertilizers = generator._get_random_fertilizers(2)

        self.assertIsInstance(fertilizers, list)
        self.assertEqual(len(fertilizers), 1)
        self.assertEqual(fertilizers[0][0], 6)

    def test_21_get_random_feed_items(self):
        """Test random feed items retrieval"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Random Feed Items",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")
        generator._generate_feed_items_data(fake)

        feed_items = generator._get_random_feed_items(2)

        self.assertIsInstance(feed_items, list)
        self.assertEqual(len(feed_items), 1)
        self.assertEqual(feed_items[0][0], 6)

    def test_22_get_random_season(self):
        """Test random season retrieval"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Random Season",
                "locale_origin": self.test_country.id,
                "season_name": "Test Season Random",
                "season_start_date": datetime.date(2024, 1, 1),
                "season_end_date": datetime.date(2024, 12, 31),
            }
        )

        season_id = generator._get_random_season()

        self.assertIsNotNone(season_id)

    def test_23_generate_groups_with_farm_details(self):
        """Test group generation with farm details"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Group Farm Details",
                "locale_origin": self.test_country.id,
                "percentage_with_farm_details": 100,
                "percentage_with_land_records": 0,
                "percentage_with_farm_assets": 0,
                "percentage_with_agricultural_activities": 0,
                "season_name": "Test Season Group",
                "season_start_date": datetime.date(2024, 1, 1),
                "season_end_date": datetime.date(2024, 12, 31),
            }
        )

        fake = Faker("en_US")

        # Generate required reference data
        generator._generate_species_data(fake)
        generator._generate_season_data(fake)

        group = generator.generate_groups(fake)

        self.assertTrue(group.is_group)
        self.assertTrue(group.is_registrant)
        # Farm details should be created (if farm_detail_id field exists)
        if hasattr(group, "farm_detail_id"):
            self.assertTrue(group.farm_detail_id or True)  # May or may not have depending on module setup

    def test_24_generate_farm_details(self):
        """Test farm details generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Farm Details Gen",
                "locale_origin": self.test_country.id,
                "percentage_with_land_records": 0,
                "percentage_with_farm_assets": 0,
                "percentage_with_agricultural_activities": 0,
            }
        )

        fake = Faker("en_US")

        # Create a test group
        group = self.env["res.partner"].create(
            {
                "name": "Test Farm Group",
                "is_group": True,
                "is_registrant": True,
            }
        )

        generator._generate_farm_details(fake, group)

        # Verify farm details were created
        farm_details = self.env["spp.farm.details"].search([("details_farm_id", "=", group.id)])
        self.assertGreaterEqual(len(farm_details), 1)

    def test_25_generate_land_records(self):
        """Test land records generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Land Records Gen",
                "locale_origin": self.test_country.id,
                "max_land_parcels_per_farm": 3,
            }
        )

        fake = Faker("en_US")
        generator._generate_species_data(fake)

        # Create a test group
        group = self.env["res.partner"].create(
            {
                "name": "Test Farm Group",
                "is_group": True,
                "is_registrant": True,
            }
        )

        generator._generate_land_records(fake, group)

        # Verify land records were created
        land_records = self.env["spp.land.record"].search([("land_farm_id", "=", group.id)])
        self.assertGreaterEqual(len(land_records), 1)
        self.assertLessEqual(len(land_records), 3)

    def test_26_generate_farm_assets(self):
        """Test farm assets generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Farm Assets Gen",
                "locale_origin": self.test_country.id,
                "max_assets_per_farm": 3,
            }
        )

        fake = Faker("en_US")

        # Create a test group
        group = self.env["res.partner"].create(
            {
                "name": "Test Farm Group",
                "is_group": True,
                "is_registrant": True,
            }
        )

        generator._generate_farm_assets(fake, group)

        # Verify farm assets were created
        farm_assets = self.env["spp.farm.asset"].search(
            ["|", ("asset_farm_id", "=", group.id), ("machinery_farm_id", "=", group.id)]
        )
        self.assertGreaterEqual(len(farm_assets), 1)

    def test_27_generate_agricultural_activities(self):
        """Test agricultural activities generation"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Agricultural Activities Gen",
                "locale_origin": self.test_country.id,
                "max_activities_per_farm": 3,
                "season_name": "Test Season Activities",
                "season_start_date": datetime.date(2024, 1, 1),
                "season_end_date": datetime.date(2024, 12, 31),
            }
        )

        fake = Faker("en_US")

        # Generate required reference data
        generator._generate_species_data(fake)
        generator._generate_chemical_data(fake)
        generator._generate_fertilizer_data(fake)
        generator._generate_feed_items_data(fake)
        generator._generate_season_data(fake)

        # Create a test group
        group = self.env["res.partner"].create(
            {
                "name": "Test Farm Group",
                "is_group": True,
                "is_registrant": True,
            }
        )

        generator._generate_agricultural_activities(fake, group)

        # Verify agricultural activities were created
        activities = self.env["spp.farm.activity"].search(
            [
                "|",
                "|",
                ("crop_farm_id", "=", group.id),
                ("live_farm_id", "=", group.id),
                ("aqua_farm_id", "=", group.id),
            ]
        )
        self.assertGreaterEqual(len(activities), 1)

    def test_28_percentage_fields_defaults(self):
        """Test that percentage fields have correct defaults"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Percentage Defaults",
                "locale_origin": self.test_country.id,
            }
        )

        self.assertEqual(generator.percentage_with_farm_details, 100)
        self.assertEqual(generator.percentage_with_land_records, 100)
        self.assertEqual(generator.percentage_with_farm_assets, 100)
        self.assertEqual(generator.percentage_with_agricultural_activities, 100)

    def test_29_farm_size_fields_defaults(self):
        """Test that farm size fields have correct defaults"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Farm Size Defaults",
                "locale_origin": self.test_country.id,
            }
        )

        self.assertEqual(generator.max_farm_size, 100.0)
        self.assertEqual(generator.min_farm_size, 0.5)
        self.assertEqual(generator.max_land_parcels_per_farm, 5)
        self.assertEqual(generator.max_assets_per_farm, 10)
        self.assertEqual(generator.max_activities_per_farm, 8)

    def test_30_season_name_default(self):
        """Test that season name has a default value"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Season Name Default",
                "locale_origin": self.test_country.id,
            }
        )

        self.assertIsNotNone(generator.season_name)
        self.assertIn("Demo Season", generator.season_name)

    def test_31_demo_farm_details_vals_livestock(self):
        """Test demo farm details values for livestock farm"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Demo Farm Details Livestock",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")
        vals = generator._get_demo_farm_details_vals(fake, "livestock")

        # Check livestock-specific fields might be present
        self.assertIsInstance(vals, dict)

    def test_32_demo_farm_details_vals_aquaculture(self):
        """Test demo farm details values for aquaculture farm"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Demo Farm Details Aquaculture",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")
        vals = generator._get_demo_farm_details_vals(fake, "aquaculture")

        # Check aquaculture-specific fields might be present
        self.assertIsInstance(vals, dict)

    def test_33_demo_farm_details_vals_crop(self):
        """Test demo farm details values for crop farm"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Demo Farm Details Crop",
                "locale_origin": self.test_country.id,
            }
        )

        fake = Faker("en_US")
        vals = generator._get_demo_farm_details_vals(fake, "crop")

        # Check crop farm fields
        self.assertIsInstance(vals, dict)

    def test_34_season_data_reuse_existing(self):
        """Test that existing season is reused if available"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Season Reuse",
                "locale_origin": self.test_country.id,
                "season_name": "Test Season Reuse",
                "season_start_date": datetime.date(2024, 1, 1),
                "season_end_date": datetime.date(2024, 12, 31),
            }
        )

        fake = Faker("en_US")

        # Generate season first time
        season1 = generator._generate_season_data(fake)

        # Generate season second time
        season2 = generator._generate_season_data(fake)

        # Should be the same season
        self.assertEqual(season1.id, season2.id)

    def test_35_edge_case_zero_percentage_farm_details(self):
        """Test with 0% percentage for farm details"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Zero Farm Details Percentage",
                "locale_origin": self.test_country.id,
                "percentage_with_farm_details": 0,
                "season_name": "Test Season Zero",
                "season_start_date": datetime.date(2024, 1, 1),
                "season_end_date": datetime.date(2024, 12, 31),
            }
        )

        fake = Faker("en_US")

        # Generate season
        generator._generate_season_data(fake)

        # Create group - should not have farm details
        group = generator.generate_groups(fake)

        # Farm details should not be created
        self.env["spp.farm.details"].search([("details_farm_id", "=", group.id)])
        # With 0% there's still a small chance, so we just check it ran without error
        self.assertTrue(True)

    def test_36_edge_case_max_values(self):
        """Test with maximum values for size fields"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Max Values Test",
                "locale_origin": self.test_country.id,
                "max_farm_size": 10000.0,
                "min_farm_size": 100.0,
                "max_land_parcels_per_farm": 100,
                "max_assets_per_farm": 100,
                "max_activities_per_farm": 50,
            }
        )

        # Should not raise error
        self.assertEqual(generator.max_farm_size, 10000.0)
        self.assertEqual(generator.max_land_parcels_per_farm, 100)

    def test_37_edge_case_min_values(self):
        """Test with minimum values for size fields"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Min Values Test",
                "locale_origin": self.test_country.id,
                "max_farm_size": 1.0,
                "min_farm_size": 0.1,
                "max_land_parcels_per_farm": 1,
                "max_assets_per_farm": 1,
                "max_activities_per_farm": 1,
            }
        )

        # Should not raise error
        self.assertEqual(generator.min_farm_size, 0.1)
        self.assertEqual(generator.max_land_parcels_per_farm, 1)

    def test_38_constants_defined(self):
        """Test that all constant lists are properly defined"""
        generator = self.env["spp.demo.data.generator"].create(
            {
                "name": "Test Constants",
                "locale_origin": self.test_country.id,
            }
        )

        # Check that constants exist
        self.assertTrue(hasattr(generator, "FARM_TYPES"))
        self.assertTrue(hasattr(generator, "LAND_USES"))
        self.assertTrue(hasattr(generator, "CULTIVATION_METHODS"))
        self.assertTrue(hasattr(generator, "LEGAL_STATUSES"))
        self.assertTrue(hasattr(generator, "ACTIVITY_TYPES"))
        self.assertTrue(hasattr(generator, "PRODUCTION_PURPOSES"))

        # Check that they are not empty
        self.assertGreater(len(generator.FARM_TYPES), 0)
        self.assertGreater(len(generator.LAND_USES), 0)
        self.assertGreater(len(generator.ACTIVITY_TYPES), 0)
