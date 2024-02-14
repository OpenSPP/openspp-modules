from odoo.tests import TransactionCase


class TestSppApiLog(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.api_log = cls.env["spp_api.log"].create(
            {
                "method": "get",
                "http_type": "request",
                "model": "res.partner",
            }
        )

    def test_01_compute_name(self):
        format_name = f"{self.api_log.http_type} {self.api_log.method} - {self.api_log.model}"
        self.assertEqual(self.api_log.name, format_name)
