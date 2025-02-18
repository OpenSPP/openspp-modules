import uuid

from odoo.tests.common import TransactionCase


class TestNamespace(TransactionCase):
    def setUp(self):
        super().setUp()
        self.namespace = self.env["spp_api.namespace"].create(
            {
                "name": "Test API Namespace",
                "version_name": "v1",
                "description": "Test Description",
            }
        )

    def test_create_namespace(self):
        """Test namespace creation and name formatting"""
        self.assertEqual(self.namespace.name, "test+api+namespace")
        self.assertEqual(self.namespace.version_name, "v1")
        self.assertTrue(self.namespace.token)  # Token should be automatically generated
        self.assertTrue(self.namespace.active)  # Should be active by default

    def test_compute_display_name(self):
        """Test display name computation"""
        expected_name = "/api/test+api+namespace/v1 (Test Description)"
        self.assertEqual(self.namespace.display_name, expected_name)

        # Test without description
        namespace_no_desc = self.env["spp_api.namespace"].create(
            {
                "name": "Test API Namespace 2",
                "version_name": "v2",
            }
        )
        self.assertEqual(namespace_no_desc.display_name, "/api/test+api+namespace+2/v2")

    def test_reset_token(self):
        """Test token reset functionality"""
        old_token = self.namespace.token
        self.namespace.reset_token()
        self.assertNotEqual(old_token, self.namespace.token)
        self.assertTrue(uuid.UUID(self.namespace.token, version=4))

    def test_compute_spec_url(self):
        """Test computation of spec URLs"""
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        expected_spec_url = (
            f"{base_url}/api/test+api+namespace/v1/swagger.json?token={self.namespace.token}&db={self.env.cr.dbname}"
        )
        expected_spec_url_v2 = (
            f"{base_url}/api/swagger-doc/test+api+namespace/v1?token={self.namespace.token}&db={self.env.cr.dbname}"
        )

        self.assertEqual(self.namespace.spec_url, expected_spec_url)
        self.assertEqual(self.namespace.spec_url_v2, expected_spec_url_v2)

    def test_compute_log_count(self):
        """Test log count computation"""
        # Create some test logs
        Log = self.env["spp_api.log"]
        for _ in range(3):
            Log.create(
                {
                    "namespace_id": self.namespace.id,
                    "method": "get",
                    "http_type": "request",
                    "model": "res.partner",  # Adding required model field
                }
            )

        self.namespace._compute_log_count()
        self.assertEqual(self.namespace.log_count, 3)
