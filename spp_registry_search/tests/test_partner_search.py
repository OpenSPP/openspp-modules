# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


# Tests for spp_registry_search module

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

        # Get or create search field configurations
        cls.name_field = cls.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "name")], limit=1
        )
        cls.email_field = cls.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "email")], limit=1
        )
        cls.phone_field = cls.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "phone")], limit=1
        )

    def test_01_search_field_configuration(self):
        """Test creating and managing search field configurations"""
        search_field = self.env["spp.partner.search.field"].create(
            {
                "name": "Test Name Field",
                "field_id": self.name_field.id,
                "target_type": "both",
                "sequence": 100,
                "active": True,
            }
        )

        self.assertTrue(search_field.exists())
        self.assertEqual(search_field.field_name, "name")
        self.assertEqual(search_field.field_type, "char")
        self.assertEqual(search_field.target_type, "both")

    def test_02_get_searchable_fields(self):
        """Test retrieving searchable fields"""
        # Create test fields with different target types
        self.env["spp.partner.search.field"].create(
            {
                "name": "Name",
                "field_id": self.name_field.id,
                "target_type": "both",
                "sequence": 10,
                "active": True,
            }
        )
        self.env["spp.partner.search.field"].create(
            {
                "name": "Email",
                "field_id": self.email_field.id,
                "target_type": "individual",
                "sequence": 20,
                "active": True,
            }
        )

        # Test getting all fields
        fields = self.env["res.partner"].get_searchable_fields()
        self.assertIsInstance(fields, list)
        self.assertTrue(len(fields) >= 2)

        # Test getting individual fields only
        individual_fields = self.env["res.partner"].get_searchable_fields("individual")
        self.assertTrue(len(individual_fields) >= 2)  # both + individual

        # Test getting group fields only
        group_fields = self.env["res.partner"].get_searchable_fields("group")
        self.assertTrue(len(group_fields) >= 1)  # only "both" fields

        # Check field structure
        if fields:
            field = fields[0]
            self.assertIn("id", field)
            self.assertIn("name", field)
            self.assertIn("field_name", field)
            self.assertIn("field_type", field)
            self.assertIn("target_type", field)

    def test_03_search_by_name(self):
        """Test searching partners by name"""
        # Create search field configuration
        self.env["spp.partner.search.field"].create(
            {
                "name": "Name",
                "field_id": self.name_field.id,
                "target_type": "both",
                "sequence": 10,
                "active": True,
            }
        )

        # Search for partial name (individuals)
        partner_ids = self.env["res.partner"].search_by_field(
            "name", "Test Partner", is_group=False
        )

        self.assertIn(self.partner_1.id, partner_ids)
        self.assertIn(self.partner_2.id, partner_ids)
        self.assertNotIn(self.partner_3.id, partner_ids)
        self.assertNotIn(self.group_1.id, partner_ids)

        # Search for groups
        group_ids = self.env["res.partner"].search_by_field(
            "name", "Test Group", is_group=True
        )
        self.assertIn(self.group_1.id, group_ids)
        self.assertNotIn(self.partner_1.id, group_ids)

    def test_04_search_by_email(self):
        """Test searching partners by email"""
        # Create search field configuration
        self.env["spp.partner.search.field"].create(
            {
                "name": "Email",
                "field_id": self.email_field.id,
                "target_type": "both",
                "sequence": 20,
                "active": True,
            }
        )

        # Search for specific email (individuals)
        partner_ids = self.env["res.partner"].search_by_field(
            "email", "alpha@test.com", is_group=False
        )

        self.assertIn(self.partner_1.id, partner_ids)
        self.assertNotIn(self.partner_2.id, partner_ids)
        self.assertNotIn(self.partner_3.id, partner_ids)
        self.assertNotIn(self.group_1.id, partner_ids)

    def test_05_search_by_phone(self):
        """Test searching partners by phone"""
        # Create search field configuration
        self.env["spp.partner.search.field"].create(
            {
                "name": "Phone",
                "field_id": self.phone_field.id,
                "target_type": "both",
                "sequence": 30,
                "active": True,
            }
        )

        # Search for specific phone (individuals)
        partner_ids = self.env["res.partner"].search_by_field(
            "phone", "+1234567890", is_group=False
        )

        self.assertIn(self.partner_1.id, partner_ids)
        self.assertNotIn(self.partner_2.id, partner_ids)
        self.assertNotIn(self.group_1.id, partner_ids)

    def test_06_search_empty_value(self):
        """Test searching with empty value"""
        self.env["spp.partner.search.field"].create(
            {
                "name": "Name",
                "field_id": self.name_field.id,
                "target_type": "both",
                "sequence": 10,
                "active": True,
            }
        )

        # Search with empty value should return empty recordset
        results = self.env["res.partner"].search_by_field("name", "")
        self.assertEqual(len(results), 0)

    def test_07_search_nonexistent_field(self):
        """Test searching with non-configured field"""
        # Search with a field that is not configured should return empty recordset
        results = self.env["res.partner"].search_by_field("nonexistent_field", "value")
        self.assertEqual(len(results), 0)

    def test_08_search_inactive_field(self):
        """Test searching with inactive field configuration"""
        # Create inactive search field configuration
        self.env["spp.partner.search.field"].create(
            {
                "name": "Name",
                "field_id": self.name_field.id,
                "target_type": "both",
                "sequence": 10,
                "active": False,
            }
        )

        # Search should not work for inactive field
        results = self.env["res.partner"].search_by_field(
            "name", "Test Partner", is_group=False
        )
        self.assertEqual(len(results), 0)

    def test_09_unique_field_constraint(self):
        """Test unique field per company constraint"""
        # Create first search field
        self.env["spp.partner.search.field"].create(
            {
                "name": "Name",
                "field_id": self.name_field.id,
                "target_type": "both",
                "sequence": 10,
                "active": True,
            }
        )

        # Try to create duplicate - should fail
        with self.assertRaises(Exception):
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
        search_field = self.env["spp.partner.search.field"].create(
            {
                "name": "Test Field",
                "field_id": self.name_field.id,
                "target_type": "both",
                "sequence": 10,
                "active": True,
            }
        )

        name_get_result = search_field.name_get()
        self.assertEqual(len(name_get_result), 1)
        self.assertIn("Test Field", name_get_result[0][1])
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

        # Create search field configuration
        self.env["spp.partner.search.field"].create(
            {
                "name": "Name",
                "field_id": self.name_field.id,
                "target_type": "both",
                "sequence": 10,
                "active": True,
            }
        )

        # Search should not return non-registrant partners
        partner_ids = self.env["res.partner"].search_by_field(
            "name", "Non Registrant", is_group=False
        )
        self.assertNotIn(non_registrant.id, partner_ids)

        # But registrants should be found
        partner_ids = self.env["res.partner"].search_by_field(
            "name", "Test Partner", is_group=False
        )
        self.assertIn(self.partner_1.id, partner_ids)

