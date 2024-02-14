import json

from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestSPPCreateNewProgramWiz(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.area_id = cls.env["spp.area"].create(
            {"draft_name": "Area 1 [TEST]"},
        )
        cls.tags_id = cls.env["g2p.registrant.tags"].create(
            {
                "name": "Test Tags",
            }
        )
        cls.program_create_wiz = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "Program 1 [TEST]",
                "eligibility_kind": "tags_eligibility",
                "area_id": cls.area_id.id,
                "tags_id": cls.tags_id.id,
                "entitlement_kind": "default",
                "amount_per_cycle": 1.0,
                "amount_per_individual_in_group": 1.0,
            }
        )
        cls.program = cls.program_create_wiz.create_program()

    def test_01_on_tags_area_change(self):
        self.program_create_wiz.on_tags_area_change()
        expected_result = json.dumps([("tags_ids", "=", self.tags_id.id), ("area_id", "=", self.area_id.id)])

        self.assertEqual(self.program_create_wiz.custom_domain, expected_result)

    def test_02_check_required_fields(self):
        self.program_create_wiz.tags_id = False

        with self.assertRaisesRegex(UserError, "A tag is needed for this eligibility criteria type."):
            self.program_create_wiz._check_required_fields()

    def test_03_get_eligibility_manager(self):
        res = self.program_create_wiz._get_eligibility_manager(self.program["res_id"])

        self.assertIn("eligibility_managers", res)
