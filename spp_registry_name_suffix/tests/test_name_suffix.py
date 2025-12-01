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

    def test_03_name_with_suffix(self):
        """Test that suffix is appended to the computed name."""
        individual = self.env["res.partner"].create(
            {
                "family_name": "Doe",
                "given_name": "John",
                "suffix_id": self.suffix_jr.id,
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

    def test_05_name_with_all_fields(self):
        """Test name with all fields including addl_name and suffix."""
        individual = self.env["res.partner"].create(
            {
                "family_name": "Smith",
                "given_name": "Robert",
                "addl_name": "James",
                "suffix_id": self.suffix_phd.id,
                "is_registrant": True,
                "is_group": False,
            }
        )
        individual.name_change()
        self.assertEqual(
            individual.name,
            "SMITH, ROBERT JAMES, PHD",
            "Name should include all parts including suffix",
        )

    def test_06_group_name_unaffected(self):
        """Test that group name is not affected by suffix logic."""
        group = self.env["res.partner"].create(
            {
                "name": "Test Group",
                "suffix_id": self.suffix_jr.id,
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

    def test_07_suffix_update_triggers_name_change(self):
        """Test that updating suffix and calling name_change updates name."""
        individual = self.env["res.partner"].create(
            {
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
        individual.suffix_id = self.suffix_phd.id
        individual.name_change()
        self.assertEqual(
            individual.name,
            "JOHNSON, MICHAEL, PHD",
            "Name should update when suffix is added",
        )

    def test_08_suffix_removal(self):
        """Test that removing suffix updates the name correctly."""
        individual = self.env["res.partner"].create(
            {
                "family_name": "Williams",
                "given_name": "Sarah",
                "suffix_id": self.suffix_jr.id,
                "is_registrant": True,
                "is_group": False,
            }
        )
        individual.name_change()
        self.assertEqual(individual.name, "WILLIAMS, SARAH, JR.")

        individual.suffix_id = False
        individual.name_change()
        self.assertEqual(
            individual.name,
            "WILLIAMS, SARAH",
            "Name should update when suffix is removed",
        )
