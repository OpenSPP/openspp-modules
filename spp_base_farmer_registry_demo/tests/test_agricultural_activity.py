# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import datetime
import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestAgriculturalActivity(TransactionCase):
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
                "name": "Test Farm Activity",
                "is_group": True,
                "is_registrant": True,
            }
        )

        # Create test user with farm manager role
        cls.farm_manager = cls.env["res.users"].create(
            {
                "name": "Farm Manager",
                "login": "farm_manager",
                "groups_id": [(4, cls.env.ref("spp_base_farmer_registry.group_spp_farm_manager").id)],
            }
        )

        # Create test season
        cls.season = (
            cls.env["spp.farm.season"]
            .with_user(cls.farm_manager)
            .create(
                {
                    "name": "Test Season 2024",
                    "date_start": datetime.date(2024, 1, 1),
                    "date_end": datetime.date(2024, 12, 31),
                    "state": "draft",
                }
            )
        )
        cls.season.with_user(cls.farm_manager).action_activate()

        # Create test species
        cls.crop_species = cls.env["spp.farm.species"].create(
            {
                "name": "Test Crop",
                "species_type": "crop",
            }
        )

        cls.livestock_species = cls.env["spp.farm.species"].create(
            {
                "name": "Test Livestock",
                "species_type": "livestock",
            }
        )

        cls.aqua_species = cls.env["spp.farm.species"].create(
            {
                "name": "Test Fish",
                "species_type": "aquaculture",
            }
        )

        # Create test chemicals
        cls.chemical = cls.env["spp.farm.chemical"].create(
            {
                "name": "Test Herbicide",
            }
        )

        # Create test fertilizers
        cls.fertilizer = cls.env["spp.fertilizer"].create(
            {
                "name": "Test Fertilizer",
            }
        )

        # Create test feed items
        cls.feed_item = cls.env["spp.feed.items"].create(
            {
                "name": "Test Feed",
            }
        )

    def test_01_crop_cultivation_water_source(self):
        """Test cultivation water source field"""
        activity = self.env["spp.farm.activity"].create(
            {
                "crop_farm_id": self.farm.id,
                "activity_type": "crop",
                "species_id": self.crop_species.id,
                "season_id": self.season.id,
                "cultivation_water_source": "irrigated",
            }
        )

        self.assertEqual(activity.cultivation_water_source, "irrigated")

        # Test rainfed
        activity.write({"cultivation_water_source": "rainfed"})
        self.assertEqual(activity.cultivation_water_source, "rainfed")

    def test_02_crop_production_system(self):
        """Test cultivation production system field"""
        production_systems = [
            "Mono-cropping",
            "Mixed-cropping",
            "Agroforestry",
            "Plantation",
            "Greenhouse",
        ]

        for system in production_systems:
            activity = self.env["spp.farm.activity"].create(
                {
                    "crop_farm_id": self.farm.id,
                    "activity_type": "crop",
                    "species_id": self.crop_species.id,
                    "season_id": self.season.id,
                    "cultivation_production_system": system,
                }
            )
            self.assertEqual(activity.cultivation_production_system, system)

    def test_03_crop_chemical_interventions(self):
        """Test cultivation chemical interventions many2many field"""
        activity = self.env["spp.farm.activity"].create(
            {
                "crop_farm_id": self.farm.id,
                "activity_type": "crop",
                "species_id": self.crop_species.id,
                "season_id": self.season.id,
                "cultivation_chemical_interventions": [(6, 0, [self.chemical.id])],
            }
        )

        self.assertIn(self.chemical, activity.cultivation_chemical_interventions)

    def test_04_crop_fertilizer_interventions(self):
        """Test cultivation fertilizer interventions many2many field"""
        activity = self.env["spp.farm.activity"].create(
            {
                "crop_farm_id": self.farm.id,
                "activity_type": "crop",
                "species_id": self.crop_species.id,
                "season_id": self.season.id,
                "cultivation_fertilizer_interventions": [(6, 0, [self.fertilizer.id])],
            }
        )

        self.assertIn(self.fertilizer, activity.cultivation_fertilizer_interventions)

    def test_05_livestock_production_system(self):
        """Test livestock production system field"""
        production_systems = [
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

        for system in production_systems:
            activity = self.env["spp.farm.activity"].create(
                {
                    "live_farm_id": self.farm.id,
                    "activity_type": "livestock",
                    "species_id": self.livestock_species.id,
                    "season_id": self.season.id,
                    "livestock_production_system": system,
                }
            )
            self.assertEqual(activity.livestock_production_system, system)

    def test_06_livestock_feed_items(self):
        """Test livestock feed items many2many field"""
        activity = self.env["spp.farm.activity"].create(
            {
                "live_farm_id": self.farm.id,
                "activity_type": "livestock",
                "species_id": self.livestock_species.id,
                "season_id": self.season.id,
                "livestock_feed_items": [(6, 0, [self.feed_item.id])],
            }
        )

        self.assertIn(self.feed_item, activity.livestock_feed_items)

    def test_07_aquaculture_production_system(self):
        """Test aquaculture production system field"""
        production_systems = [
            "ponds",
            "cages",
            "tanks",
            "raceways",
            "recirculating systems",
            "aquaponics",
            "other",
        ]

        for system in production_systems:
            activity = self.env["spp.farm.activity"].create(
                {
                    "aqua_farm_id": self.farm.id,
                    "activity_type": "aquaculture",
                    "species_id": self.aqua_species.id,
                    "season_id": self.season.id,
                    "aquaculture_production_system": system,
                }
            )
            self.assertEqual(activity.aquaculture_production_system, system)

    def test_08_aquaculture_number_of_fingerlings(self):
        """Test aquaculture number of fingerlings field"""
        activity = self.env["spp.farm.activity"].create(
            {
                "aqua_farm_id": self.farm.id,
                "activity_type": "aquaculture",
                "species_id": self.aqua_species.id,
                "season_id": self.season.id,
                "aquaculture_number_of_fingerlings": 5000,
            }
        )

        self.assertEqual(activity.aquaculture_number_of_fingerlings, 5000)

    def test_09_onchange_farm_id(self):
        """Test onchange farm_id clears land_id"""
        # Create a land record
        land_record = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Test Land",
                "land_acreage": 10.0,
            }
        )

        # Create activity with land
        activity = self.env["spp.farm.activity"].create(
            {
                "live_farm_id": self.farm.id,
                "activity_type": "livestock",
                "species_id": self.livestock_species.id,
                "season_id": self.season.id,
                "land_id": land_record.id,
            }
        )

        # Trigger onchange
        activity._onchange_farm_id()

        # land_id should be cleared
        self.assertFalse(activity.land_id)

    def test_10_crop_activity_comprehensive(self):
        """Test creating crop activity with all fields"""
        # Create multiple chemicals and fertilizers
        chemical2 = self.env["spp.farm.chemical"].create({"name": "Test Insecticide"})
        fertilizer2 = self.env["spp.fertilizer"].create({"name": "Test NPK"})

        activity = self.env["spp.farm.activity"].create(
            {
                "crop_farm_id": self.farm.id,
                "activity_type": "crop",
                "species_id": self.crop_species.id,
                "season_id": self.season.id,
                "cultivation_water_source": "irrigated",
                "cultivation_production_system": "Greenhouse",
                "cultivation_chemical_interventions": [(6, 0, [self.chemical.id, chemical2.id])],
                "cultivation_fertilizer_interventions": [(6, 0, [self.fertilizer.id, fertilizer2.id])],
            }
        )

        self.assertEqual(activity.cultivation_water_source, "irrigated")
        self.assertEqual(activity.cultivation_production_system, "Greenhouse")
        self.assertEqual(len(activity.cultivation_chemical_interventions), 2)
        self.assertEqual(len(activity.cultivation_fertilizer_interventions), 2)

    def test_11_livestock_activity_comprehensive(self):
        """Test creating livestock activity with all fields"""
        # Create multiple feed items
        feed2 = self.env["spp.feed.items"].create({"name": "Test Hay"})
        feed3 = self.env["spp.feed.items"].create({"name": "Test Grain"})

        activity = self.env["spp.farm.activity"].create(
            {
                "live_farm_id": self.farm.id,
                "activity_type": "livestock",
                "species_id": self.livestock_species.id,
                "season_id": self.season.id,
                "livestock_production_system": "zero grazing",
                "livestock_feed_items": [(6, 0, [self.feed_item.id, feed2.id, feed3.id])],
            }
        )

        self.assertEqual(activity.livestock_production_system, "zero grazing")
        self.assertEqual(len(activity.livestock_feed_items), 3)

    def test_12_aquaculture_activity_comprehensive(self):
        """Test creating aquaculture activity with all fields"""
        activity = self.env["spp.farm.activity"].create(
            {
                "aqua_farm_id": self.farm.id,
                "activity_type": "aquaculture",
                "species_id": self.aqua_species.id,
                "season_id": self.season.id,
                "aquaculture_production_system": "ponds",
                "aquaculture_number_of_fingerlings": 10000,
            }
        )

        self.assertEqual(activity.aquaculture_production_system, "ponds")
        self.assertEqual(activity.aquaculture_number_of_fingerlings, 10000)

    def test_13_multiple_activities_same_farm(self):
        """Test creating multiple activities for the same farm"""
        activity1 = self.env["spp.farm.activity"].create(
            {
                "crop_farm_id": self.farm.id,
                "activity_type": "crop",
                "species_id": self.crop_species.id,
                "season_id": self.season.id,
                "cultivation_water_source": "irrigated",
            }
        )

        activity2 = self.env["spp.farm.activity"].create(
            {
                "live_farm_id": self.farm.id,
                "activity_type": "livestock",
                "species_id": self.livestock_species.id,
                "season_id": self.season.id,
                "livestock_production_system": "free range",
            }
        )

        activity3 = self.env["spp.farm.activity"].create(
            {
                "aqua_farm_id": self.farm.id,
                "activity_type": "aquaculture",
                "species_id": self.aqua_species.id,
                "season_id": self.season.id,
                "aquaculture_production_system": "tanks",
            }
        )

        # All should be created successfully
        self.assertTrue(activity1)
        self.assertTrue(activity2)
        self.assertTrue(activity3)

    def test_14_update_activity_fields(self):
        """Test updating activity fields"""
        activity = self.env["spp.farm.activity"].create(
            {
                "crop_farm_id": self.farm.id,
                "activity_type": "crop",
                "species_id": self.crop_species.id,
                "season_id": self.season.id,
                "cultivation_water_source": "rainfed",
                "cultivation_production_system": "Mono-cropping",
            }
        )

        # Update fields
        activity.write(
            {
                "cultivation_water_source": "irrigated",
                "cultivation_production_system": "Mixed-cropping",
            }
        )

        self.assertEqual(activity.cultivation_water_source, "irrigated")
        self.assertEqual(activity.cultivation_production_system, "Mixed-cropping")

    def test_15_add_remove_chemical_interventions(self):
        """Test adding and removing chemical interventions"""
        activity = self.env["spp.farm.activity"].create(
            {
                "crop_farm_id": self.farm.id,
                "activity_type": "crop",
                "species_id": self.crop_species.id,
                "season_id": self.season.id,
            }
        )

        # Add chemical
        activity.write({"cultivation_chemical_interventions": [(6, 0, [self.chemical.id])]})
        self.assertIn(self.chemical, activity.cultivation_chemical_interventions)

        # Remove chemical
        activity.write({"cultivation_chemical_interventions": [(6, 0, [])]})
        self.assertEqual(len(activity.cultivation_chemical_interventions), 0)

    def test_16_add_remove_feed_items(self):
        """Test adding and removing feed items"""
        activity = self.env["spp.farm.activity"].create(
            {
                "live_farm_id": self.farm.id,
                "activity_type": "livestock",
                "species_id": self.livestock_species.id,
                "season_id": self.season.id,
            }
        )

        # Add feed item
        activity.write({"livestock_feed_items": [(6, 0, [self.feed_item.id])]})
        self.assertIn(self.feed_item, activity.livestock_feed_items)

        # Remove feed item
        activity.write({"livestock_feed_items": [(6, 0, [])]})
        self.assertEqual(len(activity.livestock_feed_items), 0)

    def test_17_search_activities_by_type(self):
        """Test searching activities by type"""
        # Create activities
        self.env["spp.farm.activity"].create(
            {
                "crop_farm_id": self.farm.id,
                "activity_type": "crop",
                "species_id": self.crop_species.id,
                "season_id": self.season.id,
            }
        )
        self.env["spp.farm.activity"].create(
            {
                "live_farm_id": self.farm.id,
                "activity_type": "livestock",
                "species_id": self.livestock_species.id,
                "season_id": self.season.id,
            }
        )

        # Search for crop activities
        crop_activities = self.env["spp.farm.activity"].search([("activity_type", "=", "crop")])
        self.assertGreaterEqual(len(crop_activities), 1)

        # Search for livestock activities
        livestock_activities = self.env["spp.farm.activity"].search([("activity_type", "=", "livestock")])
        self.assertGreaterEqual(len(livestock_activities), 1)

    def test_18_search_activities_by_production_system(self):
        """Test searching activities by production system"""
        self.env["spp.farm.activity"].create(
            {
                "crop_farm_id": self.farm.id,
                "activity_type": "crop",
                "species_id": self.crop_species.id,
                "season_id": self.season.id,
                "cultivation_production_system": "Greenhouse",
            }
        )

        # Search for greenhouse activities
        greenhouse = self.env["spp.farm.activity"].search([("cultivation_production_system", "=", "Greenhouse")])
        self.assertGreaterEqual(len(greenhouse), 1)

    def test_19_activities_with_different_seasons(self):
        """Test activities with different seasons"""
        season2 = self.env["spp.farm.season"].create(
            {
                "name": "Test Season 2025",
                "date_start": datetime.date(2025, 1, 1),
                "date_end": datetime.date(2025, 12, 31),
                "state": "draft",
            }
        )
        season2.action_activate()

        activity1 = self.env["spp.farm.activity"].create(
            {
                "crop_farm_id": self.farm.id,
                "activity_type": "crop",
                "species_id": self.crop_species.id,
                "season_id": self.season.id,
            }
        )

        activity2 = self.env["spp.farm.activity"].create(
            {
                "crop_farm_id": self.farm.id,
                "activity_type": "crop",
                "species_id": self.crop_species.id,
                "season_id": season2.id,
            }
        )

        self.assertEqual(activity1.season_id, self.season)
        self.assertEqual(activity2.season_id, season2)

    def test_20_field_types_verification(self):
        """Test field types are correct"""
        activity = self.env["spp.farm.activity"].create(
            {
                "crop_farm_id": self.farm.id,
                "activity_type": "crop",
                "species_id": self.crop_species.id,
                "season_id": self.season.id,
            }
        )

        # Check field types
        self.assertEqual(activity._fields["cultivation_water_source"].type, "selection")
        self.assertEqual(activity._fields["cultivation_production_system"].type, "selection")
        self.assertEqual(activity._fields["cultivation_chemical_interventions"].type, "many2many")
        self.assertEqual(activity._fields["cultivation_fertilizer_interventions"].type, "many2many")
        self.assertEqual(activity._fields["livestock_production_system"].type, "selection")
        self.assertEqual(activity._fields["livestock_feed_items"].type, "many2many")
        self.assertEqual(activity._fields["aquaculture_production_system"].type, "selection")
        self.assertEqual(activity._fields["aquaculture_number_of_fingerlings"].type, "integer")
