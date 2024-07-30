from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class CustomFieldsTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """
        Setup and create necessary records for this test
        """
        super().setUpClass()
        cls.model_id = cls.env["ir.model"].search([("model", "=", "res.partner")], limit=1)
        cls.kind_id = cls.env.ref("g2p_registry_membership.group_membership_kind_head")
        cls.model_field_id = cls.env["ir.model.fields"].create(
            {
                "name": "x_test_field",
                "model_id": cls.model_id.id,
                "field_description": "Test Field",
                "draft_name": "test_field",
                "ttype": "char",
                "state": "manual",
                "kinds": [(6, 0, [cls.kind_id.id])],
            }
        )

    def test_open_custom_fields_tree(self):
        action = self.model_field_id.open_custom_fields_tree()

        self.assertEqual(action["name"], "Custom Fields")
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "ir.model.fields")
        self.assertEqual(action["context"]["default_model_id"], self.model_id.id)
        self.assertEqual(action["context"]["default_model"], self.model_id.model)
        self.assertEqual(action["view_mode"], "tree, form")
        self.assertEqual(action["views"][0][0], self.env.ref("spp_custom_fields_ui.view_custom_fields_ui_tree").id)
        self.assertEqual(action["views"][0][1], "tree")
        self.assertEqual(action["views"][1][0], self.env.ref("spp_custom_fields_ui.view_custom_fields_ui_form").id)
        self.assertEqual(action["views"][1][1], "form")
        self.assertEqual(action["domain"], [("model_id", "=", self.model_id.id), ("state", "=", "manual")])

    def test_compute_prefix(self):
        self.model_field_id._compute_prefix()
        self.assertEqual(self.model_field_id.prefix, "x_cst_grp")

    def test_onchange_draft_name(self):
        self.model_field_id._onchange_draft_name()

        self.assertEqual(self.model_field_id.name, "x_cst_grp_test_field")

    def test_onchange_field_category(self):
        self.model_field_id._onchange_field_category()

        self.assertEqual(self.model_field_id.name, "x_cst_grp_test_field")
        self.assertEqual(self.model_field_id.ttype, "char")
        self.assertFalse(self.model_field_id.compute)

    def test_onchange_kinds(self):
        self.model_field_id._onchange_kinds()

        self.assertEqual(self.model_field_id.name, "x_cst_grp_test_field")
        self.assertEqual(self.model_field_id.ttype, "char")
        self.assertFalse(self.model_field_id.compute)

    def test_onchange_target_type(self):
        self.model_field_id._onchange_target_type()

        self.assertEqual(self.model_field_id.name, "x_cst_grp_test_field")
        self.assertEqual(self.model_field_id.ttype, "char")
        self.assertFalse(self.model_field_id.compute)

    def test_onchange_has_presence(self):
        self.model_field_id._onchange_has_presence()

        self.assertEqual(self.model_field_id.name, "x_cst_grp_test_field")
        self.assertEqual(self.model_field_id.ttype, "char")

    def test_set_compute(self):
        self.model_field_id.field_category = "ind"
        with self.assertRaisesRegex(
            UserError, "Changing the type of a field is not yet supported. Please drop it and create it again!"
        ):
            self.model_field_id.set_compute()

        self.model_field_id.has_presence = True
        with self.assertRaisesRegex(
            UserError, "Changing the type of a field is not yet supported. Please drop it and create it again!"
        ):
            self.model_field_id.set_compute()
