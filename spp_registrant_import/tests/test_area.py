from psycopg2.errors import UniqueViolation

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase
from odoo.tools import mute_logger

EXCLUDED_CHARACTERS = ["0", "O", "1", "I"]


class TestArea(TransactionCase):
    def setUp(self):
        super().setUp()
        self.area_1, self.area_2 = self.env["spp.area"].create(
            [
                {"draft_name": "Area 1"},
                {"draft_name": "Area 2"},
            ]
        )

    def test_01_compute_spp_id_uniq(self):
        self.assertNotEqual(self.area_1.spp_id, self.area_2.spp_id)

    def test_02_compute_spp_id(self):
        for area in [self.area_1, self.area_2]:
            self.assertRegex(
                area.spp_id,
                r"^LOC_[a-zA-Z0-9]{8}$",
                "Area should have unique id start with " "`LOC_` and following by 8 characters.",
            )
            for char in EXCLUDED_CHARACTERS:
                self.assertNotIn(
                    char,
                    area.spp_id.split("_")[-1],
                    "Excluded characters should not be exist in spp_id",
                )

    @mute_logger("odoo.sql_db")
    def test_03_spp_id_unique_violation(self):
        with self.assertRaises(UniqueViolation):
            self.area_1.write(
                {
                    "spp_id": self.area_2.spp_id,
                }
            )

    @mute_logger("py.warnings")
    def test_04_check_spp_id(self):
        with self.assertRaisesRegex(ValidationError, "^.*not following correct format.{1}$"):
            # 7 characters spp_id
            self.area_1.write({"spp_id": "LOC_AaAaAa2"})
        with self.assertRaisesRegex(ValidationError, "^.*not following correct format.{1}$"):
            # '1' in spp_id
            self.area_2.write({"spp_id": "LOC_AaAaAa21"})
