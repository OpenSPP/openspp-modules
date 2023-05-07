from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestAreaKind(TransactionCase):
    def setUp(self):
        super().setUp()
        self.data = self.env.ref("spp_area.admin_area_kind")
        self.test_area_kind = self.env["spp.area.kind"].create(
            {
                "name": "Test Area Kind",
                "parent_id": self.data.id,
            }
        )

    def test_01_compute_complete_name(self):
        self.assertEqual(
            self.data.complete_name,
            "Admin Area",
            "Parent Area should have complete name == name",
        )
        self.assertEqual(
            self.test_area_kind.complete_name,
            "Admin Area > Test Area Kind",
            "Child Area should have complete name including its parent complete name",
        )

    def test_02_write(self):
        with self.assertRaisesRegex(ValidationError, "Can't edit default Area Kind"):
            self.data.write({"name": "New name"})

    def test_03_unlink(self):
        with self.assertRaisesRegex(ValidationError, "Can't delete default Area Kind"):
            self.data.unlink()
        self.env["spp.area"].create(
            {
                "draft_name": "Draft Name",
                "kind": self.test_area_kind.id,
            }
        )
        with self.assertRaisesRegex(ValidationError, "Can't delete used Area Kind"):
            self.test_area_kind.unlink()
