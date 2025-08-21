# ABOUTME: Unit tests for hide paid apps functionality
# ABOUTME: Tests the filtering of paid Odoo apps from the Apps list

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHidePaidApps(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Module = self.env["ir.module.module"]
        self.IrConfigParam = self.env["ir.config_parameter"].sudo()

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

        # Check if any paid modules exist (if installed)
        paid_modules = modules.filtered(
            lambda m: m.license and (m.license.startswith("OEEL") or m.license.startswith("OPL"))
        )

        # If paid modules exist in the system, they should be visible
        if self.Module.search([("license", "in", ["OEEL-1", "OPL-1"])]):
            self.assertTrue(paid_modules, "Paid modules should be visible when setting is disabled")

    def test_paid_apps_hidden_when_enabled(self):
        """Test that paid apps are hidden when setting is enabled"""
        # Enable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", True)

        # Search for modules in Apps context
        modules = self.Module.with_context(apps_menu=True).search([])

        # Check that no paid modules are returned
        paid_modules = modules.filtered(
            lambda m: m.license and (m.license.startswith("OEEL") or m.license.startswith("OPL"))
        )

        self.assertFalse(paid_modules, "No paid modules should be visible when setting is enabled")

    def test_paid_apps_visible_outside_apps_menu(self):
        """Test that paid apps remain visible in module management views"""
        # Enable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", True)

        # Search without apps_menu context (simulating module management view)
        modules = self.Module.search([])

        # Check if paid modules are still accessible for management
        all_paid_modules = self.Module.search(["|", ("license", "=like", "OEEL%"), ("license", "=like", "OPL%")])

        modules_paid = modules.filtered(
            lambda m: m.license and (m.license.startswith("OEEL") or m.license.startswith("OPL"))
        )

        # In management context, paid modules should still be accessible
        self.assertEqual(
            len(modules_paid), len(all_paid_modules), "Paid modules should be accessible in management views"
        )

    def test_search_methods_respect_setting(self):
        """Test that all search methods respect the hide paid apps setting"""
        # Enable hiding paid apps
        self.IrConfigParam.set_param("openspp.hide_paid_apps", True)

        # Test _search method
        domain = [("application", "=", True)]
        module_ids = self.Module.with_context(apps_menu=True)._search(domain)
        modules = self.Module.browse(module_ids)
        paid_in_search = modules.filtered(
            lambda m: m.license and (m.license.startswith("OEEL") or m.license.startswith("OPL"))
        )
        self.assertFalse(paid_in_search, "_search should filter paid apps")

        # Test search_fetch method
        modules = self.Module.with_context(apps_menu=True).search_fetch(domain, ["name", "license"])
        paid_in_fetch = modules.filtered(
            lambda m: m.license and (m.license.startswith("OEEL") or m.license.startswith("OPL"))
        )
        self.assertFalse(paid_in_fetch, "search_fetch should filter paid apps")

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
