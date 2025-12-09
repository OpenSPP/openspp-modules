from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestNameSuffix(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_queue_job_no_delay=True,
            )
        )

        # Use existing suffixes from data file
        cls.suffix_jr = cls.env.ref("spp_registry_name_suffix.suffix_jr")
        cls.suffix_phd = cls.env.ref("spp_registry_name_suffix.suffix_phd")

    def test_01_suffix_model_creation(self):
        """Test that suffix model can be created correctly."""
        suffix = self.env["spp.name.suffix"].create(
            {
                "name": "Test Suffix",
                "code": "TEST",
            }
        )
        self.assertTrue(suffix.active)
        self.assertEqual(suffix.sequence, 10)  # Default

    def test_02_suffix_data_loaded(self):
        """Test that default suffix data is loaded correctly."""
        self.assertEqual(self.suffix_jr.name, "Jr.")
        self.assertEqual(self.suffix_jr.code, "JR")
        self.assertEqual(self.suffix_phd.name, "PhD")
        self.assertEqual(self.suffix_phd.code, "PHD")

    def test_03_name_with_single_suffix(self):
        """Test that a single suffix is appended to the computed name."""
        individual = self.env["res.partner"].create(
            {
                "name": "Temp",  # Required by res_partner_check_name constraint
                "family_name": "Doe",
                "given_name": "John",
                "suffix_ids": [(6, 0, [self.suffix_jr.id])],
                "is_registrant": True,
                "is_group": False,
            }
        )
        # Call name_change to generate name (simulates form onchange)
        individual.name_change()
        self.assertEqual(
            individual.name,
            "DOE, JOHN, JR.",
            "Name should include suffix",
        )

    def test_04_name_without_suffix(self):
        """Test that name is computed correctly without suffix."""
        individual = self.env["res.partner"].create(
            {
                "name": "Temp",  # Required by res_partner_check_name constraint
                "family_name": "Doe",
                "given_name": "Jane",
                "is_registrant": True,
                "is_group": False,
            }
        )
        individual.name_change()
        self.assertEqual(
            individual.name,
            "DOE, JANE",
            "Name should not have trailing comma when no suffix",
        )

    def test_05_name_with_multiple_suffixes(self):
        """Test name with multiple suffixes (e.g., Jr. and PhD)."""
        individual = self.env["res.partner"].create(
            {
                "name": "Temp",  # Required by res_partner_check_name constraint
                "family_name": "Smith",
                "given_name": "Robert",
                "suffix_ids": [(6, 0, [self.suffix_jr.id, self.suffix_phd.id])],
                "is_registrant": True,
                "is_group": False,
            }
        )
        individual.name_change()
        # Jr. has sequence 10, PhD has sequence 100, so Jr. comes first
        self.assertEqual(
            individual.name,
            "SMITH, ROBERT, JR., PHD",
            "Name should include multiple suffixes in sequence order",
        )

    def test_06_name_with_all_fields_and_multiple_suffixes(self):
        """Test name with all fields including addl_name and multiple suffixes."""
        individual = self.env["res.partner"].create(
            {
                "name": "Temp",  # Required by res_partner_check_name constraint
                "family_name": "Williams",
                "given_name": "James",
                "addl_name": "Edward",
                "suffix_ids": [(6, 0, [self.suffix_jr.id, self.suffix_phd.id])],
                "is_registrant": True,
                "is_group": False,
            }
        )
        individual.name_change()
        self.assertEqual(
            individual.name,
            "WILLIAMS, JAMES EDWARD, JR., PHD",
            "Name should include all parts including multiple suffixes",
        )

    def test_07_group_name_unaffected(self):
        """Test that group name is not affected by suffix logic."""
        group = self.env["res.partner"].create(
            {
                "name": "Test Group",
                "suffix_ids": [(6, 0, [self.suffix_jr.id])],
                "is_registrant": True,
                "is_group": True,
            }
        )
        # Call name_change to simulate form behavior
        group.name_change()
        self.assertEqual(
            group.name,
            "Test Group",
            "Group name should not include suffix",
        )

    def test_08_suffix_update_triggers_name_change(self):
        """Test that updating suffixes and calling name_change updates name."""
        individual = self.env["res.partner"].create(
            {
                "name": "Temp",  # Required by res_partner_check_name constraint
                "family_name": "Johnson",
                "given_name": "Michael",
                "is_registrant": True,
                "is_group": False,
            }
        )
        # Call name_change to generate name
        individual.name_change()
        self.assertEqual(individual.name, "JOHNSON, MICHAEL")

        # Add suffix and call name_change again
        individual.suffix_ids = [(6, 0, [self.suffix_phd.id])]
        individual.name_change()
        self.assertEqual(
            individual.name,
            "JOHNSON, MICHAEL, PHD",
            "Name should update when suffix is added",
        )

    def test_09_suffix_removal(self):
        """Test that removing suffixes updates the name correctly."""
        individual = self.env["res.partner"].create(
            {
                "name": "Temp",  # Required by res_partner_check_name constraint
                "family_name": "Williams",
                "given_name": "Sarah",
                "suffix_ids": [(6, 0, [self.suffix_jr.id])],
                "is_registrant": True,
                "is_group": False,
            }
        )
        individual.name_change()
        self.assertEqual(individual.name, "WILLIAMS, SARAH, JR.")

        individual.suffix_ids = [(5, 0, 0)]  # Clear all suffixes
        individual.name_change()
        self.assertEqual(
            individual.name,
            "WILLIAMS, SARAH",
            "Name should update when suffixes are removed",
        )

    def test_10_suffix_sequence_ordering(self):
        """Test that suffixes are ordered by sequence field."""
        # PhD has sequence 100, Jr. has sequence 10
        # Even if we add PhD first, Jr. should appear first in the name
        individual = self.env["res.partner"].create(
            {
                "name": "Temp",
                "family_name": "Brown",
                "given_name": "David",
                "suffix_ids": [(6, 0, [self.suffix_phd.id, self.suffix_jr.id])],
                "is_registrant": True,
                "is_group": False,
            }
        )
        individual.name_change()
        self.assertEqual(
            individual.name,
            "BROWN, DAVID, JR., PHD",
            "Suffixes should be ordered by sequence regardless of selection order",
        )

    def test_11_name_get_with_different_code(self):
        """Test name_get when code differs from name."""
        # suffix_jr has name="Jr." and code="JR" (different)
        result = self.suffix_jr.name_get()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], self.suffix_jr.id)
        self.assertEqual(
            result[0][1],
            "Jr. (JR)",
            "name_get should show name with code in parentheses",
        )

    def test_12_name_get_with_same_code(self):
        """Test name_get when code equals name."""
        # Create a suffix where name and code are the same
        suffix_same = self.env["spp.name.suffix"].create(
            {
                "name": "SAME",
                "code": "SAME",
            }
        )
        result = suffix_same.name_get()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], suffix_same.id)
        self.assertEqual(
            result[0][1],
            "SAME",
            "name_get should show only name when code equals name",
        )

    def test_13_name_get_multiple_records(self):
        """Test name_get with multiple records."""
        # Get multiple suffixes at once
        suffixes = self.suffix_jr | self.suffix_phd
        result = suffixes.name_get()
        self.assertEqual(len(result), 2)
        # Check that all record IDs are in the result
        result_ids = [r[0] for r in result]
        self.assertIn(self.suffix_jr.id, result_ids)
        self.assertIn(self.suffix_phd.id, result_ids)
