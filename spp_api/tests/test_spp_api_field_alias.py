from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestSppApiFieldAlias(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Get a field from res.partner to use in tests
        cls.partner_model = cls.env["ir.model"].search([("model", "=", "res.partner")], limit=1)
        cls.partner_name_field = cls.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "name")], limit=1
        )

        cls.partner_email_field = cls.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "email")], limit=1
        )

        # Create namespace for API path
        cls.namespace = cls.env["spp_api.namespace"].create(
            {
                "name": "test_namespace",
                "description": "Test Namespace",
                "version_name": "v1",  # Required field
            }
        )

        # Create an API path for testing with all required fields
        cls.api_path = cls.env["spp_api.path"].create(
            {
                "name": "test_path",
                "namespace_id": cls.namespace.id,
                "model_id": cls.partner_model.id,
                "method": "get",  # One of: get, post, put, delete, patch
                "field_ids": [(6, 0, [cls.partner_name_field.id, cls.partner_email_field.id])],  # Required fields list
            }
        )

    def setUp(self):
        super().setUp()
        # Clean up existing field aliases before each test
        self.env["spp_api.field.alias"].search([]).unlink()

    def _create_api_path(self, name):
        """Helper method to create a new API path"""
        # Clean up existing path with same name if exists
        existing_path = self.env["spp_api.path"].search([("name", "=", name)])
        if existing_path:
            existing_path.unlink()

        return self.env["spp_api.path"].create(
            {
                "name": name,
                "namespace_id": self.namespace.id,
                "model_id": self.partner_model.id,
                "method": "get",
                "field_ids": [(6, 0, [self.partner_name_field.id, self.partner_email_field.id])],
            }
        )

    def test_create_field_alias(self):
        """Test basic creation of field alias"""
        api_path = self._create_api_path("test_path_1")
        alias = self.env["spp_api.field.alias"].create(
            {
                "field_id": self.partner_name_field.id,
                "alias_name": "full_name",
                "api_path_id": api_path.id,
            }
        )
        self.assertEqual(alias.model_id, self.partner_name_field.model_id)
        self.assertEqual(alias.display_name, f"full_name - {self.partner_name_field.name}")

    def test_same_name_constraint(self):
        """Test constraint preventing alias name same as field name"""
        api_path = self._create_api_path("test_path_2")
        with self.assertRaises(ValidationError):
            self.env["spp_api.field.alias"].create(
                {
                    "field_id": self.partner_name_field.id,
                    "alias_name": "name",  # Same as field name
                    "api_path_id": api_path.id,
                }
            )

    def test_global_alias(self):
        """Test global alias functionality"""
        api_path = self._create_api_path("test_path_5")
        alias = self.env["spp_api.field.alias"].create(
            {
                "field_id": self.partner_name_field.id,
                "alias_name": "full_name",
                "api_path_id": api_path.id,
            }
        )

        # Setting global_alias should clear api_path_id
        alias.global_alias = True
        self.assertFalse(alias.api_path_id)

    def test_global_alias_duplicate(self):
        """Test constraint preventing duplicate global aliases for same field"""
        self.env["spp_api.field.alias"].create(
            {
                "field_id": self.partner_name_field.id,
                "alias_name": "full_name",
                "global_alias": True,
            }
        )

        with self.assertRaises(ValidationError):
            self.env["spp_api.field.alias"].create(
                {
                    "field_id": self.partner_name_field.id,
                    "alias_name": "another_name",
                    "global_alias": True,
                }
            )
