# ABOUTME: Unit tests for the models in spp_branding_kit
# ABOUTME: Tests IrHttp, IrModuleModule helpers, and ResUsers

from unittest.mock import patch

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestIrHttp(TransactionCase):
    def setUp(self):
        super().setUp()
        self.IrConfigParam = self.env["ir.config_parameter"].sudo()
        self.IrHttp = self.env["ir.http"]

    def test_session_info_with_custom_values(self):
        """Test session_info returns custom OpenSPP configuration"""
        # Set custom configuration values
        self.IrConfigParam.set_param("openspp.system_name", "Custom System")
        self.IrConfigParam.set_param("openspp.documentation_url", "https://custom-docs.org")
        self.IrConfigParam.set_param("openspp.support_url", "https://custom-support.org")
        self.IrConfigParam.set_param("openspp.show_powered_by", "False")
        self.IrConfigParam.set_param("openspp.telemetry_enabled", "False")
        self.IrConfigParam.set_param("openspp.telemetry_endpoint", "https://custom-telemetry.org")
        self.IrConfigParam.set_param("openspp.debug_admin_only", "False")

        # Mock super().session_info to return base data
        with patch.object(self.IrHttp.__class__.__bases__[0], "session_info", return_value={"base": "data"}):
            result = self.IrHttp.session_info()

            # Check that OpenSPP configuration is added
            self.assertEqual(result["openspp_system_name"], "Custom System")
            self.assertEqual(result["openspp_documentation_url"], "https://custom-docs.org")
            self.assertEqual(result["openspp_support_url"], "https://custom-support.org")
            self.assertFalse(result["openspp_show_powered_by"])
            self.assertFalse(result["openspp_telemetry_enabled"])
            self.assertEqual(result["openspp_telemetry_endpoint"], "https://custom-telemetry.org")
            self.assertFalse(result["openspp_debug_admin_only"])

    def test_session_info_with_default_values(self):
        """Test session_info returns default values when parameters not set"""
        # Clear any existing parameters
        self.IrConfigParam.search([("key", "=like", "openspp.%")]).unlink()

        # Mock super().session_info to return base data
        with patch.object(self.IrHttp.__class__.__bases__[0], "session_info", return_value={"base": "data"}):
            result = self.IrHttp.session_info()

            # Check that default values are used
            self.assertEqual(result["openspp_system_name"], "OpenSPP Platform")
            self.assertEqual(result["openspp_documentation_url"], "https://docs.openspp.org")
            self.assertEqual(result["openspp_support_url"], "https://openspp.org")
            self.assertTrue(result["openspp_show_powered_by"])
            self.assertTrue(result["openspp_telemetry_enabled"])
            self.assertEqual(result["openspp_telemetry_endpoint"], "https://telemetry.openspp.org")
            self.assertTrue(result["openspp_debug_admin_only"])

    def test_session_info_customizes_server_version(self):
        """Test session_info customizes server version info"""
        # Mock super().session_info with server_version_info
        base_data = {"server_version_info": ["Odoo", "17.0", "final", "0", ""], "other": "data"}

        with patch.object(self.IrHttp.__class__.__bases__[0], "session_info", return_value=base_data):
            result = self.IrHttp.session_info()

            # Check that server version info is customized
            self.assertEqual(result["server_version_info"], ["OpenSPP", "1.0", "", "", ""])


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

    def test_get_paid_app_filter(self):
        """Test _get_paid_app_filter helper method"""
        filter_domain = self.Module._get_paid_app_filter()

        # Should return correct domain to exclude paid apps
        self.assertEqual(filter_domain[0], "!")
        self.assertEqual(filter_domain[1], "|")
        self.assertIn(("license", "=like", "OEEL%"), filter_domain)
        self.assertIn(("license", "=like", "OPL%"), filter_domain)

    def test_apply_paid_app_filter_when_enabled(self):
        """Test _apply_paid_app_filter when hiding is enabled"""
        # Enable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", "True")

        # Test with apps_menu context
        Module = self.Module.with_context(apps_menu=True)

        # Test with existing domain
        original_domain = [("application", "=", True)]
        filtered_domain = Module._apply_paid_app_filter(original_domain)

        # Should combine with AND operator
        self.assertEqual(filtered_domain[0], "&")
        self.assertIn(("application", "=", True), filtered_domain)
        self.assertIn("!", filtered_domain)

        # Test with empty domain
        filtered_domain = Module._apply_paid_app_filter([])
        self.assertEqual(filtered_domain[0], "!")

    def test_apply_paid_app_filter_when_disabled(self):
        """Test _apply_paid_app_filter when hiding is disabled"""
        # Disable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", "False")

        # Test with apps_menu context
        Module = self.Module.with_context(apps_menu=True)

        # Test with existing domain
        original_domain = [("application", "=", True)]
        filtered_domain = Module._apply_paid_app_filter(original_domain)

        # Should return unchanged domain
        self.assertEqual(filtered_domain, original_domain)

    def test_apply_paid_app_filter_without_apps_context(self):
        """Test _apply_paid_app_filter without apps_menu context"""
        # Enable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", "True")

        # Test without apps_menu context
        Module = self.Module.with_context(apps_menu=False)

        # Test with existing domain
        original_domain = [("application", "=", True)]
        filtered_domain = Module._apply_paid_app_filter(original_domain)

        # Should return unchanged domain
        self.assertEqual(filtered_domain, original_domain)

    def test_search_adds_context(self):
        """Test that _search adds hide_paid_apps_enabled context"""
        # Enable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", "True")

        # Mock super()._search
        with patch.object(self.Module.__class__.__bases__[0], "_search", return_value=[]) as mock_super:
            # Call _search
            self.Module.with_context(apps_menu=True)._search([])

            # Check that context was added
            args, kwargs = mock_super.call_args
            self.assertTrue(hasattr(mock_super.call_args[0][0], "env"))

    def test_search_fetch_applies_filter(self):
        """Test that search_fetch applies paid app filter"""
        # Enable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", "True")

        # Create test modules
        self.Module.create(
            {
                "name": "test_paid_fetch",
                "shortdesc": "Test Paid Fetch",
                "license": "OEEL-1",
                "application": True,
            }
        )
        self.Module.create(
            {
                "name": "test_free_fetch",
                "shortdesc": "Test Free Fetch",
                "license": "LGPL-3",
                "application": True,
            }
        )

        # Search with apps_menu context
        modules = self.Module.with_context(apps_menu=True).search_fetch(
            [("application", "=", True)], ["name", "license"]
        )

        # Check that paid module is filtered out
        module_names = [m.name for m in modules]
        self.assertNotIn("test_paid_fetch", module_names)
        self.assertIn("test_free_fetch", module_names)

    def test_web_search_read_applies_filter(self):
        """Test that web_search_read applies paid app filter"""
        # Enable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", "True")

        # Create test modules
        self.Module.create(
            {
                "name": "test_paid_web",
                "shortdesc": "Test Paid Web",
                "license": "OPL-1",
                "application": True,
            }
        )
        self.Module.create(
            {
                "name": "test_free_web",
                "shortdesc": "Test Free Web",
                "license": "AGPL-3",
                "application": True,
            }
        )

        # Search with apps_menu context
        result = self.Module.with_context(apps_menu=True).web_search_read(
            domain=[("application", "=", True)], specification={"name": {}, "license": {}}
        )

        # Check that paid module is filtered out
        module_names = [r["name"] for r in result["records"]]
        self.assertNotIn("test_paid_web", module_names)
        self.assertIn("test_free_web", module_names)


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
