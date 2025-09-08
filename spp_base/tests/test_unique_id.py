# Part of OpenSPP Registry. See LICENSE file for full copyright and licensing details.
import re

from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase
from odoo.tools import mute_logger


class TestSppUniqueID(TransactionCase):
    @mute_logger("py.warnings")
    def test_01_spp_id_generation_and_format(self):
        """Test that spp_id is generated correctly on creation."""
        test_record = self.env["spp.unique.id.test"].create({"name": "Test Record 1"})
        self.assertTrue(test_record.spp_id, "spp_id should be generated on creation.")
        self.assertTrue(
            test_record.spp_id.startswith("TEST_"),
            "spp_id should start with the correct prefix.",
        )

        # Check format using regex
        pattern = re.compile(r"^TEST_[2-9A-HJ-NP-Z]{8}$")
        self.assertIsNotNone(pattern.match(test_record.spp_id), "spp_id has an invalid format.")

    @mute_logger("odoo.sql_db")
    def test_02_spp_id_uniqueness(self):
        """Test the SQL constraint for spp_id uniqueness."""
        test_record_1 = self.env["spp.unique.id.test"].create({"name": "Test Record 2"})
        self.assertTrue(test_record_1.spp_id)

        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self.env["spp.unique.id.test"].create({"name": "Test Record 3", "spp_id": test_record_1.spp_id})

    @mute_logger("py.warnings")
    def test_03_spp_id_format_constraint_invalid_prefix(self):
        """Test the python constraint on spp_id with an invalid prefix."""
        test_record = self.env["spp.unique.id.test"].new({"name": "Invalid Prefix", "spp_id": "FAIL_ABCDE123"})
        with self.assertRaisesRegex(ValidationError, "Unique ID is not following correct format!"):
            test_record._check_spp_id()

    @mute_logger("py.warnings")
    def test_04_spp_id_format_constraint_invalid_chars(self):
        """Test the python constraint on spp_id with forbidden characters."""
        test_record = self.env["spp.unique.id.test"].new({"name": "Invalid Chars", "spp_id": "TEST_ABCDE123"})
        with self.assertRaisesRegex(ValidationError, "Unique ID is not following correct format!"):
            test_record._check_spp_id()

    @mute_logger("py.warnings")
    def test_05_spp_id_not_recomputed(self):
        """Test that spp_id is not recomputed on subsequent writes."""
        test_record = self.env["spp.unique.id.test"].create({"name": "Initial Name"})
        original_spp_id = test_record.spp_id
        self.assertTrue(original_spp_id)

        test_record.write({"name": "Updated Name"})
        self.assertEqual(
            test_record.spp_id,
            original_spp_id,
            "spp_id should not change on update.",
        )
