# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from lxml import etree

from odoo.tests import TransactionCase


class TestCustomField(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Add is_group field if it doesn't exist
        if not cls.env["ir.model.fields"].search([("model", "=", "res.partner"), ("name", "=", "is_group")]):
            cls.env["ir.model.fields"].create(
                {
                    "name": "is_group",
                    "field_description": "Is Group",
                    "model_id": cls.env.ref("base.model_res_partner").id,
                    "ttype": "boolean",
                    "state": "manual",
                }
            )

        # Create test custom fields
        cls.env["ir.model.fields"].create(
            [
                {
                    "name": "x_cst_test_text",
                    "field_description": "Test Custom Text",
                    "model_id": cls.env.ref("base.model_res_partner").id,
                    "ttype": "char",
                    "help": "This is a test custom text field",
                    "state": "manual",
                },
                {
                    "name": "x_cst_test_bool",
                    "field_description": "Test Custom Boolean",
                    "model_id": cls.env.ref("base.model_res_partner").id,
                    "ttype": "boolean",
                    "help": "This is a test custom boolean field",
                    "state": "manual",
                },
                {
                    "name": "x_ind_test_readonly",
                    "field_description": "Test Indicator",
                    "model_id": cls.env.ref("base.model_res_partner").id,
                    "ttype": "char",
                    "help": "This is a test indicator field",
                    "state": "manual",
                },
                {
                    "name": "x_cst_grp_test",
                    "field_description": "Test Group Only Field",
                    "model_id": cls.env.ref("base.model_res_partner").id,
                    "ttype": "char",
                    "help": "This field should only show for groups",
                    "state": "manual",
                },
                {
                    "name": "x_cst_indv_test",
                    "field_description": "Test Individual Only Field",
                    "model_id": cls.env.ref("base.model_res_partner").id,
                    "ttype": "char",
                    "help": "This field should only show for individuals",
                    "state": "manual",
                },
            ]
        )

        # Create base form view with basic_info page
        cls.base_view = cls.env["ir.ui.view"].create(
            {
                "name": "test.res.partner.form",
                "model": "res.partner",
                "type": "form",
                "priority": 1,
                "arch": """
                <form>
                    <sheet>
                        <notebook>
                            <page name="basic_info" string="Basic Info">
                                <group>
                                    <field name="name"/>
                                    <field name="is_group" invisible="1"/>
                                </group>
                            </page>
                        </notebook>
                    </sheet>
                </form>
            """,
            }
        )

        # Create custom field extension view
        cls.extension_view = cls.env["ir.ui.view"].create(
            {
                "name": "test.res.partner.form.custom.extension",
                "model": "res.partner",
                "type": "form",
                "inherit_id": cls.base_view.id,
                "priority": 99,
                "arch": """
                <xpath expr="//page[@name='basic_info']" position="after">
                    <page name="additional_details" string="Additional Details">
                        <div class="row mt16 o_settings_container">
                            <div class="col-12 col-lg-6 o_setting_box">
                                <div class="o_setting_right_pane">
                                    <field name="x_cst_test_text"/>
                                    <field name="x_cst_indv_test" invisible="is_group"/>
                                    <field name="x_cst_grp_test" invisible="not is_group"/>
                                </div>
                            </div>
                            <div class="col-12 col-lg-6 o_setting_box">
                                <div class="o_setting_left_pane">
                                    <field name="x_cst_test_bool"/>
                                </div>
                                <div class="o_setting_right_pane">
                                    <label for="x_cst_test_bool"/>
                                    <div class="text-muted">
                                        <span>This is a test custom boolean field</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </page>
                    <page name="indicators" string="Indicators">
                        <div class="row mt16 o_settings_container">
                            <div class="col-12 col-lg-6 o_setting_box">
                                <div class="o_setting_right_pane">
                                    <field name="x_ind_test_readonly" readonly="1"/>
                                </div>
                            </div>
                        </div>
                    </page>
                </xpath>
            """,
            }
        )

    def _get_form_view(self, is_group=False):
        """Helper method to get form view architecture"""
        # Get the view with the specific view_id and context
        partner_model = self.env["res.partner"].with_context(default_is_group=is_group)
        view = partner_model.get_view(
            view_type="form",
            view_id=self.base_view.id,
        )
        arch = view.get("arch")
        if isinstance(arch, etree._Element):
            return arch
        return etree.fromstring(arch)

    def test_01_view_for_individual(self):
        """Test view generation for individual registrants"""
        arch = self._get_form_view(is_group=False)

        # Test presence of custom pages
        self.assertTrue(arch.xpath("//page[@name='additional_details']"), "Additional Details page should exist")
        self.assertTrue(arch.xpath("//page[@name='indicators']"), "Indicators page should exist")

        # Test individual-specific fields
        indv_fields = arch.xpath("//field[@name='x_cst_indv_test']")
        self.assertTrue(indv_fields, "Individual-only field should be present")

        # Test group-specific fields are not present
        grp_fields = arch.xpath("//field[@name='x_cst_grp_test']")
        self.assertFalse(grp_fields, "Group-only field should not be present")

        # Test indicator fields are readonly
        ind_fields = arch.xpath("//field[@name='x_ind_test_readonly']")
        self.assertTrue(ind_fields, "Indicator field should be present")
        self.assertEqual(ind_fields[0].get("readonly"), "1", "Indicator field should be readonly")

    def test_02_view_for_group(self):
        """Test view generation for group registrants"""
        arch = self._get_form_view(is_group=True)

        # Test group-specific fields
        grp_fields = arch.xpath("//field[@name='x_cst_grp_test']")
        self.assertTrue(grp_fields, "Group-only field should be present")

        # Test individual-specific fields are not present
        indv_fields = arch.xpath("//field[@name='x_cst_indv_test']")
        self.assertFalse(indv_fields, "Individual-only field should not be present")

    def test_03_boolean_field_layout(self):
        """Test boolean field layout in the view"""
        arch = self._get_form_view(is_group=False)

        # Find boolean field
        bool_fields = arch.xpath("//field[@name='x_cst_test_bool']")
        self.assertTrue(bool_fields, "Boolean field should be present")

        # Check if boolean field is in left pane
        bool_field = bool_fields[0]
        parent_div = bool_field.getparent()
        self.assertEqual(
            parent_div.get("class"),
            "o_setting_left_pane",
            "Boolean field should be in left pane",
        )

        # Check if label exists
        field_label = arch.xpath("//label[@for='x_cst_test_bool']")
        self.assertTrue(field_label, "Boolean field should have a label")

    def test_04_help_text_rendering(self):
        """Test help text rendering in the view"""
        arch = self._get_form_view(is_group=False)

        # Find field with help text
        help_divs = arch.xpath("//div[@class='text-muted']/span")
        help_texts = [div.text for div in help_divs]

        # Check if help texts are present
        self.assertIn(
            "This is a test custom text field",
            help_texts,
            "Help text for custom text field should be present",
        )
        self.assertIn(
            "This is a test custom boolean field",
            help_texts,
            "Help text for custom boolean field should be present",
        )

    def test_01_field_creation(self):
        """Test custom field creation"""
        # Check if fields were created
        fields = self.env["ir.model.fields"].search(
            [
                ("model", "=", "res.partner"),
                ("name", "like", "x_cst%"),
            ]
        )
        self.assertTrue(fields, "Custom fields should be created")

        # Check specific fields
        field_names = fields.mapped("name")
        self.assertIn("x_cst_test_text", field_names, "Text field should exist")
        self.assertIn("x_cst_test_bool", field_names, "Boolean field should exist")

    def test_02_field_attributes(self):
        """Test custom field attributes"""
        # Test boolean field
        bool_field = self.env["ir.model.fields"].search(
            [
                ("model", "=", "res.partner"),
                ("name", "=", "x_cst_test_bool"),
            ]
        )
        self.assertEqual(bool_field.ttype, "boolean", "Field should be boolean type")
        self.assertEqual(bool_field.help, "This is a test custom boolean field", "Help text should be set correctly")

        # Test text field
        text_field = self.env["ir.model.fields"].search(
            [
                ("model", "=", "res.partner"),
                ("name", "=", "x_cst_test_text"),
            ]
        )
        self.assertEqual(text_field.ttype, "char", "Field should be char type")
        self.assertEqual(text_field.help, "This is a test custom text field", "Help text should be set correctly")

    def test_03_indicator_field(self):
        """Test indicator field creation and attributes"""
        indicator = self.env["ir.model.fields"].search(
            [
                ("model", "=", "res.partner"),
                ("name", "=", "x_ind_test_readonly"),
            ]
        )
        self.assertTrue(indicator, "Indicator field should exist")
        self.assertEqual(indicator.ttype, "char", "Indicator should be char type")
        self.assertEqual(indicator.help, "This is a test indicator field", "Help text should be set correctly")

    def test_04_group_specific_fields(self):
        """Test group-specific field creation"""
        group_field = self.env["ir.model.fields"].search(
            [
                ("model", "=", "res.partner"),
                ("name", "=", "x_cst_grp_test"),
            ]
        )
        self.assertTrue(group_field, "Group-specific field should exist")
        self.assertEqual(
            group_field.help, "This field should only show for groups", "Help text should be set correctly"
        )

    def test_05_individual_specific_fields(self):
        """Test individual-specific field creation"""
        indv_field = self.env["ir.model.fields"].search(
            [
                ("model", "=", "res.partner"),
                ("name", "=", "x_cst_indv_test"),
            ]
        )
        self.assertTrue(indv_field, "Individual-specific field should exist")
        self.assertEqual(
            indv_field.help, "This field should only show for individuals", "Help text should be set correctly"
        )

    def test_06_field_naming_convention(self):
        """Test field naming conventions"""
        # Test custom fields prefix
        custom_fields = self.env["ir.model.fields"].search(
            [
                ("model", "=", "res.partner"),
                ("name", "like", "x_cst%"),
            ]
        )
        for field in custom_fields:
            self.assertTrue(field.name.startswith("x_cst_"), "Custom fields should start with x_cst_")

        # Test indicator fields prefix
        indicator_fields = self.env["ir.model.fields"].search(
            [
                ("model", "=", "res.partner"),
                ("name", "like", "x_ind%"),
            ]
        )
        for field in indicator_fields:
            self.assertTrue(field.name.startswith("x_ind_"), "Indicator fields should start with x_ind_")

    def test_07_field_model_assignment(self):
        """Test fields are assigned to correct model"""
        all_fields = self.env["ir.model.fields"].search(
            [
                ("model", "=", "res.partner"),
                "|",
                ("name", "like", "x_cst%"),
                ("name", "like", "x_ind%"),
            ]
        )
        for field in all_fields:
            self.assertEqual(field.model_id.model, "res.partner", "Fields should be assigned to res.partner model")
