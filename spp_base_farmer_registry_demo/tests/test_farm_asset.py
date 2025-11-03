# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestFarmAsset(TransactionCase):
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
                "name": "Test Farm Asset",
                "is_group": True,
                "is_registrant": True,
            }
        )

    def test_01_farm_asset_aquaculture_active_fields(self):
        """Test aquaculture active fields"""
        farm_asset = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_active": 5,
                "active_area": 100.5,
                "active_volume": 500.75,
            }
        )

        self.assertEqual(farm_asset.number_active, 5)
        self.assertEqual(farm_asset.active_area, 100.5)
        self.assertEqual(farm_asset.active_volume, 500.75)

    def test_02_farm_asset_aquaculture_inactive_fields(self):
        """Test aquaculture inactive fields"""
        farm_asset = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_inactive": 3,
                "inactive_area": 50.25,
                "inactive_volume": 250.5,
            }
        )

        self.assertEqual(farm_asset.number_inactive, 3)
        self.assertEqual(farm_asset.inactive_area, 50.25)
        self.assertEqual(farm_asset.inactive_volume, 250.5)

    def test_03_farm_asset_all_aquaculture_fields(self):
        """Test all aquaculture fields together"""
        farm_asset = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_active": 10,
                "active_area": 200.0,
                "active_volume": 1000.0,
                "number_inactive": 5,
                "inactive_area": 100.0,
                "inactive_volume": 500.0,
            }
        )

        # Verify active fields
        self.assertEqual(farm_asset.number_active, 10)
        self.assertEqual(farm_asset.active_area, 200.0)
        self.assertEqual(farm_asset.active_volume, 1000.0)

        # Verify inactive fields
        self.assertEqual(farm_asset.number_inactive, 5)
        self.assertEqual(farm_asset.inactive_area, 100.0)
        self.assertEqual(farm_asset.inactive_volume, 500.0)

    def test_04_farm_asset_field_types(self):
        """Test farm asset field types"""
        farm_asset = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
            }
        )

        # Check field types
        self.assertEqual(farm_asset._fields["number_active"].type, "integer")
        self.assertEqual(farm_asset._fields["active_area"].type, "float")
        self.assertEqual(farm_asset._fields["active_volume"].type, "float")
        self.assertEqual(farm_asset._fields["number_inactive"].type, "integer")
        self.assertEqual(farm_asset._fields["inactive_area"].type, "float")
        self.assertEqual(farm_asset._fields["inactive_volume"].type, "float")

    def test_05_farm_asset_default_values(self):
        """Test farm asset default values"""
        farm_asset = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
            }
        )

        # Default values should be 0 or False
        self.assertIn(farm_asset.number_active, [0, False])
        self.assertIn(farm_asset.active_area, [0.0, False])
        self.assertIn(farm_asset.active_volume, [0.0, False])
        self.assertIn(farm_asset.number_inactive, [0, False])
        self.assertIn(farm_asset.inactive_area, [0.0, False])
        self.assertIn(farm_asset.inactive_volume, [0.0, False])

    def test_06_farm_asset_update_fields(self):
        """Test updating farm asset fields"""
        farm_asset = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_active": 5,
                "active_area": 100.0,
            }
        )

        # Update fields
        farm_asset.write(
            {
                "number_active": 10,
                "active_area": 200.0,
            }
        )

        self.assertEqual(farm_asset.number_active, 10)
        self.assertEqual(farm_asset.active_area, 200.0)

    def test_07_farm_asset_zero_values(self):
        """Test farm asset with zero values"""
        farm_asset = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_active": 0,
                "active_area": 0.0,
                "active_volume": 0.0,
                "number_inactive": 0,
                "inactive_area": 0.0,
                "inactive_volume": 0.0,
            }
        )

        self.assertEqual(farm_asset.number_active, 0)
        self.assertEqual(farm_asset.active_area, 0.0)
        self.assertEqual(farm_asset.active_volume, 0.0)

    def test_08_farm_asset_large_values(self):
        """Test farm asset with large values"""
        farm_asset = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_active": 1000,
                "active_area": 10000.5,
                "active_volume": 50000.75,
            }
        )

        self.assertEqual(farm_asset.number_active, 1000)
        self.assertEqual(farm_asset.active_area, 10000.5)
        self.assertEqual(farm_asset.active_volume, 50000.75)

    def test_09_farm_asset_decimal_precision(self):
        """Test farm asset with decimal precision"""
        farm_asset = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "active_area": 123.456789,
                "active_volume": 987.654321,
            }
        )

        # Should preserve decimal values
        self.assertAlmostEqual(farm_asset.active_area, 123.456789, places=5)
        self.assertAlmostEqual(farm_asset.active_volume, 987.654321, places=5)

    def test_10_multiple_farm_assets_same_farm(self):
        """Test multiple farm assets for the same farm"""
        asset1 = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_active": 5,
                "active_area": 100.0,
            }
        )

        asset2 = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_active": 10,
                "active_area": 200.0,
            }
        )

        # Both should belong to the same farm
        self.assertEqual(asset1.asset_farm_id, self.farm)
        self.assertEqual(asset2.asset_farm_id, self.farm)

    def test_11_farm_assets_different_farms(self):
        """Test farm assets for different farms"""
        farm2 = self.env["res.partner"].create(
            {
                "name": "Farm 2",
                "is_group": True,
                "is_registrant": True,
            }
        )

        asset1 = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_active": 5,
            }
        )

        asset2 = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": farm2.id,
                "number_active": 10,
            }
        )

        self.assertEqual(asset1.asset_farm_id, self.farm)
        self.assertEqual(asset2.asset_farm_id, farm2)

    def test_12_search_farm_assets_by_farm(self):
        """Test searching farm assets by farm"""
        self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_active": 5,
            }
        )
        self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_active": 10,
            }
        )

        # Search for all assets of this farm
        assets = self.env["spp.farm.asset"].search([("asset_farm_id", "=", self.farm.id)])

        self.assertGreaterEqual(len(assets), 2)

    def test_13_search_farm_assets_by_number_active(self):
        """Test searching farm assets by number active"""
        self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_active": 5,
            }
        )
        self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_active": 15,
            }
        )

        # Search for assets with more than 10 active
        large = self.env["spp.farm.asset"].search([("number_active", ">", 10)])
        self.assertGreaterEqual(len(large), 1)

    def test_14_farm_asset_with_asset_type(self):
        """Test farm asset with asset_type field (if exists)"""
        farm_asset = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_active": 5,
            }
        )

        # Check if asset_type field exists (from parent model)
        if "asset_type" in farm_asset._fields:
            self.assertIn("asset_type", farm_asset._fields)

    def test_15_farm_asset_with_machinery_fields(self):
        """Test farm asset with machinery fields (if exists)"""
        farm_asset = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_active": 5,
            }
        )

        # Check if machinery_farm_id field exists
        if "machinery_farm_id" in farm_asset._fields:
            farm_asset2 = self.env["spp.farm.asset"].create(
                {
                    "machinery_farm_id": self.farm.id,
                    "number_active": 3,
                }
            )
            self.assertEqual(farm_asset2.machinery_farm_id, self.farm)

    def test_16_farm_asset_bulk_create(self):
        """Test bulk creating farm assets"""
        vals_list = [
            {
                "asset_farm_id": self.farm.id,
                "number_active": i,
                "active_area": float(i * 10),
            }
            for i in range(1, 6)
        ]

        assets = self.env["spp.farm.asset"].create(vals_list)

        self.assertEqual(len(assets), 5)
        for i, asset in enumerate(assets, 1):
            self.assertEqual(asset.number_active, i)

    def test_17_farm_asset_delete(self):
        """Test deleting farm asset"""
        farm_asset = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_active": 5,
            }
        )

        asset_id = farm_asset.id
        farm_asset.unlink()

        # Verify deleted
        found = self.env["spp.farm.asset"].search([("id", "=", asset_id)])
        self.assertEqual(len(found), 0)

    def test_18_farm_asset_inherit_check(self):
        """Test that spp.farm.asset is properly inherited"""
        farm_asset = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
            }
        )

        # Verify our custom fields exist
        custom_fields = [
            "number_active",
            "active_area",
            "active_volume",
            "number_inactive",
            "inactive_area",
            "inactive_volume",
        ]

        for field in custom_fields:
            self.assertIn(field, farm_asset._fields)

    def test_19_farm_asset_active_vs_inactive(self):
        """Test comparing active vs inactive values"""
        farm_asset = self.env["spp.farm.asset"].create(
            {
                "asset_farm_id": self.farm.id,
                "number_active": 10,
                "active_area": 200.0,
                "active_volume": 1000.0,
                "number_inactive": 5,
                "inactive_area": 100.0,
                "inactive_volume": 500.0,
            }
        )

        # Active should be greater than inactive
        self.assertGreater(farm_asset.number_active, farm_asset.number_inactive)
        self.assertGreater(farm_asset.active_area, farm_asset.inactive_area)
        self.assertGreater(farm_asset.active_volume, farm_asset.inactive_volume)

    def test_20_farm_asset_comprehensive(self):
        """Test creating comprehensive farm asset with all fields"""
        vals = {
            "asset_farm_id": self.farm.id,
            "number_active": 15,
            "active_area": 300.5,
            "active_volume": 1500.75,
            "number_inactive": 8,
            "inactive_area": 150.25,
            "inactive_volume": 750.5,
        }

        # Add optional fields if they exist
        if "quantity" in self.env["spp.farm.asset"]._fields:
            vals["quantity"] = 5

        farm_asset = self.env["spp.farm.asset"].create(vals)

        # Verify all fields
        self.assertEqual(farm_asset.number_active, 15)
        self.assertEqual(farm_asset.active_area, 300.5)
        self.assertEqual(farm_asset.active_volume, 1500.75)
        self.assertEqual(farm_asset.number_inactive, 8)
        self.assertEqual(farm_asset.inactive_area, 150.25)
        self.assertEqual(farm_asset.inactive_volume, 750.5)
