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
                "target_type": "grp",
                "field_group_id": self.group_field_group.id,
                "sequence": 5,
            }
        )

        self.assertEqual(field.field_group_id, self.group_field_group)
        self.assertEqual(field.target_type, "grp")
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
                "target_type": "indv",
                "field_group_id": self.individual_field_group.id,
                "sequence": 15,
            }
        )

        self.assertEqual(field.field_group_id, self.individual_field_group)
        self.assertEqual(field.target_type, "indv")

    def test_05_target_type_mismatch_cleared_on_change(self):
        """Test field_group_id is cleared when target_type changes"""
        field = self.field_model.create(
            {
                "name": "x_cst_grp_test_field",
                "model_id": self.partner_model.id,
                "field_description": "Test Field",
                "ttype": "char",
                "state": "manual",
                "target_type": "grp",
                "field_group_id": self.group_field_group.id,
            }
        )

        # Change target type - should clear field_group_id
        field.target_type = "indv"
        field._onchange_target_type()

        self.assertFalse(field.field_group_id)

    def test_06_field_group_domain_filtering(self):
        """Test domain filtering ensures correct field group types"""
        # Create a group field
        group_field = self.field_model.create(
            {
                "name": "x_cst_grp_test_domain",
                "model_id": self.partner_model.id,
                "field_description": "Test Domain Field",
                "ttype": "char",
                "state": "manual",
                "target_type": "grp",
            }
        )

        # Get available field groups for this field (simulate domain)
        available_groups = self.field_group_model.search([("target_type", "=", group_field.target_type)])

        # Should only include group-type field groups
        self.assertIn(self.group_field_group, available_groups)
        self.assertNotIn(self.individual_field_group, available_groups)

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
