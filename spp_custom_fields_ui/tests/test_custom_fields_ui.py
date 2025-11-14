from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestCustomFieldsUI(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_id = cls.env["ir.model"].search([("model", "=", "res.partner")], limit=1)
        cls.field_model = cls.env["ir.model.fields"]
        cls.kind_head = cls.env.ref("g2p_registry_membership.group_membership_kind_head")

        # Create field group for testing
        cls.field_group = cls.env["spp.custom.field.group"].create(
            {
                "name": "Test Group",
                "target_type": "grp",
                "sequence": 10,
            }
        )

    def test_01_compute_prefix_custom_group(self):
        """Test prefix computation for custom group field"""
        field = self.field_model.create(
            {
                "name": "x_temp",
                "model_id": self.model_id.id,
                "field_description": "Test Field",
                "ttype": "char",
                "state": "manual",
                "target_type": "grp",
                "field_category": "cst",
            }
        )
        field._compute_prefix()
        self.assertEqual(field.prefix, "x_cst_grp")

    def test_02_compute_prefix_indicator_individual(self):
        """Test prefix computation for indicator individual field"""
        field = self.field_model.create(
            {
                "name": "x_temp",
                "model_id": self.model_id.id,
                "field_description": "Test Indicator",
                "ttype": "integer",
                "state": "manual",
                "target_type": "indv",
                "field_category": "ind",
            }
        )
        field._compute_prefix()
        self.assertEqual(field.prefix, "x_ind_indv")

    def test_03_onchange_draft_name_generates_field_name(self):
        """Test that draft name generates proper field name"""
        field = self.field_model.create(
            {
                "name": "x_temp",
                "model_id": self.model_id.id,
                "field_description": "Test Field",
                "ttype": "char",
                "state": "manual",
                "target_type": "grp",
                "field_category": "cst",
                "draft_name": "household_size",
            }
        )
        field._onchange_draft_name()
        self.assertEqual(field.name, "x_cst_grp_household_size")

    def test_04_indicator_field_with_kinds(self):
        """Test indicator field with membership kinds"""
        field = self.field_model.create(
            {
                "name": "x_temp",
                "model_id": self.model_id.id,
                "field_description": "Number of Heads",
                "draft_name": "num_heads",
                "ttype": "integer",
                "state": "manual",
                "target_type": "grp",
                "field_category": "ind",
                "kinds": [(6, 0, [self.kind_head.id])],
            }
        )
        field._onchange_draft_name()

        self.assertEqual(field.name, "x_ind_grp_num_heads")
        self.assertTrue(field.compute)
        self.assertIn(self.kind_head.name, field.compute)
        self.assertIn("compute_count_and_set_indicator", field.compute)

    def test_05_presence_field_creates_boolean(self):
        """Test that presence field creates boolean type"""
        field = self.field_model.create(
            {
                "name": "x_ind_indv_has_disability",
                "model_id": self.model_id.id,
                "field_description": "Has Disability",
                "draft_name": "has_disability",
                "ttype": "boolean",
                "state": "manual",
                "target_type": "indv",
                "field_category": "ind",
                "has_presence": True,
            }
        )
        field.set_compute()

        self.assertEqual(field.ttype, "boolean")
        self.assertTrue(field.compute)
        self.assertIn("presence_only=True", field.compute)

    def test_06_calculated_field_without_presence_creates_integer(self):
        """Test that calculated field without presence is integer"""
        field = self.field_model.create(
            {
                "name": "x_ind_grp_member_count",
                "model_id": self.model_id.id,
                "field_description": "Member Count",
                "draft_name": "member_count",
                "ttype": "integer",
                "state": "manual",
                "target_type": "grp",
                "field_category": "ind",
                "has_presence": False,
            }
        )
        field.set_compute()

        self.assertEqual(field.ttype, "integer")
        self.assertTrue(field.compute)
        self.assertIn("compute_count_and_set_indicator", field.compute)

    def test_07_field_group_assignment(self):
        """Test field can be assigned to field group"""
        field = self.field_model.create(
            {
                "name": "x_cst_grp_test_grouped",
                "model_id": self.model_id.id,
                "field_description": "Grouped Field",
                "ttype": "char",
                "state": "manual",
                "target_type": "grp",
                "field_category": "cst",
                "field_group_id": self.field_group.id,
            }
        )

        self.assertEqual(field.field_group_id, self.field_group)

    def test_08_sequence_field(self):
        """Test sequence field for ordering"""
        field1 = self.field_model.create(
            {
                "name": "x_cst_grp_field1",
                "model_id": self.model_id.id,
                "field_description": "Field 1",
                "ttype": "char",
                "state": "manual",
                "sequence": 5,
            }
        )
        field2 = self.field_model.create(
            {
                "name": "x_cst_grp_field2",
                "model_id": self.model_id.id,
                "field_description": "Field 2",
                "ttype": "char",
                "state": "manual",
                "sequence": 10,
            }
        )

        self.assertEqual(field1.sequence, 5)
        self.assertEqual(field2.sequence, 10)
        self.assertLess(field1.sequence, field2.sequence)

    def test_09_set_compute_error_on_type_change(self):
        """Test error when trying to change field type"""
        field = self.field_model.create(
            {
                "name": "x_cst_grp_test_change",
                "model_id": self.model_id.id,
                "field_description": "Test Change",
                "ttype": "char",
                "state": "manual",
                "field_category": "cst",
            }
        )

        # Try to change to indicator (different type)
        field.field_category = "ind"
        with self.assertRaisesRegex(
            UserError,
            "Changing the type of a field is not yet supported",
        ):
            field.set_compute()
