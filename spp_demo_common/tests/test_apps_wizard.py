# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestAppsWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

    def test_01_create_wizard(self):
        """Test creating apps wizard"""
        wizard = self.env["spp.apps.wizard"].create({})

        self.assertIsNotNone(wizard)

    def test_02_wizard_with_not_installed_modules(self):
        """Test wizard with not installed modules"""
        # Find an uninstalled module
        uninstalled_module = self.env["ir.module.module"].search([("state", "=", "uninstalled")], limit=1)

        if not uninstalled_module:
            self.skipTest("No uninstalled modules found for testing")

        wizard = self.env["spp.apps.wizard"].create(
            {
                "not_installed_module_ids": [(6, 0, [uninstalled_module.id])],
            }
        )

        self.assertEqual(len(wizard.not_installed_module_ids), 1)
        self.assertIn(uninstalled_module, wizard.not_installed_module_ids)

    def test_03_wizard_with_missing_modules(self):
        """Test wizard with missing modules"""
        wizard = self.env["spp.apps.wizard"].create({})

        self.env["spp.missing.module"].create(
            {
                "name": "fake_missing_module",
                "wizard_id": wizard.id,
            }
        )

        self.assertEqual(len(wizard.missing_module_ids), 1)
        self.assertEqual(wizard.missing_module_ids[0].name, "fake_missing_module")

    def test_04_wizard_with_both_types(self):
        """Test wizard with both not installed and missing modules"""
        uninstalled_module = self.env["ir.module.module"].search([("state", "=", "uninstalled")], limit=1)

        if not uninstalled_module:
            self.skipTest("No uninstalled modules found for testing")

        wizard = self.env["spp.apps.wizard"].create(
            {
                "not_installed_module_ids": [(6, 0, [uninstalled_module.id])],
                "missing_module_ids": [(0, 0, {"name": "fake_missing_module"})],
            }
        )

        self.assertEqual(len(wizard.not_installed_module_ids), 1)
        self.assertEqual(len(wizard.missing_module_ids), 1)

    def test_05_install_modules_no_modules(self):
        """Test install_modules with no modules"""
        wizard = self.env["spp.apps.wizard"].create({})

        result = wizard.install_modules()

        # Should return reload action
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(result["tag"], "reload")

    def test_06_missing_module_model(self):
        """Test SPPMissingModule model"""
        wizard = self.env["spp.apps.wizard"].create({})

        missing_module = self.env["spp.missing.module"].create(
            {
                "name": "test_missing_module",
                "wizard_id": wizard.id,
            }
        )

        self.assertEqual(missing_module.name, "test_missing_module")
        self.assertEqual(missing_module.wizard_id, wizard)

    def test_07_missing_module_readonly_fields(self):
        """Test missing module readonly fields"""
        wizard = self.env["spp.apps.wizard"].create({})

        missing_module = self.env["spp.missing.module"].create(
            {
                "name": "readonly_test_module",
                "wizard_id": wizard.id,
            }
        )

        # Check field properties
        name_field = missing_module._fields["name"]
        wizard_field = missing_module._fields["wizard_id"]

        self.assertTrue(name_field.readonly)
        self.assertTrue(wizard_field.readonly)

    def test_08_wizard_transient_model(self):
        """Test that wizard is a transient model"""
        wizard = self.env["spp.apps.wizard"].create({})

        self.assertTrue(wizard._transient)

    def test_09_missing_module_transient_model(self):
        """Test that missing module is a transient model"""
        wizard = self.env["spp.apps.wizard"].create({})

        missing_module = self.env["spp.missing.module"].create(
            {
                "name": "transient_test",
                "wizard_id": wizard.id,
            }
        )

        self.assertTrue(missing_module._transient)

    def test_10_wizard_fields_exist(self):
        """Test that wizard fields exist"""
        wizard = self.env["spp.apps.wizard"].create({})

        self.assertIn("not_installed_module_ids", wizard._fields)
        self.assertIn("missing_module_ids", wizard._fields)

    def test_11_missing_module_fields_exist(self):
        """Test that missing module fields exist"""
        wizard = self.env["spp.apps.wizard"].create({})

        missing_module = self.env["spp.missing.module"].create(
            {
                "name": "field_test",
                "wizard_id": wizard.id,
            }
        )

        self.assertIn("name", missing_module._fields)
        self.assertIn("wizard_id", missing_module._fields)

    def test_12_multiple_missing_modules(self):
        """Test wizard with multiple missing modules"""
        wizard = self.env["spp.apps.wizard"].create(
            {
                "missing_module_ids": [
                    (0, 0, {"name": "missing_module_1"}),
                    (0, 0, {"name": "missing_module_2"}),
                    (0, 0, {"name": "missing_module_3"}),
                ],
            }
        )

        self.assertEqual(len(wizard.missing_module_ids), 3)
        module_names = wizard.missing_module_ids.mapped("name")
        self.assertIn("missing_module_1", module_names)
        self.assertIn("missing_module_2", module_names)
        self.assertIn("missing_module_3", module_names)

    def test_13_multiple_not_installed_modules(self):
        """Test wizard with multiple not installed modules"""
        uninstalled_modules = self.env["ir.module.module"].search([("state", "=", "uninstalled")], limit=3)

        if len(uninstalled_modules) < 2:
            self.skipTest("Not enough uninstalled modules found for testing")

        wizard = self.env["spp.apps.wizard"].create(
            {
                "not_installed_module_ids": [(6, 0, uninstalled_modules.ids)],
            }
        )

        self.assertGreaterEqual(len(wizard.not_installed_module_ids), 2)

    def test_14_wizard_one2many_relation(self):
        """Test one2many relation from wizard to missing modules"""
        wizard = self.env["spp.apps.wizard"].create({})

        missing_module1 = self.env["spp.missing.module"].create(
            {
                "name": "relation_test_1",
                "wizard_id": wizard.id,
            }
        )

        missing_module2 = self.env["spp.missing.module"].create(
            {
                "name": "relation_test_2",
                "wizard_id": wizard.id,
            }
        )

        self.assertIn(missing_module1, wizard.missing_module_ids)
        self.assertIn(missing_module2, wizard.missing_module_ids)

    def test_15_wizard_many2many_relation(self):
        """Test many2many relation for not_installed_module_ids"""
        uninstalled_modules = self.env["ir.module.module"].search([("state", "=", "uninstalled")], limit=2)

        if len(uninstalled_modules) < 2:
            self.skipTest("Not enough uninstalled modules found for testing")

        wizard = self.env["spp.apps.wizard"].create(
            {
                "not_installed_module_ids": [(6, 0, uninstalled_modules.ids)],
            }
        )

        # Many2many field should have the modules
        for module in uninstalled_modules:
            self.assertIn(module, wizard.not_installed_module_ids)

    def test_16_empty_wizard(self):
        """Test empty wizard with no modules"""
        wizard = self.env["spp.apps.wizard"].create({})

        self.assertEqual(len(wizard.not_installed_module_ids), 0)
        self.assertEqual(len(wizard.missing_module_ids), 0)

    def test_17_update_wizard_modules(self):
        """Test updating wizard module lists"""
        wizard = self.env["spp.apps.wizard"].create(
            {
                "missing_module_ids": [(0, 0, {"name": "initial_module"})],
            }
        )

        self.assertEqual(len(wizard.missing_module_ids), 1)

        # Add more modules
        wizard.write(
            {
                "missing_module_ids": [(0, 0, {"name": "additional_module"})],
            }
        )

        self.assertEqual(len(wizard.missing_module_ids), 2)
