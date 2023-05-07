# Part of OpenG2P Registry. See LICENSE file for full copyright and licensing details.

import logging

# from odoo.tests import tagged
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


# @tagged("post_install", "-at_install")
class AreaTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(AreaTest, cls).setUpClass()

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
        cls.area_1._compute_get_childs()
        cls.model = cls.env["spp.area"]

    def test_01_check_childs(self):
        self.assertEqual(len(self.area_1.child_ids), 1)

    def test_02_compute_area_level(self):
        self.assertEqual(
            self.area_1.area_level, 0, "Parent Area should have area level = 0"
        )
        self.assertEqual(
            self.area_1_child.area_level, 1, "Child Area should have area level = 1"
        )

    def test_03_onchange_parent_id(self):
        area_lv_2 = self.model.create(
            {"draft_name": "lv2", "parent_id": self.area_1_child.id}
        )
        area_lv_3 = self.model.create({"draft_name": "lv2", "parent_id": area_lv_2.id})
        area_lv_4 = self.model.create({"draft_name": "lv2", "parent_id": area_lv_3.id})
        area_lv_5 = self.model.create({"draft_name": "lv2", "parent_id": area_lv_4.id})
        area_lv_6 = self.model.create({"draft_name": "lv2", "parent_id": area_lv_5.id})
        area_lv_7 = self.model.create({"draft_name": "lv2", "parent_id": area_lv_6.id})
        area_lv_8 = self.model.create({"draft_name": "lv2", "parent_id": area_lv_7.id})
        area_lv_9 = self.model.create({"draft_name": "lv2", "parent_id": area_lv_8.id})
        area_lv_10 = self.model.create({"draft_name": "lv2", "parent_id": area_lv_9.id})
        area_lv_11 = self.model.create(
            {"draft_name": "lv2", "parent_id": area_lv_10.id}
        )
        with self.assertRaisesRegex(ValidationError, "^Max level exceeded!"):
            area_lv_11._onchange_parent_id()

    def test_04_compute_complete_name(self):
        self.area_1.code = "1"
        self.area_1_child.code = "2"
        self.assertEqual(
            self.area_1.complete_name,
            "1 - Testing Area",
            "Area 1 Complete Name should be [Code] - [DraftName]",
        )
        self.assertEqual(
            self.area_1_child.complete_name,
            "1 - Testing Area > 2 - Testing Area Child",
            "Area Child should have complete name as combination of its name & its parent name",
        )

    def test_05_constraints_name_and_code(self):
        self.area_1.code = "1"
        with self.assertRaisesRegex(ValidationError, "Area already exist!"):
            self.area_1_child.write({"name": "1 - Testing Area", "code": "1"})
        with self.assertRaisesRegex(ValidationError, "Area already exist!"):
            self.env["spp.area"].create(
                {
                    "code": "1",
                    "draft_name": "Testing Area",
                    "name": "1 - Testing Area",
                }
            )

    def test_06_open_area_form(self):
        res = self.area_1.open_area_form()
        self.assertEqual(
            res["res_model"], self.area_1._name, "Should open readonly form for Area 1"
        )
        self.assertEqual(
            res["res_id"], self.area_1.id, "Should open readonly form for Area 1"
        )
        self.assertEqual(
            res["res_id"], self.area_1.id, "Should open readonly form for Area 1"
        )
        self.assertEqual(
            res["res_id"], self.area_1.id, "Should open readonly form for Area 1"
        )
        self.assertEqual(
            res["view_mode"], "form", "Should open readonly form for Area 1"
        )
        self.assertEqual(
            res["flags"], {"mode": "readonly"}, "Should open readonly form for Area 1"
        )
