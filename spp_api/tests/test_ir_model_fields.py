from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase
from odoo.tools import mute_logger


class TestIrModelFields(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.field_model = cls.env["ir.model.fields"]
        cls.field_alias_model = cls.env["spp_api.field.alias"]

        # Create test namespace
        cls.namespace = cls.env["spp_api.namespace"].create(
            {
                "name": "Test Namespace",
                "version_name": "v1",  # Added required version_name field
            }
        )

        # Get a test model
        cls.test_model = cls.env["ir.model"].search([("model", "=", "res.partner")], limit=1)

        # Get a test model field first
        cls.test_field = cls.field_model.search(
            [
                ("model_id", "=", cls.test_model.id),
                ("ttype", "in", ["char", "text", "integer"]),  # Get a simple field type
            ],
            limit=1,
        )

        # Create a test API path with required fields
        cls.api_path = cls.env["spp_api.path"].create(
            {
                "name": "test_path",
                "namespace_id": cls.namespace.id,
                "model_id": cls.test_model.id,
                "method": "get",  # One of: get, post, put, delete, patch
                "field_ids": [(6, 0, [cls.test_field.id])],  # Add the test field to the API path
            }
        )

    def test_create_api_field_name_alias_without_path(self):
        """Test creating field alias without API path"""
        with self.assertRaises(ValidationError), mute_logger("odoo.models"):
            self.test_field.with_context({}).create_api_field_name_alias()

    def test_create_api_field_name_alias_new(self):
        """Test creating new field alias"""
        context = {"default_api_path_id": self.api_path.id}
        result = self.test_field.with_context(context).create_api_field_name_alias()

        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "spp_api.field.alias")
        self.assertEqual(result["view_mode"], "form")
        self.assertEqual(result["target"], "new")
        self.assertEqual(result["context"]["default_field_id"], self.test_field.id)
        self.assertTrue(result["context"]["scoped_alias"])
        self.assertNotIn("res_id", result)

    def test_create_api_field_name_alias_existing(self):
        """Test creating field alias when one already exists"""
        # Create an existing field alias
        existing_alias = self.field_alias_model.create(
            {
                "field_id": self.test_field.id,
                "api_path_id": self.api_path.id,
                "alias_name": "test_alias",  # Changed from 'name' to 'alias_name'
            }
        )

        context = {"default_api_path_id": self.api_path.id}
        result = self.test_field.with_context(context).create_api_field_name_alias()

        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "spp_api.field.alias")
        self.assertEqual(result["view_mode"], "form")
        self.assertEqual(result["target"], "new")
        self.assertEqual(result["res_id"], existing_alias.id)
