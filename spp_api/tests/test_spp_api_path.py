from datetime import datetime

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestSPPAPIPath(TransactionCase):
    def setUp(self):
        super().setUp()
        # Use res.partner model and create test fields
        self.test_model = self.env["ir.model"].search([("model", "=", "res.partner")])

        self.test_char_field = self.env["ir.model.fields"].create(
            {"name": "x_test_char", "field_description": "Test Char", "model_id": self.test_model.id, "ttype": "char"}
        )

        self.test_int_field = self.env["ir.model.fields"].create(
            {
                "name": "x_test_int",
                "field_description": "Test Integer",
                "model_id": self.test_model.id,
                "ttype": "integer",
            }
        )

        # Create test namespace
        self.test_namespace = self.env["spp_api.namespace"].create(
            {"name": "test", "description": "Test Namespace", "version_name": "v1"}
        )

        # Create base API path for testing
        self.api_path = self.env["spp_api.path"].create(
            {
                "name": "test_path",
                "namespace_id": self.test_namespace.id,
                "model_id": self.test_model.id,
                "method": "get",
                "field_ids": [(6, 0, [self.test_char_field.id, self.test_int_field.id])],
            }
        )

    def test_convert_field_type_to_swagger(self):
        """Test conversion of Odoo field types to Swagger types"""
        from ..models.spp_api_path import convert_field_type_to_swagger

        # Test basic types
        self.assertEqual(convert_field_type_to_swagger("char"), ("string", ""))
        self.assertEqual(convert_field_type_to_swagger("integer"), ("integer", ""))
        self.assertEqual(convert_field_type_to_swagger("float"), ("number", "float"))
        self.assertEqual(convert_field_type_to_swagger("datetime"), ("string", "date-time"))

        # Test array types
        self.assertEqual(convert_field_type_to_swagger("many2many"), ("array", ""))
        self.assertEqual(convert_field_type_to_swagger("one2many"), ("array", ""))

        # Test unknown type
        self.assertEqual(convert_field_type_to_swagger("unknown_type"), ("string", ""))

    def test_format_definition_name(self):
        """Test definition name formatting"""
        from ..models.spp_api_path import format_definition_name

        self.assertEqual(format_definition_name("Test Name"), "TestName")
        self.assertEqual(format_definition_name("test name with spaces"), "testnamewithspaces")
        self.assertEqual(format_definition_name(""), "")
        self.assertEqual(format_definition_name(None), "")

    def test_get_domain(self):
        """Test domain generation"""
        # Test basic domain
        kwargs = {"domain": [("x_test_char", "=", "value")]}
        domain = self.api_path.get_domain(kwargs)
        self.assertEqual(domain, [("x_test_char", "=", "value")])

        # Test with from_date
        test_date = datetime.now()
        kwargs = {"from_date": test_date}
        domain = self.api_path.get_domain(kwargs)
        self.assertEqual(domain, [("create_date", ">=", test_date)])

        # Test with last_modified_date
        kwargs = {"last_modified_date": test_date}
        domain = self.api_path.get_domain(kwargs)
        self.assertEqual(domain, [("write_date", ">", test_date)])

    def test_search_treatment_kwargs(self):
        """Test search kwargs treatment"""
        kwargs = {
            "limit": 1000,  # Should be reduced to MAX_LIMIT
            "start_from": 10,  # Should be converted to offset
            "fields": ["x_test_char", "x_test_int", "invalid_field"],
        }

        result = self.api_path.search_treatment_kwargs(kwargs)

        self.assertEqual(result["limit"], 500)  # MAX_LIMIT
        self.assertEqual(result["offset"], 10)
        self.assertEqual(set(result["fields"]), {"x_test_char", "x_test_int"})
        self.assertNotIn("start_from", result)

    def test_get_definition_properties(self):
        """Test generation of Swagger definition properties"""
        properties = self.api_path.get_definition_properties()

        self.assertIn("id", properties)
        self.assertIn("x_test_char", properties)
        self.assertIn("x_test_int", properties)

        self.assertEqual(properties["x_test_char"]["type"], "string")
        self.assertEqual(properties["x_test_int"]["type"], "integer")

    def test_field_validation(self):
        """Test field validation for GET method"""
        # Should raise ValidationError when no fields are specified for GET method
        with self.assertRaises(ValidationError):
            self.env["spp_api.path"].create(
                {
                    "name": "test_path_2",
                    "namespace_id": self.test_namespace.id,
                    "model_id": self.test_model.id,
                    "method": "get",
                    "field_ids": [(6, 0, [])],  # Empty fields
                }
            )

    def test_response_treatment(self):
        """Test response data treatment"""
        test_data = {
            "x_test_char": None,
            "x_test_int": None,
        }

        treated_data = self.api_path._get_response_treatment(test_data)
        self.assertEqual(treated_data[0]["x_test_char"], "")  # Char fields should be empty string
        self.assertIsNone(treated_data[0]["x_test_int"])  # Integer fields should be None

    def test_fields_alias_treatment(self):
        """Test field alias handling"""
        # Create a field alias
        self.env["spp_api.field.alias"].create(
            {"api_path_id": self.api_path.id, "field_id": self.test_char_field.id, "alias_name": "alias_char"}
        )

        post_values = {"alias_char": "test value", "x_test_int": 42}

        result = self.api_path._fields_alias_treatment(post_values)
        self.assertIn("x_test_char", result)
        self.assertEqual(result["x_test_char"], "test value")
        self.assertEqual(result["x_test_int"], 42)
