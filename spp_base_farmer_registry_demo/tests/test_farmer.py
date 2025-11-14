# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestFarmer(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

    def test_01_farmer_marital_status_fields(self):
        """Test farmer marital status field extensions"""
        partner = self.env["res.partner"].create(
            {
                "name": "Test Farmer Partner",
                "is_registrant": True,
            }
        )

        # Test that marital_status field exists and has the extended selections
        self.assertIn("marital_status", partner._fields)

        # Test setting married_monogamous
        partner.write({"marital_status": "married_monogamous"})
        self.assertEqual(partner.marital_status, "married_monogamous")

        # Test setting married_polygamous
        partner.write({"marital_status": "married_polygamous"})
        self.assertEqual(partner.marital_status, "married_polygamous")

    def test_02_farmer_education_level_fields(self):
        """Test farmer education level field extensions"""
        partner = self.env["res.partner"].create(
            {
                "name": "Test Farmer Education",
                "is_registrant": True,
            }
        )

        # Test that highest_education_level field exists
        self.assertIn("highest_education_level", partner._fields)

        # Test setting various education levels
        education_levels = ["none", "primary", "secondary", "certificate", "diploma", "university", "tertiary"]

        for level in education_levels:
            partner.write({"highest_education_level": level})
            self.assertEqual(partner.highest_education_level, level)

    def test_03_farmer_marital_status_filter(self):
        """Test that marital_status field allows filtering"""
        partner = self.env["res.partner"].create(
            {
                "name": "Test Farmer Filter",
                "is_registrant": True,
                "marital_status": "married_monogamous",
            }
        )

        # Test filtering
        found = self.env["res.partner"].search([("marital_status", "=", "married_monogamous")])
        self.assertIn(partner, found)

    def test_04_farmer_education_level_filter(self):
        """Test that highest_education_level field allows filtering"""
        partner = self.env["res.partner"].create(
            {
                "name": "Test Education Filter",
                "is_registrant": True,
                "highest_education_level": "university",
            }
        )

        # Test filtering
        found = self.env["res.partner"].search([("highest_education_level", "=", "university")])
        self.assertIn(partner, found)

    def test_05_spp_farmer_marital_status(self):
        """Test spp.farmer model marital status extensions"""
        # Check if spp.farmer model exists (temp farmer)
        if "spp.farmer" not in self.env:
            self.skipTest("spp.farmer model not available")

        # Create a farmer record
        farmer = self.env["spp.farmer"].create(
            {
                "farmer_given_name": "Test",
                "farmer_family_name": "Farmer",
            }
        )

        # Test that farmer_marital_status field exists and has extended selections
        self.assertIn("farmer_marital_status", farmer._fields)

        # Test setting values
        farmer.write({"farmer_marital_status": "married_monogamous"})
        self.assertEqual(farmer.farmer_marital_status, "married_monogamous")

    def test_06_spp_farmer_education_level(self):
        """Test spp.farmer model education level extensions"""
        # Check if spp.farmer model exists
        if "spp.farmer" not in self.env:
            self.skipTest("spp.farmer model not available")

        # Create a farmer record
        farmer = self.env["spp.farmer"].create(
            {
                "farmer_given_name": "Test",
                "farmer_family_name": "Farmer",
            }
        )

        # Test that farmer_highest_education_level field exists
        self.assertIn("farmer_highest_education_level", farmer._fields)

        # Test setting various education levels
        education_levels = ["none", "primary", "secondary", "certificate", "diploma", "university", "tertiary"]

        for level in education_levels:
            farmer.write({"farmer_highest_education_level": level})
            self.assertEqual(farmer.farmer_highest_education_level, level)

    def test_07_multiple_farmers_with_different_status(self):
        """Test multiple farmers with different marital statuses"""
        farmer1 = self.env["res.partner"].create(
            {
                "name": "Monogamous Farmer",
                "is_registrant": True,
                "marital_status": "married_monogamous",
            }
        )

        farmer2 = self.env["res.partner"].create(
            {
                "name": "Polygamous Farmer",
                "is_registrant": True,
                "marital_status": "married_polygamous",
            }
        )

        farmer3 = self.env["res.partner"].create(
            {
                "name": "Single Farmer",
                "is_registrant": True,
                "marital_status": "single",
            }
        )

        # Verify each farmer has correct status
        self.assertEqual(farmer1.marital_status, "married_monogamous")
        self.assertEqual(farmer2.marital_status, "married_polygamous")
        self.assertEqual(farmer3.marital_status, "single")

    def test_08_multiple_farmers_with_different_education(self):
        """Test multiple farmers with different education levels"""
        farmers = []
        education_levels = ["none", "primary", "secondary", "university"]

        for i, level in enumerate(education_levels):
            farmer = self.env["res.partner"].create(
                {
                    "name": f"Farmer {i}",
                    "is_registrant": True,
                    "highest_education_level": level,
                }
            )
            farmers.append(farmer)

        # Verify each farmer has correct education level
        for i, level in enumerate(education_levels):
            self.assertEqual(farmers[i].highest_education_level, level)

    def test_09_search_farmers_by_marital_status(self):
        """Test searching farmers by marital status"""
        # Create farmers with different statuses
        self.env["res.partner"].create(
            {
                "name": "Monogamous 1",
                "is_registrant": True,
                "marital_status": "married_monogamous",
            }
        )
        self.env["res.partner"].create(
            {
                "name": "Monogamous 2",
                "is_registrant": True,
                "marital_status": "married_monogamous",
            }
        )
        self.env["res.partner"].create(
            {
                "name": "Polygamous 1",
                "is_registrant": True,
                "marital_status": "married_polygamous",
            }
        )

        # Search for monogamous farmers
        monogamous = self.env["res.partner"].search([("marital_status", "=", "married_monogamous")])
        self.assertGreaterEqual(len(monogamous), 2)

        # Search for polygamous farmers
        polygamous = self.env["res.partner"].search([("marital_status", "=", "married_polygamous")])
        self.assertGreaterEqual(len(polygamous), 1)

    def test_10_search_farmers_by_education_level(self):
        """Test searching farmers by education level"""
        # Create farmers with different education levels
        self.env["res.partner"].create(
            {
                "name": "University Farmer 1",
                "is_registrant": True,
                "highest_education_level": "university",
            }
        )
        self.env["res.partner"].create(
            {
                "name": "University Farmer 2",
                "is_registrant": True,
                "highest_education_level": "university",
            }
        )
        self.env["res.partner"].create(
            {
                "name": "Primary Farmer",
                "is_registrant": True,
                "highest_education_level": "primary",
            }
        )

        # Search for university educated farmers
        university = self.env["res.partner"].search([("highest_education_level", "=", "university")])
        self.assertGreaterEqual(len(university), 2)

        # Search for primary educated farmers
        primary = self.env["res.partner"].search([("highest_education_level", "=", "primary")])
        self.assertGreaterEqual(len(primary), 1)

    def test_11_farmer_field_update(self):
        """Test updating farmer fields"""
        farmer = self.env["res.partner"].create(
            {
                "name": "Updateable Farmer",
                "is_registrant": True,
                "marital_status": "single",
                "highest_education_level": "none",
            }
        )

        # Update fields
        farmer.write(
            {
                "marital_status": "married_monogamous",
                "highest_education_level": "university",
            }
        )

        self.assertEqual(farmer.marital_status, "married_monogamous")
        self.assertEqual(farmer.highest_education_level, "university")

    def test_12_farmer_without_marital_status(self):
        """Test farmer without marital status set"""
        farmer = self.env["res.partner"].create(
            {
                "name": "No Status Farmer",
                "is_registrant": True,
            }
        )

        # marital_status can be False
        self.assertIn(farmer.marital_status, [False, None, ""])

    def test_13_farmer_without_education_level(self):
        """Test farmer without education level set"""
        farmer = self.env["res.partner"].create(
            {
                "name": "No Education Farmer",
                "is_registrant": True,
            }
        )

        # highest_education_level can be False
        self.assertIn(farmer.highest_education_level, [False, None, ""])

    def test_14_inherit_model_check(self):
        """Test that res.partner is properly inherited"""
        farmer = self.env["res.partner"].create(
            {
                "name": "Inherit Test Farmer",
                "is_registrant": True,
            }
        )

        # Verify standard partner fields still exist
        self.assertIn("name", farmer._fields)
        self.assertIn("email", farmer._fields)
        self.assertIn("is_registrant", farmer._fields)

        # Verify our extended fields are there
        self.assertIn("marital_status", farmer._fields)
        self.assertIn("highest_education_level", farmer._fields)
