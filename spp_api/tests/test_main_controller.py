from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged("post_install", "-at_install", "test_main_controller")
class TestOASController(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test namespace
        cls.test_namespace = cls.env["spp_api.namespace"].create(
            {"name": "test", "version_name": "1.0", "active": True, "token": "test_token"}
        )

    def setUp(self):
        super().setUp()
        # Set up request environment
        self.authenticate("admin", "admin")
        self.url_open("/")  # This initializes the request object

    def test_01_index(self):
        """Test the index method of OAS controller"""
        # Test the index endpoint directly
        response = self.url_open("/doc/api-docs/index.html")
        self.assertEqual(response.status_code, 200)

    def test_02_get_api_urls(self):
        """Test the _get_api_urls method of OAS controller"""
        # Test the endpoint that uses _get_api_urls
        response = self.url_open("/doc/api-docs/index.html")
        self.assertEqual(response.status_code, 200)

        # Verify the namespace is accessible
        namespace = self.env["spp_api.namespace"].sudo().search([("name", "=", "test"), ("version_name", "=", "1.0")])
        self.assertTrue(namespace)
        self.assertTrue(namespace.active)

    def test_03_oas_json_spec_download(self):
        """Test the oas_json_spec_download method of OAS controller"""
        # Test with valid namespace and token
        response = self.url_open(f"/api/test/1.0/swagger.json?token={self.test_namespace.token}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "application/json")

        # Test with invalid namespace
        response = self.url_open("/api/invalid/1.0/swagger.json?token=test_token", allow_redirects=False)
        self.assertEqual(response.status_code, 404)

        # Test with invalid token
        response = self.url_open("/api/test/1.0/swagger.json?token=invalid_token", allow_redirects=False)
        self.assertEqual(response.status_code, 403)

    def test_04_oas_document(self):
        """Test the oas_document method of OAS controller"""
        # Test with valid namespace and token
        response = self.url_open(f"/api/swagger-doc/test/1.0?token={self.test_namespace.token}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["Content-Type"].startswith("text/html"))

        # Test with invalid namespace
        response = self.url_open("/api/swagger-doc/invalid/1.0?token=test_token", allow_redirects=False)
        self.assertEqual(response.status_code, 404)

        # Test with invalid token
        response = self.url_open("/api/swagger-doc/test/1.0?token=invalid_token", allow_redirects=False)
        self.assertEqual(response.status_code, 403)
