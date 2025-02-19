import uuid

from odoo.tests.common import TransactionCase


class TestSPPAPILog(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create a test namespace with all required fields
        self.namespace = self.env["spp_api.namespace"].create(
            {
                "name": "Test Namespace",
                "version_name": "v1",  # Required field
                "token": str(uuid.uuid4()),  # Required field with default
            }
        )

    def test_compute_name(self):
        """Test the name computation of the log entry"""
        log = self.env["spp_api.log"].create(
            {
                "method": "get",
                "http_type": "request",
                "model": "res.partner",
                "namespace_id": self.namespace.id,
            }
        )

        # Check if name is computed correctly
        self.assertEqual(log.name, "request get - res.partner")

    def test_log_creation(self):
        """Test creation of log entries with different methods"""
        test_cases = [
            ("get", "request"),
            ("post", "response"),
            ("put", "request"),
            ("delete", "response"),
            ("patch", "request"),
        ]

        for method, http_type in test_cases:
            log = self.env["spp_api.log"].create(
                {
                    "method": method,
                    "http_type": http_type,
                    "model": "res.partner",
                    "namespace_id": self.namespace.id,
                    "request_id": "TEST123",
                    "request_parameter": '{"id": 1}',
                    "request_data": '{"name": "Test"}',
                    "response_data": '{"success": true}',
                }
            )

            self.assertTrue(log.id)
            self.assertEqual(log.method, method)
            self.assertEqual(log.http_type, http_type)
            self.assertEqual(log.model, "res.partner")
