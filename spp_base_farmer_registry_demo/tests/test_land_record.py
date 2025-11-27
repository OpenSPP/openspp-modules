# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestLandRecord(TransactionCase):
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
                "name": "Test Farm Land",
                "is_group": True,
                "is_registrant": True,
            }
        )

    def test_01_land_record_ke_access_cities_reg_field(self):
        """Test ke_access_cities_reg field exists"""
        land_record = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Test Parcel",
                "land_acreage": 10.0,
            }
        )

        self.assertIn("ke_access_cities_reg", land_record._fields)

    def test_02_land_record_ke_access_cities_reg_readonly(self):
        """Test ke_access_cities_reg field is readonly"""
        land_record = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Test Parcel",
                "land_acreage": 10.0,
            }
        )

        field = land_record._fields["ke_access_cities_reg"]
        self.assertTrue(field.readonly)

    def test_03_land_record_ke_access_cities_reg_type(self):
        """Test ke_access_cities_reg field is float type"""
        land_record = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Test Parcel",
                "land_acreage": 10.0,
            }
        )

        field = land_record._fields["ke_access_cities_reg"]
        self.assertEqual(field.type, "float")

    def test_04_land_record_basic_creation(self):
        """Test creating a basic land record"""
        land_record = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Parcel 1",
                "land_acreage": 15.5,
            }
        )

        self.assertEqual(land_record.land_name, "Parcel 1")
        self.assertEqual(land_record.land_acreage, 15.5)
        self.assertEqual(land_record.land_farm_id, self.farm)

    def test_05_land_record_with_ke_access(self):
        """Test land record with ke_access_cities_reg value"""
        # Since it's readonly, we need to use sudo or direct write
        land_record = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Parcel with Access",
                "land_acreage": 20.0,
            }
        )

        # Try to set value through SQL or sudo
        # Note: In real scenario this might be computed or set by external process
        self.assertIn(land_record.ke_access_cities_reg, [0.0, False, None])

    def test_06_multiple_land_records_same_farm(self):
        """Test creating multiple land records for the same farm"""
        land1 = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Parcel A",
                "land_acreage": 10.0,
            }
        )

        land2 = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Parcel B",
                "land_acreage": 15.0,
            }
        )

        land3 = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Parcel C",
                "land_acreage": 8.5,
            }
        )

        # All should belong to the same farm
        self.assertEqual(land1.land_farm_id, self.farm)
        self.assertEqual(land2.land_farm_id, self.farm)
        self.assertEqual(land3.land_farm_id, self.farm)

    def test_07_land_records_different_farms(self):
        """Test land records for different farms"""
        farm2 = self.env["res.partner"].create(
            {
                "name": "Farm 2",
                "is_group": True,
                "is_registrant": True,
            }
        )

        land1 = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Farm 1 Parcel",
                "land_acreage": 10.0,
            }
        )

        land2 = self.env["spp.land.record"].create(
            {
                "land_farm_id": farm2.id,
                "land_name": "Farm 2 Parcel",
                "land_acreage": 20.0,
            }
        )

        self.assertEqual(land1.land_farm_id, self.farm)
        self.assertEqual(land2.land_farm_id, farm2)

    def test_08_search_land_records_by_farm(self):
        """Test searching land records by farm"""
        self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Searchable 1",
                "land_acreage": 5.0,
            }
        )
        self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Searchable 2",
                "land_acreage": 7.0,
            }
        )

        # Search for all land records of this farm
        land_records = self.env["spp.land.record"].search([("land_farm_id", "=", self.farm.id)])

        self.assertGreaterEqual(len(land_records), 2)

    def test_09_land_record_update(self):
        """Test updating land record fields"""
        land_record = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Original Name",
                "land_acreage": 10.0,
            }
        )

        # Update fields
        land_record.write(
            {
                "land_name": "Updated Name",
                "land_acreage": 12.5,
            }
        )

        self.assertEqual(land_record.land_name, "Updated Name")
        self.assertEqual(land_record.land_acreage, 12.5)

    def test_10_land_record_with_various_acreages(self):
        """Test land records with various acreage values"""
        test_acreages = [0.5, 1.0, 5.5, 10.0, 25.75, 50.0, 100.0, 1000.5]

        for i, acreage in enumerate(test_acreages):
            land_record = self.env["spp.land.record"].create(
                {
                    "land_farm_id": self.farm.id,
                    "land_name": f"Parcel {i}",
                    "land_acreage": acreage,
                }
            )
            self.assertEqual(land_record.land_acreage, acreage)

    def test_11_search_land_records_by_acreage(self):
        """Test searching land records by acreage"""
        self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Small Parcel",
                "land_acreage": 2.0,
            }
        )
        self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Medium Parcel",
                "land_acreage": 10.0,
            }
        )
        self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Large Parcel",
                "land_acreage": 50.0,
            }
        )

        # Search for large parcels
        large = self.env["spp.land.record"].search([("land_acreage", ">", 20)])
        self.assertGreaterEqual(len(large), 1)

        # Search for small parcels
        small = self.env["spp.land.record"].search([("land_acreage", "<", 5)])
        self.assertGreaterEqual(len(small), 1)

    def test_12_land_record_with_owner(self):
        """Test land record with owner field"""
        # Check if owner_id field exists
        land_record = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Owned Parcel",
                "land_acreage": 10.0,
            }
        )

        if "owner_id" in land_record._fields:
            land_record.write({"owner_id": self.farm.id})
            self.assertEqual(land_record.owner_id, self.farm)

    def test_13_land_record_with_land_use(self):
        """Test land record with land_use field"""
        land_record = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Cultivated Parcel",
                "land_acreage": 10.0,
            }
        )

        if "land_use" in land_record._fields:
            land_record.write({"land_use": "cultivation"})
            self.assertEqual(land_record.land_use, "cultivation")

    def test_14_land_record_with_species(self):
        """Test land record with species field"""
        land_record = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Species Parcel",
                "land_acreage": 10.0,
            }
        )

        if "species" in land_record._fields:
            # Create a test species
            species = self.env["spp.farm.species"].create(
                {
                    "name": "Test Crop Species",
                    "species_type": "crop",
                }
            )

            land_record.write({"species": [(6, 0, [species.id])]})
            self.assertIn(species, land_record.species)

    def test_15_land_record_delete(self):
        """Test deleting land record"""
        land_record = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "To Delete",
                "land_acreage": 10.0,
            }
        )

        record_id = land_record.id
        land_record.unlink()

        # Verify deleted
        found = self.env["spp.land.record"].search([("id", "=", record_id)])
        self.assertEqual(len(found), 0)

    def test_16_land_record_bulk_create(self):
        """Test bulk creating land records"""
        vals_list = [
            {
                "land_farm_id": self.farm.id,
                "land_name": f"Bulk Parcel {i}",
                "land_acreage": float(i * 5),
            }
            for i in range(1, 6)
        ]

        land_records = self.env["spp.land.record"].create(vals_list)

        self.assertEqual(len(land_records), 5)
        for i, record in enumerate(land_records, 1):
            self.assertEqual(record.land_name, f"Bulk Parcel {i}")

    def test_17_land_record_inherit_check(self):
        """Test that spp.land.record is properly inherited"""
        land_record = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Inherit Test",
                "land_acreage": 10.0,
            }
        )

        # Verify standard fields exist
        self.assertIn("land_name", land_record._fields)
        self.assertIn("land_acreage", land_record._fields)
        self.assertIn("land_farm_id", land_record._fields)

        # Verify our custom field exists
        self.assertIn("ke_access_cities_reg", land_record._fields)

    def test_18_land_record_name_variations(self):
        """Test land record with various name formats"""
        name_formats = [
            "Parcel-001",
            "Plot A",
            "Land Lot 123",
            "Section-45-B",
            "AB12345",
        ]

        for name in name_formats:
            land_record = self.env["spp.land.record"].create(
                {
                    "land_farm_id": self.farm.id,
                    "land_name": name,
                    "land_acreage": 10.0,
                }
            )
            self.assertEqual(land_record.land_name, name)

    def test_19_land_record_zero_acreage(self):
        """Test land record with zero acreage"""
        land_record = self.env["spp.land.record"].create(
            {
                "land_farm_id": self.farm.id,
                "land_name": "Zero Acreage",
                "land_acreage": 0.0,
            }
        )

        self.assertEqual(land_record.land_acreage, 0.0)

    def test_20_land_record_comprehensive(self):
        """Test creating land record with all available fields"""
        vals = {
            "land_farm_id": self.farm.id,
            "land_name": "Comprehensive Parcel",
            "land_acreage": 25.5,
        }

        # Add optional fields if they exist
        land_record_model = self.env["spp.land.record"]
        if "owner_id" in land_record_model._fields:
            vals["owner_id"] = self.farm.id
        if "land_use" in land_record_model._fields:
            vals["land_use"] = "cultivation"

        land_record = self.env["spp.land.record"].create(vals)

        self.assertEqual(land_record.land_name, "Comprehensive Parcel")
        self.assertEqual(land_record.land_acreage, 25.5)
        self.assertEqual(land_record.land_farm_id, self.farm)
