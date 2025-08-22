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
        self.IrConfigParam.set_param("openspp.hide_paid_apps", False)

        # Search for modules in Apps context
        modules = self.Module.with_context(apps_menu=True).search([])

        # Check that our test paid modules are visible
        self.assertIn(self.paid_module_oeel, modules, "OEEL test module should be visible when setting is disabled")
        self.assertIn(self.paid_module_opl, modules, "OPL test module should be visible when setting is disabled")
        self.assertIn(self.free_module, modules, "Free module should always be visible")

    def test_paid_apps_hidden_when_enabled(self):
        """Test that paid apps are hidden when setting is enabled"""
        # Enable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", True)

        # Search for modules in Apps context
        modules = self.Module.with_context(apps_menu=True).search([])

        # Check that our test paid modules are NOT visible, but free module is
        self.assertNotIn(self.paid_module_oeel, modules, "OEEL test module should be hidden when setting is enabled")
        self.assertNotIn(self.paid_module_opl, modules, "OPL test module should be hidden when setting is enabled")
        self.assertIn(self.free_module, modules, "Free module should still be visible")

    def test_paid_apps_visible_outside_apps_menu(self):
        """Test that paid apps remain visible in module management views"""
        # Enable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", True)

        # Search without apps_menu context (simulating module management view)
        modules = self.Module.search([])

        # Check that our test paid modules ARE visible outside apps menu context
        self.assertIn(self.paid_module_oeel, modules, "OEEL test module should be visible outside apps menu")
        self.assertIn(self.paid_module_opl, modules, "OPL test module should be visible outside apps menu")
        self.assertIn(self.free_module, modules, "Free module should be visible outside apps menu")

    def test_search_methods_respect_setting(self):
        """Test that all search methods respect the hide paid apps setting"""
        # Enable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", True)

        # Test _search method
        domain = [("application", "=", True)]
        module_ids = self.Module.with_context(apps_menu=True)._search(domain)

        # Our test paid modules should not be in results
        self.assertNotIn(self.paid_module_oeel.id, module_ids, "_search should filter OEEL apps")
        self.assertNotIn(self.paid_module_opl.id, module_ids, "_search should filter OPL apps")
        self.assertIn(self.free_module.id, module_ids, "_search should not filter free apps")

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
