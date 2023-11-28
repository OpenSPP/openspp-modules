from psycopg2.errors import UniqueViolation

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase
from odoo.tools import mute_logger

EXCLUDED_CHARACTERS = ["0", "O", "1", "I"]


class TestRegistrant(TransactionCase):
    def setUp(self):
        super().setUp()
        self.service_point_1, self.service_point_2 = self.env[
            "spp.service.point"
        ].create(
            [
                {"name": "Service Point 1"},
                {"name": "Service Point 2"},
            ]
        )
        (self.service_point_1 | self.service_point_2)._compute_registrant_id()

    def test_01_compute_registrant_id_uniq(self):
        self.assertNotEqual(
            self.service_point_1.registrant_id, self.service_point_2.registrant_id
        )

    def test_02_compute_registrant_id(self):
        for area in [self.service_point_1, self.service_point_2]:
            self.assertRegex(
                area.registrant_id,
                r"^SVP_[a-zA-Z0-9]{8}$",
                "Area should have unique id start with "
                "`SVP_` and following by 8 characters.",
            )
            for char in EXCLUDED_CHARACTERS:
                self.assertNotIn(
                    char,
                    area.registrant_id.split("_")[-1],
                    "Excluded characters should not be exist in registrant_id",
                )

    @mute_logger("odoo.sql_db")
    def test_03_registrant_id_unique_violation(self):
        with self.assertRaises(UniqueViolation):
            self.service_point_1.write(
                {
                    "registrant_id": self.service_point_2.registrant_id,
                }
            )

    @mute_logger("py.warnings")
    def test_04_check_registrant_id(self):
        with self.assertRaisesRegex(
            ValidationError, "^.*not following correct format.{1}$"
        ):
            # 7 characters registrant_id
            self.service_point_1.write({"registrant_id": "SVP_AaAaAa2"})
        with self.assertRaisesRegex(
            ValidationError, "^.*not following correct format.{1}$"
        ):
            # '1' in registrant_id
            self.service_point_2.write({"registrant_id": "SVP_AaAaAa21"})
