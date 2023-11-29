from psycopg2.errors import UniqueViolation

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase
from odoo.tools import mute_logger

EXCLUDED_CHARACTERS = ["0", "O", "1", "I"]


class TestRegistrant(TransactionCase):
    def setUp(self):
        super().setUp()
        self._test_household = self.env["res.partner"].create(
            {
                "name": "Test Household 1",
                "is_registrant": True,
                "is_group": True,
            }
        )
        self._test_individuals = self.env["res.partner"].create(
            [
                {
                    "name": "Test Individual 1",
                    "is_registrant": True,
                    "is_group": False,
                },
                {
                    "name": "Test Individual 2",
                    "is_registrant": True,
                    "is_group": False,
                },
            ]
        )
        self._partner = self.env["res.partner"].create(
            {
                "name": "Partner 1",
            }
        )
        (
            self._partner | self._test_household | self._test_individuals
        )._compute_spp_id()

    def test_01_compute_spp_id_normal_partner(self):
        self.assertFalse(
            bool(self._partner.spp_id),
            "Normal Odoo contact should not have spp_id",
        )

    def test_02_compute_spp_id_household(self):
        self.assertRegex(
            self._test_household.spp_id,
            r"^GRP_[a-zA-Z0-9]{8}$",
            "Household should have unique registrant id start with "
            "`GRP_` and following by 8 characters.",
        )
        for char in EXCLUDED_CHARACTERS:
            self.assertNotIn(
                char,
                self._test_household.spp_id.split("_")[-1],
                "Excluded characters should not be exist in unique spp_id",
            )

    def test_03_compute_spp_id_individual(self):
        for individual in self._test_individuals:
            self.assertRegex(
                individual.spp_id,
                r"^IND_[a-zA-Z0-9]{8}$",
                "Individual should have unique registrant id start with "
                "`IND_` and following by 8 characters.",
            )
            for char in EXCLUDED_CHARACTERS:
                self.assertNotIn(
                    char,
                    individual.spp_id.split("_")[-1],
                    "Excluded characters should not be exist in unique spp_id",
                )

    @mute_logger("odoo.sql_db")
    def test_04_compute_spp_id_unique_violation(self):
        with self.assertRaises(UniqueViolation):
            self._test_individuals[0].write(
                {
                    "spp_id": self._test_individuals[1].spp_id,
                }
            )

    @mute_logger("py.warnings")
    def test_05_check_spp_id(self):
        with self.assertRaisesRegex(
            ValidationError, "^.*not following correct format.{1}$"
        ):
            # 7 characters spp_id
            self._test_household.write({"spp_id": "GRP_AaAaAa2"})
        with self.assertRaisesRegex(
            ValidationError, "^.*not following correct format.{1}$"
        ):
            # '1' in spp_id
            self._test_individuals[0].write({"spp_id": "IND_AaAaAa21"})
        self._partner.write({"spp_id": "IND_AaAaAa21"})
