# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase


class TestFieldGroup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.field_group_model = cls.env["spp.custom.field.group"]
        cls.field_model = cls.env["ir.model.fields"]
        cls.partner_model = cls.env["ir.model"].search([("model", "=", "res.partner")], limit=1)

        # Create field groups
        cls.group_field_group = cls.field_group_model.create(
            {
                "name": "Household Information",
                "target_type": "grp",
                "sequence": 10,
                "description": "Fields related to household data",
            }
        )

        cls.individual_field_group = cls.field_group_model.create(
            {
                "name": "Personal Information",
                "target_type": "indv",
                "sequence": 20,
                "description": "Fields related to individual data",
            }
        )

    def test_01_create_field_group(self):
        """Test field group creation with proper attributes"""
        self.assertEqual(self.group_field_group.name, "Household Information")
        self.assertEqual(self.group_field_group.target_type, "grp")
        self.assertEqual(self.group_field_group.sequence, 10)
        self.assertTrue(self.group_field_group.active)

    def test_02_field_group_ordering(self):
        """Test field groups are ordered by sequence"""
        groups = self.field_group_model.search([])
        self.assertGreater(len(groups), 0)
        # Verify default ordering by sequence
        for i in range(len(groups) - 1):
            self.assertLessEqual(groups[i].sequence, groups[i + 1].sequence)

    def test_03_field_group_assignment_to_group_field(self):
        """Test assigning field group to a group-type field"""
        field = self.field_model.create(
            {
                "name": "x_cst_grp_household_size",
                "model_id": self.partner_model.id,
                "field_description": "Household Size",
                "ttype": "integer",
                "state": "manual",
                "field_group_id": self.group_field_group.id,
                "sequence": 5,
            }
        )

        self.assertEqual(field.field_group_id, self.group_field_group)
        self.assertEqual(field.sequence, 5)

    def test_04_field_group_assignment_to_individual_field(self):
        """Test assigning field group to an individual-type field"""
        field = self.field_model.create(
            {
                "name": "x_cst_indv_education_level",
                "model_id": self.partner_model.id,
                "field_description": "Education Level",
                "ttype": "char",
                "state": "manual",
                "field_group_id": self.individual_field_group.id,
                "sequence": 15,
            }
        )

        self.assertEqual(field.field_group_id, self.individual_field_group)

    def test_05_field_sequence_ordering(self):
        """Test fields can be ordered by sequence"""
        field1 = self.field_model.create(
            {
                "name": "x_cst_grp_test_field_1",
                "model_id": self.partner_model.id,
                "field_description": "Test Field 1",
                "ttype": "char",
                "state": "manual",
                "field_group_id": self.group_field_group.id,
                "sequence": 5,
            }
        )
        field2 = self.field_model.create(
            {
                "name": "x_cst_grp_test_field_2",
                "model_id": self.partner_model.id,
                "field_description": "Test Field 2",
                "ttype": "char",
                "state": "manual",
                "field_group_id": self.group_field_group.id,
                "sequence": 10,
            }
        )

        self.assertLess(field1.sequence, field2.sequence)

    def test_06_field_group_domain_filtering_by_target_type(self):
        """Test field groups can be filtered by target_type"""
        # Get group-type field groups
        group_type_groups = self.field_group_model.search([("target_type", "=", "grp")])

        # Should only include group-type field groups
        self.assertIn(self.group_field_group, group_type_groups)
        self.assertNotIn(self.individual_field_group, group_type_groups)

        # Get individual-type field groups
        indv_type_groups = self.field_group_model.search([("target_type", "=", "indv")])

        # Should only include individual-type field groups
        self.assertIn(self.individual_field_group, indv_type_groups)
        self.assertNotIn(self.group_field_group, indv_type_groups)

    def test_07_inactive_field_group(self):
        """Test inactive field groups"""
        inactive_group = self.field_group_model.create(
            {
                "name": "Inactive Group",
                "target_type": "grp",
                "active": False,
            }
        )

        self.assertFalse(inactive_group.active)

        # Search with default domain should not include inactive
        active_groups = self.field_group_model.search([("target_type", "=", "grp"), ("active", "=", True)])
        self.assertNotIn(inactive_group, active_groups)
