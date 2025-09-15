from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestOpenSPPHome(TransactionCase):
    def setUp(self):
        super().setUp()
        self.IrConfigParam = self.env["ir.config_parameter"].sudo()

    # Note: HTTP-specific tests moved to HttpCase in test_http_endpoints.py


# Note: Controller tests that require HTTP request context have been removed
# These tests would require HttpCase instead of TransactionCase to work properly
