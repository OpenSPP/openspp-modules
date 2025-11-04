# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from psycopg2 import IntegrityError

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

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

        # Get predefined search field configurations
        cls.search_field_name = cls.env.ref("spp_registry_search.registry_search_field_name")
        cls.search_field_email = cls.env.ref("spp_registry_search.registry_search_field_email")
        cls.search_field_phone = cls.env.ref("spp_registry_search.registry_search_field_phone")

        # Get model fields for reference
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
        """Test predefined search field configuration"""
        # Use predefined name search field
        search_field = self.search_field_name

        self.assertTrue(search_field.exists())
        self.assertEqual(search_field.field_name, "name")
        self.assertEqual(search_field.field_type, "char")
        self.assertEqual(search_field.target_type, "both")
        self.assertTrue(search_field.active)

    def test_02_get_searchable_fields(self):
        """Test retrieving searchable fields"""
        # Predefined fields use "both" target type
        # Temporarily change email field to "individual" for testing
        original_target = self.search_field_email.target_type
        self.search_field_email.write({"target_type": "individual"})

        try:
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
        finally:
            # Restore original target type
            self.search_field_email.write({"target_type": original_target})

    def test_03_search_by_name(self):
        """Test searching partners by name"""
        # Use predefined name search field (already active)
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
        # Use predefined email search field (already active)
        # Search for specific email (individuals)
        partner_ids = self.env["res.partner"].search_by_field("email", "alpha@test.com", is_group=False)

        self.assertIn(self.partner_1.id, partner_ids)
        self.assertNotIn(self.partner_2.id, partner_ids)
        self.assertNotIn(self.partner_3.id, partner_ids)
        self.assertNotIn(self.group_1.id, partner_ids)

    def test_05_search_by_phone(self):
        """Test searching partners by phone"""
        # Use predefined phone search field (already active)
        # Search for specific phone (individuals)
        partner_ids = self.env["res.partner"].search_by_field("phone", "+1234567890", is_group=False)

        self.assertIn(self.partner_1.id, partner_ids)
        self.assertNotIn(self.partner_2.id, partner_ids)
        self.assertNotIn(self.group_1.id, partner_ids)

    def test_06_search_empty_value(self):
        """Test searching with empty value - should return all matching records"""
        # Use predefined name search field (already active)
        # Search with empty value returns all active registrant individuals (search all)
        results = self.env["res.partner"].search_by_field("name", "", is_group=False)
        # Should return all 3 individual registrants (partner_1, partner_2, partner_3)
        self.assertEqual(len(results), 3)
        self.assertIn(self.partner_1.id, results)
        self.assertIn(self.partner_2.id, results)
        self.assertIn(self.partner_3.id, results)

    def test_07_search_nonexistent_field(self):
        """Test searching with non-configured field"""
        # Search with a field that is not configured should return empty recordset
        results = self.env["res.partner"].search_by_field("nonexistent_field", "value")
        self.assertEqual(len(results), 0)

    def test_08_search_inactive_field(self):
        """Test searching with inactive field configuration"""
        # Temporarily deactivate predefined name field
        original_active = self.search_field_name.active
        self.search_field_name.write({"active": False})

        try:
            # Search should not work for inactive field
            results = self.env["res.partner"].search_by_field("name", "Test Partner", is_group=False)
            self.assertEqual(len(results), 0)
        finally:
            # Restore original active state
            self.search_field_name.write({"active": original_active})

    @mute_logger("odoo.sql_db")
    def test_09_unique_field_constraint(self):
        """Test unique field per company constraint"""
        # Predefined name field already exists
        # Try to create duplicate of the same field - should fail with IntegrityError
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
        # Use predefined name search field
        search_field = self.search_field_name

        name_get_result = search_field.name_get()
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

        # Use predefined name search field (already active)
        # Search should not return non-registrant partners
        partner_ids = self.env["res.partner"].search_by_field("name", "Non Registrant", is_group=False)
        self.assertNotIn(non_registrant.id, partner_ids)

        # But registrants should be found
        partner_ids = self.env["res.partner"].search_by_field("name", "Test Partner", is_group=False)
        self.assertIn(self.partner_1.id, partner_ids)

    def test_12_search_by_integer_field(self):
        """Test searching by integer field"""
        # Get an integer field (e.g., color)
        color_field = self.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "color")], limit=1
        )

        # Create search configuration for integer field
        int_search_field = self.env["spp.partner.search.field"].create(
            {
                "name": "Color",
                "field_id": color_field.id,
                "target_type": "both",
                "sequence": 100,
                "active": True,
            }
        )

        # Set color on partner
        self.partner_1.write({"color": 5})

        try:
            # Search by integer value
            partner_ids = self.env["res.partner"].search_by_field("color", "5", is_group=False)
            self.assertIn(self.partner_1.id, partner_ids)

            # Search with invalid integer value
            partner_ids = self.env["res.partner"].search_by_field("color", "invalid", is_group=False)
            self.assertEqual(len(partner_ids), 0)
        finally:
            int_search_field.unlink()

    def test_13_search_by_selection_field(self):
        """Test searching by selection field"""
        # Get a selection field (e.g., type)
        type_field = self.env["ir.model.fields"].search([("model", "=", "res.partner"), ("name", "=", "type")], limit=1)

        if not type_field:
            self.skipTest("Type field not available")

        # Create search configuration for selection field
        sel_search_field = self.env["spp.partner.search.field"].create(
            {
                "name": "Type",
                "field_id": type_field.id,
                "target_type": "both",
                "sequence": 101,
                "active": True,
            }
        )

        # Set type on partner
        self.partner_1.write({"type": "contact"})

        try:
            # Search by selection value
            partner_ids = self.env["res.partner"].search_by_field("type", "contact", is_group=False)
            self.assertIn(self.partner_1.id, partner_ids)
        finally:
            sel_search_field.unlink()

    def test_14_search_by_many2one_field(self):
        """Test searching by many2one field"""
        # Create a country for testing
        test_country = self.env["res.country"].search([("code", "=", "US")], limit=1)
        if not test_country:
            test_country = self.env["res.country"].create({"name": "United States", "code": "US"})

        # Get country_id field
        country_field = self.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "country_id")], limit=1
        )

        # Create search configuration for many2one field
        m2o_search_field = self.env["spp.partner.search.field"].create(
            {
                "name": "Country",
                "field_id": country_field.id,
                "target_type": "both",
                "sequence": 102,
                "active": True,
            }
        )

        # Set country on partner
        self.partner_1.write({"country_id": test_country.id})

        try:
            # Search by ID
            partner_ids = self.env["res.partner"].search_by_field("country_id", str(test_country.id), is_group=False)
            self.assertIn(self.partner_1.id, partner_ids)

            # Search by name (fallback)
            partner_ids = self.env["res.partner"].search_by_field("country_id", "United States", is_group=False)
            self.assertIn(self.partner_1.id, partner_ids)
        finally:
            m2o_search_field.unlink()

    def test_15_search_by_boolean_field(self):
        """Test searching by boolean field"""
        # Get a boolean field (e.g., active)
        active_field = self.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "active")], limit=1
        )

        # Create search configuration for boolean field
        bool_search_field = self.env["spp.partner.search.field"].create(
            {
                "name": "Active",
                "field_id": active_field.id,
                "target_type": "both",
                "sequence": 103,
                "active": True,
            }
        )

        try:
            # Search for active partners (true)
            partner_ids = self.env["res.partner"].search_by_field("active", "true", is_group=False)
            self.assertIn(self.partner_1.id, partner_ids)

            # Search with different boolean representations
            partner_ids = self.env["res.partner"].search_by_field("active", "1", is_group=False)
            self.assertIn(self.partner_1.id, partner_ids)

            partner_ids = self.env["res.partner"].search_by_field("active", "yes", is_group=False)
            self.assertIn(self.partner_1.id, partner_ids)
        finally:
            bool_search_field.unlink()

    def test_16_search_with_filter_domain(self):
        """Test searching with additional filter domain"""
        # Create partners with specific attributes for filtering
        female_partner = self.env["res.partner"].create(
            {
                "name": "Female Partner",
                "email": "female@test.com",
                "is_registrant": True,
                "is_group": False,
            }
        )

        # Add gender field if available
        if "gender" in self.env["res.partner"]._fields:
            female_partner.write({"gender": "Female"})

            # Search with filter domain
            filter_domain = '[["gender", "=", "Female"]]'
            partner_ids = self.env["res.partner"].search_by_field(
                "name", "Partner", is_group=False, filter_domain=filter_domain
            )

            self.assertIn(female_partner.id, partner_ids)

    def test_17_search_with_or_filter_domain(self):
        """Test searching with OR operator in filter domain"""
        # Search with complex domain using OR operator
        filter_domain = '["|", ["email", "=", "alpha@test.com"], ["email", "=", "beta@test.com"]]'
        partner_ids = self.env["res.partner"].search_by_field("name", "", is_group=False, filter_domain=filter_domain)

        self.assertIn(self.partner_1.id, partner_ids)
        self.assertIn(self.partner_2.id, partner_ids)

    def test_18_search_archived_records(self):
        """Test searching archived records with filter domain"""
        # Archive a partner
        self.partner_3.write({"active": False})

        # Search without archived filter - should not find archived
        partner_ids = self.env["res.partner"].search_by_field("name", "Another Partner", is_group=False)
        self.assertNotIn(self.partner_3.id, partner_ids)

        # Search with archived filter - should find archived
        filter_domain = '[["active", "=", false]]'
        partner_ids = self.env["res.partner"].search_by_field(
            "name", "Another Partner", is_group=False, filter_domain=filter_domain
        )
        self.assertIn(self.partner_3.id, partner_ids)

        # Restore partner
        self.partner_3.write({"active": True})

    def test_19_search_with_invalid_filter_domain(self):
        """Test searching with invalid filter domain"""
        # Search with invalid JSON domain - should default to active records
        invalid_domain = "not valid json"
        partner_ids = self.env["res.partner"].search_by_field(
            "name", "Test Partner", is_group=False, filter_domain=invalid_domain
        )

        # Should still return results (with default active filter)
        self.assertIn(self.partner_1.id, partner_ids)

    def test_20_get_searchable_fields_with_selection(self):
        """Test get_searchable_fields includes selection options"""
        # Get a selection field
        type_field = self.env["ir.model.fields"].search([("model", "=", "res.partner"), ("name", "=", "type")], limit=1)

        if not type_field:
            self.skipTest("Type field not available")

        # Create search configuration for selection field
        sel_search_field = self.env["spp.partner.search.field"].create(
            {
                "name": "Type",
                "field_id": type_field.id,
                "target_type": "both",
                "sequence": 200,
                "active": True,
            }
        )

        try:
            # Get searchable fields
            fields = self.env["res.partner"].get_searchable_fields()

            # Find the selection field
            type_field_info = next((f for f in fields if f["field_name"] == "type"), None)
            self.assertIsNotNone(type_field_info)

            # Check that selection options are included
            self.assertIn("selection", type_field_info)
            self.assertIsInstance(type_field_info["selection"], (list, tuple))
        finally:
            sel_search_field.unlink()

    def test_21_get_searchable_fields_with_many2one(self):
        """Test get_searchable_fields includes many2one relation info"""
        # Get country_id field
        country_field = self.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "country_id")], limit=1
        )

        # Create search configuration for many2one field
        m2o_search_field = self.env["spp.partner.search.field"].create(
            {
                "name": "Country",
                "field_id": country_field.id,
                "target_type": "both",
                "sequence": 201,
                "active": True,
            }
        )

        try:
            # Get searchable fields
            fields = self.env["res.partner"].get_searchable_fields()

            # Find the many2one field
            country_field_info = next((f for f in fields if f["field_name"] == "country_id"), None)
            self.assertIsNotNone(country_field_info)

            # Check that relation info is included
            self.assertIn("relation", country_field_info)
            self.assertEqual(country_field_info["relation"], "res.country")
            self.assertIn("relation_field", country_field_info)
        finally:
            m2o_search_field.unlink()

    def test_22_get_searchable_fields_by_type(self):
        """Test get_searchable_fields filtered by partner type"""
        # Get all fields
        all_fields = self.env["res.partner"].get_searchable_fields()
        self.assertTrue(len(all_fields) >= 3)

        # Get individual fields
        individual_fields = self.env["res.partner"].get_searchable_fields("individual")
        self.assertTrue(len(individual_fields) >= 3)

        # Get group fields
        group_fields = self.env["res.partner"].get_searchable_fields("group")
        self.assertTrue(len(group_fields) >= 3)

    def test_23_get_field_options(self):
        """Test get_field_options method"""
        # Get options for res.country
        options = self.env["res.partner"].get_field_options("res.country")

        # Should return list of tuples
        self.assertIsInstance(options, list)
        if options:
            self.assertIsInstance(options[0], tuple)
            self.assertEqual(len(options[0]), 2)  # (id, name)

    def test_24_get_field_options_invalid_model(self):
        """Test get_field_options with invalid model"""
        # Should handle error gracefully
        options = self.env["res.partner"].get_field_options("invalid.model")
        self.assertEqual(options, [])

    def test_25_get_search_filters(self):
        """Test get_search_filters method"""
        # Get all filters
        filters = self.env["res.partner"].get_search_filters()

        # Should return list of dictionaries
        self.assertIsInstance(filters, list)

        # Check filter structure if any exist
        if filters:
            filter_info = filters[0]
            self.assertIn("id", filter_info)
            self.assertIn("name", filter_info)
            self.assertIn("domain", filter_info)
            self.assertIn("description", filter_info)
            self.assertIn("target_type", filter_info)

            # Domain should be valid JSON
            import json

            domain = json.loads(filter_info["domain"])
            self.assertIsInstance(domain, list)

    def test_26_get_search_filters_by_type(self):
        """Test get_search_filters filtered by partner type"""
        # Get all filters
        all_filters = self.env["res.partner"].get_search_filters()

        # Get individual filters
        individual_filters = self.env["res.partner"].get_search_filters("individual")

        # Get group filters
        group_filters = self.env["res.partner"].get_search_filters("group")

        # All should return lists
        self.assertIsInstance(all_filters, list)
        self.assertIsInstance(individual_filters, list)
        self.assertIsInstance(group_filters, list)

    def test_27_search_with_empty_field_name(self):
        """Test search_by_field with empty field name"""
        # Should return empty list
        results = self.env["res.partner"].search_by_field("", "value", is_group=False)
        self.assertEqual(results, [])

    def test_28_search_with_none_field_name(self):
        """Test search_by_field with None field name"""
        # Should return empty list
        results = self.env["res.partner"].search_by_field(None, "value", is_group=False)
        self.assertEqual(results, [])
