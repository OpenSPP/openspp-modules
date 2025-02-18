from odoo.tests import TransactionCase


class TestSppApiField(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Get model and fields from res.partner to use in tests
        cls.partner_model = cls.env["ir.model"].search([("model", "=", "res.partner")], limit=1)
        cls.partner_name_field = cls.env["ir.model.fields"].search(
            [("model", "=", "res.partner"), ("name", "=", "name")], limit=1
        )

        cls.partner_email_field = cls.env["ir.model.fields"].search(
            [
                ("model", "=", "res.partner"),
                ("name", "=", "email"),
                ("required", "=", False),  # Get a non-required field for testing
            ],
            limit=1,
        )

        # Create namespace for API path
        cls.namespace = cls.env["spp_api.namespace"].create(
            {
                "name": "test_namespace",
                "description": "Test Namespace",
                "version_name": "v1",
            }
        )

    def setUp(self):
        super().setUp()
        # Clean up existing records before each test
        self.env["spp_api.field"].search([]).unlink()
        self.env["spp_api.path"].search([]).unlink()

    def _create_api_path(self, name):
        """Helper method to create a new API path"""
        return self.env["spp_api.path"].create(
            {
                "name": name,
                "namespace_id": self.namespace.id,
                "model_id": self.partner_model.id,
                "method": "get",
                "field_ids": [(6, 0, [self.partner_name_field.id, self.partner_email_field.id])],
            }
        )

    def test_create_api_field(self):
        """Test basic creation of API field"""
        api_path = self._create_api_path("test_path_1")

        field = self.env["spp_api.field"].create(
            {
                "path_id": api_path.id,
                "field_id": self.partner_name_field.id,
                "sequence": 10,
            }
        )

        self.assertEqual(field.model_id, self.partner_model)
        self.assertEqual(field.field_name, "name")

    def test_required_field_sync(self):
        """Test that required status syncs from field_id on change"""
        api_path = self._create_api_path("test_path_2")

        field = self.env["spp_api.field"].create(
            {
                "path_id": api_path.id,
                "field_id": self.partner_name_field.id,
                "sequence": 10,
            }
        )

        self.assertEqual(field.required, field.field_id.required)
        self.assertEqual(field.force_required, field.field_id.required)

    def test_default_value_affects_required(self):
        """Test that setting default_value does not affect required status"""
        api_path = self._create_api_path("test_path_3")

        field = self.env["spp_api.field"].create(
            {
                "path_id": api_path.id,
                "field_id": self.partner_name_field.id,
                "sequence": 10,
                "required": True,
            }
        )

        # Set default value
        field.default_value = "test"
        # Required status should remain True
        self.assertTrue(field.required)

    def test_required_with_default_value(self):
        """Test that field can be required even with default value"""
        api_path = self._create_api_path("test_path_4")

        field = self.env["spp_api.field"].create(
            {
                "path_id": api_path.id,
                "field_id": self.partner_email_field.id,
                "sequence": 10,
                "default_value": "test@example.com",
            }
        )

        # Set required to True
        field.required = True
        # Field can be required even with default value
        self.assertTrue(field.required)

    def test_get_field_name(self):
        """Test the _get_field_name method"""
        api_path = self._create_api_path("test_path_5")

        field = self.env["spp_api.field"].create(
            {
                "path_id": api_path.id,
                "field_id": self.partner_name_field.id,
                "sequence": 10,
            }
        )

        # By default, should return the field_name
        self.assertEqual(field._get_field_name(), field.field_name)
