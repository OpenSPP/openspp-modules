from odoo.tests import TransactionCase, tagged

# Note: IrHttp session_info tests have been removed because they require HTTP request context
# The session_info method needs request.session which doesn't exist in unit tests


@tagged("post_install", "-at_install")
class TestIrModuleModuleHelpers(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Module = self.env["ir.module.module"]
        self.IrConfigParam = self.env["ir.config_parameter"].sudo()

    def test_get_paid_apps_count(self):
        """Test get_paid_apps_count method"""
        # Create test modules with different licenses
        self.Module.create(
            {
                "name": "test_oeel_app",
                "shortdesc": "Test OEEL App",
                "license": "OEEL-1",
            }
        )
        self.Module.create(
            {
                "name": "test_opl_app",
                "shortdesc": "Test OPL App",
                "license": "OPL-1",
            }
        )
        self.Module.create(
            {
                "name": "test_free_app",
                "shortdesc": "Test Free App",
                "license": "LGPL-3",
            }
        )

        # Get count of paid apps
        count = self.Module.get_paid_apps_count()

        # Should count OEEL and OPL apps
        self.assertGreaterEqual(count, 2, "Should count at least the two paid test apps")

    # Filtering tests removed: filtering now handled in UI only


@tagged("post_install", "-at_install")
class TestResUsers(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ResUsers = self.env["res.users"]

    def test_get_default_email_signature(self):
        """Test that default email signature is customized"""
        signature = self.ResUsers._get_default_email_signature()

        # Check that signature contains OpenSPP branding
        self.assertIn("OpenSPP Platform", signature)
        self.assertIn("Open Source Social Protection Platform", signature)
        self.assertNotIn("Odoo", signature)

    def test_compute_odoo_account_url(self):
        """Test that Odoo account URL is removed"""
        # Create a test user
        user = self.ResUsers.create(
            {
                "name": "Test User",
                "login": "test_user_account",
                "email": "test@example.com",
            }
        )

        # Check that odoo_account_url is False
        self.assertFalse(user.odoo_account_url)

        # Try to manually set it (should be computed to False)
        user._compute_odoo_account_url()
        self.assertFalse(user.odoo_account_url)

    def test_odoo_account_url_field_properties(self):
        """Test that odoo_account_url field has correct properties"""
        # Get field definition
        field = self.ResUsers._fields.get("odoo_account_url")

        # Check field properties
        self.assertIsNotNone(field)
        self.assertEqual(field.string, "Account URL")
        self.assertEqual(field.help, "OpenSPP Account Management")
        self.assertTrue(field.compute)
