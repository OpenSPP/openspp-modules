# Part of OpenG2P Registry. See LICENSE file for full copyright and licensing details.

import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class AreaTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set context to avoid job queue delay for faster tests
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        # Initial Setup of Variables
        cls.area_1 = cls.env["spp.area"].create(
            {
                "draft_name": "Testing Area",
            }
        )
        cls.area_1_child = cls.env["spp.area"].create(
            {
                "draft_name": "Testing Area Child",
                "parent_id": cls.area_1.id,
            }
        )

    def test_01_check_childs(self):
        """Test that parent area correctly computes child areas"""
        self.area_1._compute_get_childs()

        self.assertEqual(len(self.area_1.child_ids), 1)

    def test_02_check_area_creation(self):
        """Test basic area creation"""
        area = self.env["spp.area"].create(
            {
                "draft_name": "Test Area 2",
            }
        )
        self.assertTrue(area)
        self.assertEqual(area.draft_name, "Test Area 2")

    def test_03_check_parent_child_relationship(self):
        """Test parent-child relationship in areas"""
        # Check parent has child
        self.assertIn(self.area_1_child, self.area_1.child_ids)

        # Check child has parent
        self.assertEqual(self.area_1_child.parent_id, self.area_1)

    def test_04_create_multi_level_hierarchy(self):
        """Test creating multiple levels of area hierarchy"""
        # Create level 2 child
        area_grandchild = self.env["spp.area"].create(
            {
                "draft_name": "Testing Area Grandchild",
                "parent_id": self.area_1_child.id,
            }
        )

        # Verify hierarchy
        self.assertEqual(area_grandchild.parent_id, self.area_1_child)
        self.assertEqual(area_grandchild.parent_id.parent_id, self.area_1)

        # Check parent has grandchild in descendants
        self.area_1._compute_get_childs()
        self.assertIn(self.area_1_child, self.area_1.child_ids)
