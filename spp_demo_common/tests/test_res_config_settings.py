# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestResConfigSettings(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

    def test_01_config_settings_fields_exist(self):
        """Test that custom config fields are available"""
        config = self.env["res.config.settings"].create({})

        # Check that custom fields exist
        self.assertIn("number_of_groups", config._fields)
        self.assertIn("members_range_from", config._fields)
        self.assertIn("members_range_to", config._fields)
        self.assertIn("batch_size", config._fields)
        self.assertIn("queue_job_minimum_size", config._fields)

    def test_02_set_values_number_of_groups(self):
        """Test setting number_of_groups config parameter"""
        config = self.env["res.config.settings"].create(
            {
                "number_of_groups": 50,
            }
        )

        config.execute()

        # Verify the parameter was set
        param_value = self.env["ir.config_parameter"].sudo().get_param("spp_demo_common.number_of_groups")
        self.assertEqual(int(param_value), 50)

    def test_03_set_values_members_range_from(self):
        """Test setting members_range_from config parameter"""
        config = self.env["res.config.settings"].create(
            {
                "members_range_from": 5,
            }
        )

        config.execute()

        # Verify the parameter was set
        param_value = self.env["ir.config_parameter"].sudo().get_param("spp_demo_common.members_range_from")
        self.assertEqual(int(param_value), 5)

    def test_04_set_values_members_range_to(self):
        """Test setting members_range_to config parameter"""
        config = self.env["res.config.settings"].create(
            {
                "members_range_to": 15,
            }
        )

        config.execute()

        # Verify the parameter was set
        param_value = self.env["ir.config_parameter"].sudo().get_param("spp_demo_common.members_range_to")
        self.assertEqual(int(param_value), 15)

    def test_05_set_values_batch_size(self):
        """Test setting batch_size config parameter"""
        config = self.env["res.config.settings"].create(
            {
                "batch_size": 200,
            }
        )

        config.execute()

        # Verify the parameter was set
        param_value = self.env["ir.config_parameter"].sudo().get_param("spp_demo_common.batch_size")
        self.assertEqual(int(param_value), 200)

    def test_06_set_values_queue_job_minimum_size(self):
        """Test setting queue_job_minimum_size config parameter"""
        config = self.env["res.config.settings"].create(
            {
                "queue_job_minimum_size": 1000,
            }
        )

        config.execute()

        # Verify the parameter was set
        param_value = self.env["ir.config_parameter"].sudo().get_param("spp_demo_common.queue_job_minimum_size")
        self.assertEqual(int(param_value), 1000)

    def test_07_get_values(self):
        """Test getting config parameter values"""
        # Set parameters
        self.env["ir.config_parameter"].sudo().set_param("spp_demo_common.number_of_groups", "25")
        self.env["ir.config_parameter"].sudo().set_param("spp_demo_common.members_range_from", "3")
        self.env["ir.config_parameter"].sudo().set_param("spp_demo_common.members_range_to", "8")
        self.env["ir.config_parameter"].sudo().set_param("spp_demo_common.batch_size", "150")
        self.env["ir.config_parameter"].sudo().set_param("spp_demo_common.queue_job_minimum_size", "750")

        # Create config and check values
        config = self.env["res.config.settings"].create({})

        self.assertEqual(config.number_of_groups, 25)
        self.assertEqual(config.members_range_from, 3)
        self.assertEqual(config.members_range_to, 8)
        self.assertEqual(config.batch_size, 150)
        self.assertEqual(config.queue_job_minimum_size, 750)

    def test_08_set_multiple_values(self):
        """Test setting multiple config parameters at once"""
        config = self.env["res.config.settings"].create(
            {
                "number_of_groups": 100,
                "members_range_from": 2,
                "members_range_to": 12,
                "batch_size": 300,
                "queue_job_minimum_size": 2000,
            }
        )

        config.execute()

        # Verify all parameters were set
        self.assertEqual(int(self.env["ir.config_parameter"].sudo().get_param("spp_demo_common.number_of_groups")), 100)
        self.assertEqual(int(self.env["ir.config_parameter"].sudo().get_param("spp_demo_common.members_range_from")), 2)
        self.assertEqual(int(self.env["ir.config_parameter"].sudo().get_param("spp_demo_common.members_range_to")), 12)
        self.assertEqual(int(self.env["ir.config_parameter"].sudo().get_param("spp_demo_common.batch_size")), 300)
        self.assertEqual(
            int(self.env["ir.config_parameter"].sudo().get_param("spp_demo_common.queue_job_minimum_size")), 2000
        )

    def test_09_default_values(self):
        """Test default values when no config parameters are set"""
        # Clear all parameters
        param_names = [
            "spp_demo_common.number_of_groups",
            "spp_demo_common.members_range_from",
            "spp_demo_common.members_range_to",
            "spp_demo_common.batch_size",
            "spp_demo_common.queue_job_minimum_size",
        ]
        for param_name in param_names:
            param = self.env["ir.config_parameter"].sudo().search([("key", "=", param_name)])
            if param:
                param.unlink()

        config = self.env["res.config.settings"].create({})

        # Should have some default values
        self.assertIsNotNone(config.number_of_groups)
        self.assertIsNotNone(config.members_range_from)
        self.assertIsNotNone(config.members_range_to)
        self.assertIsNotNone(config.batch_size)
        self.assertIsNotNone(config.queue_job_minimum_size)

    def test_10_inherit_model_check(self):
        """Test that res.config.settings is properly inherited"""
        config = self.env["res.config.settings"].create({})

        # Verify it's a TransientModel
        self.assertTrue(config._transient)

        # Verify our custom fields are there
        custom_fields = [
            "number_of_groups",
            "members_range_from",
            "members_range_to",
            "batch_size",
            "queue_job_minimum_size",
        ]
        for field in custom_fields:
            self.assertIn(field, config._fields)
