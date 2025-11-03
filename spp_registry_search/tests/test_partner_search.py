# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

_logger = logging.getLogger(__name__)


# Tests for spp_registry_search module


@tagged("post_install", "-at_install")
class TestPartnerSearch(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        # Create test partners (individuals)
        cls.partner_1 = cls.env["res.partner"].create(
            {
                "name": "Test Partner Alpha",
                "email": "alpha@test.com",
                "phone": "+1234567890",
                "mobile": "+9876543210",
                "ref": "REF001",
                "is_registrant": True,
                "is_group": False,
            }
        )

        cls.partner_2 = cls.env["res.partner"].create(
            {
                "name": "Test Partner Beta",
                "email": "beta@test.com",
                "phone": "+1111111111",
                "mobile": "+2222222222",
                "ref": "REF002",
                "is_registrant": True,
                "is_group": False,
            }
        )

        cls.partner_3 = cls.env["res.partner"].create(
            {
                "name": "Another Partner",
                "email": "another@test.com",
                "phone": "+3333333333",
                "ref": "REF003",
                "is_registrant": True,
                "is_group": False,
            }
        )

        # Create test group
        cls.group_1 = cls.env["res.partner"].create(
            {
                "name": "Test Group Alpha",
                "email": "group@test.com",
                "phone": "+5555555555",
                "ref": "GRP001",
                "is_registrant": True,
                "is_group": True,
            }
        )

        # Get existing search field configurations from data files
        # These are created by data/partner_search_field_data.xml
        cls.search_field_name = cls.env.ref("spp_registry_search.registry_search_field_name")
        cls.search_field_email = cls.env.ref("spp_registry_search.registry_search_field_email")
        cls.search_field_phone = cls.env.ref("spp_registry_search.registry_search_field_phone")

        # Get ir.model.fields for testing field creation
        cls.name_field = cls.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "name")], limit=1
        )
        cls.email_field = cls.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "email")], limit=1
        )
        cls.phone_field = cls.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "phone")], limit=1
        )
        cls.mobile_field = cls.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "mobile")], limit=1
        )

    def test_01_search_field_configuration(self):
        """Test creating and managing search field configurations"""
        # Test creating a new search field for mobile (not in default data)
        search_field = self.env["spp.partner.search.field"].create(
            {
                "name": "Mobile",
                "field_id": self.mobile_field.id,
                "target_type": "both",
                "sequence": 40,
                "active": True,
            }
        )

        self.assertTrue(search_field.exists())
        self.assertEqual(search_field.field_name, "mobile")
        self.assertEqual(search_field.field_type, "char")
        self.assertEqual(search_field.target_type, "both")

        # Verify existing search field from data file
        self.assertTrue(self.search_field_name.exists())
        self.assertEqual(self.search_field_name.field_name, "name")
        self.assertEqual(self.search_field_name.field_type, "char")

        # Clean up the mobile field we created
        search_field.unlink()

    def test_02_get_searchable_fields(self):
        """Test retrieving searchable fields"""
        # The default data already has name, email, phone fields with target_type="both"
        # Test getting all fields
        fields = self.env["res.partner"].get_searchable_fields()
        self.assertIsInstance(fields, list)
        self.assertTrue(len(fields) >= 3)  # At least name, email, phone

        # Test getting individual fields only
        individual_fields = self.env["res.partner"].get_searchable_fields("individual")
        self.assertTrue(len(individual_fields) >= 3)  # All "both" fields are included

        # Test getting group fields only
        group_fields = self.env["res.partner"].get_searchable_fields("group")
        self.assertTrue(len(group_fields) >= 3)  # All "both" fields are included

        # Check field structure
        if fields:
            field = fields[0]
            self.assertIn("id", field)
            self.assertIn("name", field)
            self.assertIn("field_name", field)
            self.assertIn("field_type", field)
            self.assertIn("target_type", field)

        # Verify specific fields exist
        field_names = [f["field_name"] for f in fields]
        self.assertIn("name", field_names)
        self.assertIn("email", field_names)
        self.assertIn("phone", field_names)

    def test_03_search_by_name(self):
        """Test searching partners by name"""
        # Name field already exists from data file, no need to create it

        # Search for partial name (individuals)
        partner_ids = self.env["res.partner"].search_by_field("name", "Test Partner", is_group=False)

        self.assertIn(self.partner_1.id, partner_ids)
        self.assertIn(self.partner_2.id, partner_ids)
        self.assertNotIn(self.partner_3.id, partner_ids)
        self.assertNotIn(self.group_1.id, partner_ids)

        # Search for groups
        group_ids = self.env["res.partner"].search_by_field("name", "Test Group", is_group=True)
        self.assertIn(self.group_1.id, group_ids)
        self.assertNotIn(self.partner_1.id, group_ids)

    def test_04_search_by_email(self):
        """Test searching partners by email"""
        # Email field already exists from data file, no need to create it

        # Search for specific email (individuals)
        partner_ids = self.env["res.partner"].search_by_field("email", "alpha@test.com", is_group=False)

        self.assertIn(self.partner_1.id, partner_ids)
        self.assertNotIn(self.partner_2.id, partner_ids)
        self.assertNotIn(self.partner_3.id, partner_ids)
        self.assertNotIn(self.group_1.id, partner_ids)

    def test_05_search_by_phone(self):
        """Test searching partners by phone"""
        # Phone field already exists from data file, no need to create it

        # Search for specific phone (individuals)
        partner_ids = self.env["res.partner"].search_by_field("phone", "+1234567890", is_group=False)

        self.assertIn(self.partner_1.id, partner_ids)
        self.assertNotIn(self.partner_2.id, partner_ids)
        self.assertNotIn(self.group_1.id, partner_ids)

    def test_06_search_empty_value(self):
        """Test searching with empty value"""
        # Name field already exists from data file

        # Search with empty value should return empty recordset
        results = self.env["res.partner"].search_by_field("name", "")
        self.assertEqual(len(results), 0)

    def test_07_search_nonexistent_field(self):
        """Test searching with non-configured field"""
        # Search with a field that is not configured should return empty recordset
        results = self.env["res.partner"].search_by_field("nonexistent_field", "value")
        self.assertEqual(len(results), 0)

    @mute_logger("odoo.sql_db")
    def test_09_unique_field_constraint(self):
        """Test unique field per company constraint"""
        # Name field already exists from data file
        # Try to create duplicate - should fail with IntegrityError
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self.env["spp.partner.search.field"].create(
                {
                    "name": "Name Duplicate",
                    "field_id": self.name_field.id,
                    "target_type": "both",
                    "sequence": 20,
                    "active": True,
                }
            )

    def test_10_name_get(self):
        """Test custom name_get method"""
        # Use existing search field from data file
        name_get_result = self.search_field_name.name_get()
        self.assertEqual(len(name_get_result), 1)
        self.assertIn("Name", name_get_result[0][1])
        self.assertIn("(name)", name_get_result[0][1])

    def test_11_is_registrant_filter(self):
        """Test that is_registrant filter is always applied"""
        # Create a partner that is not a registrant
        non_registrant = self.env["res.partner"].create(
            {
                "name": "Non Registrant Partner",
                "email": "nonreg@test.com",
                "is_registrant": False,
                "is_group": False,
            }
        )

        # Name field already exists from data file

        # Search should not return non-registrant partners
        partner_ids = self.env["res.partner"].search_by_field("name", "Non Registrant", is_group=False)
        self.assertNotIn(non_registrant.id, partner_ids)

        # But registrants should be found
        partner_ids = self.env["res.partner"].search_by_field("name", "Test Partner", is_group=False)
        self.assertIn(self.partner_1.id, partner_ids)
