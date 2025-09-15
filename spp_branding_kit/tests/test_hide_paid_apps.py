# ABOUTME: Unit tests for hide paid apps functionality
# ABOUTME: Tests the filtering of paid Odoo apps from the Apps list

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHidePaidApps(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Module = self.env["ir.module.module"]
        self.IrConfigParam = self.env["ir.config_parameter"].sudo()

        # Create dummy test modules with different licenses
        self.paid_module_oeel = self.Module.create(
            {
                "name": "test_enterprise_app",
                "shortdesc": "Test Enterprise App",
                "state": "installed",
                "license": "OEEL-1",
                "application": True,
            }
        )

        self.paid_module_opl = self.Module.create(
            {
                "name": "test_opl_app",
                "shortdesc": "Test OPL App",
                "state": "installed",
                "license": "OPL-1",
                "application": True,
            }
        )

        self.free_module = self.Module.create(
            {
                "name": "test_free_app",
                "shortdesc": "Test Free App",
                "state": "installed",
                "license": "LGPL-3",
                "application": True,
            }
        )

    def test_paid_apps_hidden_by_default(self):
        """Test that paid apps are hidden by default"""
        # Check default setting (should be True)
        default_value = self.IrConfigParam.get_param("openspp.hide_paid_apps", False)
        self.assertTrue(default_value, "Hide paid apps should be enabled by default")

    def test_paid_apps_visible_when_disabled(self):
        """Test that paid apps are visible when setting is explicitly disabled"""
        # Explicitly disable the setting
        self.IrConfigParam.set_param("openspp.hide_paid_apps", "False")

        # Search for modules in Apps context
        modules = self.Module.with_context(apps_menu=True).search([])

        # Check that our test paid modules are visible
        self.assertIn(self.paid_module_oeel, modules, "OEEL test module should be visible when setting is disabled")
        self.assertIn(self.paid_module_opl, modules, "OPL test module should be visible when setting is disabled")
        self.assertIn(self.free_module, modules, "Free module should always be visible")

    def test_paid_apps_hidden_when_enabled(self):
        """Test that paid apps are hidden when setting is enabled"""
        # Enable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", "True")
        # Use web API read for Apps UI (filtered)
        result = self.Module.with_context(apps_menu=True).web_search_read(
            domain=[], specification={"name": {}, "license": {}}
        )
        names = {r["name"] for r in result["records"]}
        self.assertNotIn(self.paid_module_oeel.name, names, "OEEL test module should be hidden when setting is enabled")
        self.assertNotIn(self.paid_module_opl.name, names, "OPL test module should be hidden when setting is enabled")
        self.assertIn(self.free_module.name, names, "Free module should still be visible")

    def test_paid_apps_visible_outside_apps_menu(self):
        """Test that paid apps remain visible in module management views"""
        # Enable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", "True")

        # Search without apps_menu context (simulating module management view)
        modules = self.Module.search([])

        # Check that our test paid modules ARE visible outside apps menu context
        self.assertIn(self.paid_module_oeel, modules, "OEEL test module should be visible outside apps menu")
        self.assertIn(self.paid_module_opl, modules, "OPL test module should be visible outside apps menu")
        self.assertIn(self.free_module, modules, "Free module should be visible outside apps menu")

    def test_ui_search_methods_respect_setting(self):
        """Test that all search methods respect the hide paid apps setting"""
        # Enable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", "True")

        domain = [("application", "=", True)]

        # Test search_fetch method
        modules = self.Module.with_context(apps_menu=True).search_fetch(domain, ["name", "license"])
        module_names = [m.name for m in modules]
        self.assertNotIn("test_enterprise_app", module_names, "search_fetch should filter OEEL apps")
        self.assertNotIn("test_opl_app", module_names, "search_fetch should filter OPL apps")
        self.assertIn("test_free_app", module_names, "search_fetch should not filter free apps")

        # Test web_search_read method
        result = self.Module.with_context(apps_menu=True).web_search_read(
            domain=domain, specification={"name": {}, "license": {}}
        )
        paid_in_web = [
            r
            for r in result["records"]
            if r.get("license") and (r["license"].startswith("OEEL") or r["license"].startswith("OPL"))
        ]
        self.assertFalse(paid_in_web, "web_search_read should filter paid apps")

    def test_edge_cases_with_none_license(self):
        """Test handling of modules with None or empty license"""
        # Create module with no license
        no_license_module = self.Module.create(
            {
                "name": "test_no_license",
                "shortdesc": "Test No License",
                "state": "installed",
                "license": False,  # No license
                "application": True,
            }
        )

        # Enable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", "True")

        # Search for modules in Apps context
        modules = self.Module.with_context(apps_menu=True).search([])

        # Module with no license should be visible
        self.assertIn(no_license_module, modules, "Modules with no license should be visible")

    def test_paid_license_variations_filtered_in_ui(self):
        """Test that different variations of paid licenses are filtered"""
        # Create modules with various paid license formats
        oeel_variations = [
            self.Module.create(
                {
                    "name": f"test_oeel_{i}",
                    "shortdesc": f"Test OEEL {i}",
                    "state": "installed",
                    "license": license,
                    "application": True,
                }
            )
            for i, license in enumerate(["OEEL-1"])
        ]

        opl_variations = [
            self.Module.create(
                {
                    "name": f"test_opl_{i}",
                    "shortdesc": f"Test OPL {i}",
                    "state": "installed",
                    "license": license,
                    "application": True,
                }
            )
            for i, license in enumerate(["OPL-1"])
        ]

        # Enable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", "True")

        # UI web read should filter paid license variants
        result = self.Module.with_context(apps_menu=True).web_search_read(
            domain=[], specification={"name": {}, "license": {}}
        )
        names = {r["name"] for r in result["records"]}
        for module in oeel_variations + opl_variations:
            self.assertNotIn(module.name, names, f"Module with license {module.license} should be hidden")
