from odoo.tests import TransactionCase


class TestSppApiFunctionParameter(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create namespace for API path
        cls.namespace = cls.env["spp_api.namespace"].create(
            {
                "name": "test_namespace",
                "description": "Test Namespace",
                "version_name": "v1",
            }
        )

        # Create API path
        cls.api_path = cls.env["spp_api.path"].create(
            {
                "name": "test_path",
                "namespace_id": cls.namespace.id,
                "model_id": cls.env["ir.model"].search([("model", "=", "res.partner")], limit=1).id,
                "method": "get",
                "field_ids": [
                    (
                        6,
                        0,
                        [
                            cls.env["ir.model.fields"]
                            .search([("model", "=", "res.partner"), ("name", "=", "name")], limit=1)
                            .id
                        ],
                    )
                ],
            }
        )

    def setUp(self):
        super().setUp()
        # Clean up existing parameters before each test
        self.env["spp_api.function.parameter"].search([]).unlink()

    def test_create_parameter(self):
        """Test basic creation of function parameter"""
        param = self.env["spp_api.function.parameter"].create(
            {
                "path_id": self.api_path.id,
                "name": "test_param",
                "type": "string",
                "sequence": 1,
            }
        )

        self.assertEqual(param.name, "test_param")
        self.assertEqual(param.type, "string")
        self.assertFalse(param.required)
        self.assertFalse(param.default_value)

    def test_default_value_makes_not_required(self):
        """Test that setting default value makes parameter not required"""
        param = self.env["spp_api.function.parameter"].create(
            {
                "path_id": self.api_path.id,
                "name": "test_param",
                "type": "string",
                "required": True,
            }
        )

        # Initially required
        self.assertTrue(param.required)

        # Set default value - should trigger onchange
        param.write({"default_value": "test_value"})
        param._onchange_default_value()

        # Should now be not required
        self.assertFalse(param.required)

    def test_required_with_default_value(self):
        """Test that parameter cannot be required if it has default value"""
        param = self.env["spp_api.function.parameter"].create(
            {
                "path_id": self.api_path.id,
                "name": "test_param",
                "type": "string",
                "default_value": "test_value",
            }
        )

        # Try to make it required - should trigger onchange
        param.write({"required": True})
        param._onchange_required()

        # Should remain not required due to default value
        self.assertFalse(param.required)

    def test_parameter_types(self):
        """Test creation of parameters with different types"""
        test_types = [
            ("integer", "42"),
            ("float", "3.14"),
            ("boolean", "true"),
            ("string", "test"),
            ("array", '["a", "b"]'),
            ("object", '{"key": "value"}'),
        ]

        for type_name, default_value in test_types:
            param = self.env["spp_api.function.parameter"].create(
                {
                    "path_id": self.api_path.id,
                    "name": f"test_param_{type_name}",
                    "type": type_name,
                    "default_value": default_value,
                }
            )

            self.assertEqual(param.type, type_name)
            self.assertEqual(param.default_value, default_value)

    def test_sequence_ordering(self):
        """Test that parameters are ordered by sequence"""
        # Create parameters with different sequences
        self.env["spp_api.function.parameter"].create(
            {
                "path_id": self.api_path.id,
                "name": "param2",
                "type": "string",
                "sequence": 2,
            }
        )

        self.env["spp_api.function.parameter"].create(
            {
                "path_id": self.api_path.id,
                "name": "param1",
                "type": "string",
                "sequence": 1,
            }
        )

        self.env["spp_api.function.parameter"].create(
            {
                "path_id": self.api_path.id,
                "name": "param3",
                "type": "string",
                "sequence": 3,
            }
        )

        # Get ordered parameters
        params = self.env["spp_api.function.parameter"].search([("path_id", "=", self.api_path.id)], order="sequence")

        # Check order
        self.assertEqual(params[0].name, "param1")
        self.assertEqual(params[1].name, "param2")
        self.assertEqual(params[2].name, "param3")
