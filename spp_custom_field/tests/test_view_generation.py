# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from lxml import etree

from odoo.tests.common import TransactionCase


class TestViewGeneration(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.field_model = cls.env["ir.model.fields"]
        cls.field_group_model = cls.env["spp.custom.field.group"]
        cls.res_partner_model = cls.env["ir.model"].search([("model", "=", "res.partner")], limit=1)

        # Create field groups
        cls.household_group = cls.field_group_model.create(
            {
                "name": "Household Info",
                "target_type": "grp",
                "sequence": 10,
            }
        )

        cls.demographics_group = cls.field_group_model.create(
            {
                "name": "Demographics",
                "target_type": "grp",
                "sequence": 20,
            }
        )

        # Create custom fields with groups
        cls.field_model.create(
            {
                "name": "x_cst_grp_household_size",
                "model_id": cls.res_partner_model.id,
                "field_description": "Household Size",
                "ttype": "integer",
                "state": "manual",
                "field_group_id": cls.household_group.id,
                "sequence": 5,
            }
        )

        cls.field_model.create(
            {
                "name": "x_cst_grp_location",
                "model_id": cls.res_partner_model.id,
                "field_description": "Location",
                "ttype": "char",
                "state": "manual",
                "field_group_id": cls.demographics_group.id,
                "sequence": 15,
            }
        )

        # Create indicator field with group
        cls.field_model.create(
            {
                "name": "x_ind_grp_member_count",
                "model_id": cls.res_partner_model.id,
                "field_description": "Member Count",
                "ttype": "integer",
                "state": "manual",
                "field_group_id": cls.household_group.id,
                "sequence": 25,
            }
        )

    def test_01_group_fields_by_group(self):
        """Test grouping fields by field_group_id"""
        fields = self.field_model.search(
            [
                ("model_id", "=", self.res_partner_model.id),
                ("name", "in", ["x_cst_grp_household_size", "x_cst_grp_location"]),
            ]
        )

        partner = self.partner_model.create({"name": "Test", "is_group": True})
        grouped = partner._group_fields_by_group(fields)

        # Should have 2 groups
        self.assertEqual(len(grouped), 2)

        # Check groups are present
        group_ids = [g[0].id if g[0] else None for g in grouped]
        self.assertIn(self.household_group.id, group_ids)
        self.assertIn(self.demographics_group.id, group_ids)

    def test_02_fields_ordered_by_sequence(self):
        """Test fields within groups are ordered by sequence"""
        # Create multiple fields in same group with different sequences
        self.field_model.create(
            {
                "name": "x_cst_grp_field_a",
                "model_id": self.res_partner_model.id,
                "field_description": "Field A",
                "ttype": "char",
                "state": "manual",
                "field_group_id": self.household_group.id,
                "sequence": 30,
            }
        )
        self.field_model.create(
            {
                "name": "x_cst_grp_field_b",
                "model_id": self.res_partner_model.id,
                "field_description": "Field B",
                "ttype": "char",
                "state": "manual",
                "field_group_id": self.household_group.id,
                "sequence": 10,
            }
        )

        fields = self.field_model.search(
            [
                ("model_id", "=", self.res_partner_model.id),
                ("field_group_id", "=", self.household_group.id),
                ("name", "in", ["x_cst_grp_field_a", "x_cst_grp_field_b"]),
            ]
        )

        partner = self.partner_model.create({"name": "Test", "is_group": True})
        grouped = partner._group_fields_by_group(fields)

        # Find the household group
        for group_record, fields_in_group in grouped:
            if group_record and group_record.id == self.household_group.id:
                # Check fields are ordered by sequence
                sequences = [f.sequence for f in fields_in_group]
                self.assertEqual(sequences, sorted(sequences))
                break

    def test_03_ungrouped_fields_placed_separately(self):
        """Test fields without group are placed separately"""
        # Create field without group
        self.field_model.create(
            {
                "name": "x_cst_grp_no_group",
                "model_id": self.res_partner_model.id,
                "field_description": "No Group Field",
                "ttype": "char",
                "state": "manual",
                "sequence": 100,
            }
        )

        fields = self.field_model.search(
            [
                ("model_id", "=", self.res_partner_model.id),
                ("name", "=", "x_cst_grp_no_group"),
            ]
        )

        partner = self.partner_model.create({"name": "Test", "is_group": True})
        grouped = partner._group_fields_by_group(fields)

        # Should have ungrouped section (group_record=None)
        has_ungrouped = any(g[0] is None for g in grouped)
        self.assertTrue(has_ungrouped)

    def test_04_view_generation_creates_elements(self):
        """Test that view generation creates proper XML elements"""
        partner = self.partner_model.create({"name": "Test Group", "is_group": True})

        # Get the form view (simplified test - just check it doesn't error)
        try:
            # This will trigger _get_view which processes custom fields
            view = self.env["ir.ui.view"].search([("model", "=", "res.partner"), ("type", "=", "form")], limit=1)
            if view:
                arch, _ = partner._get_view(view_id=view.id, view_type="form")
                # Basic check that arch is valid XML
                self.assertIsInstance(arch, etree._Element)
        except Exception as e:
            self.fail(f"View generation failed: {str(e)}")

    def test_05_group_ordering_by_sequence(self):
        """Test that field groups are ordered by sequence"""
        partner = self.partner_model.create({"name": "Test", "is_group": True})

        # Get all fields
        fields = self.field_model.search(
            [
                ("model_id", "=", self.res_partner_model.id),
                ("field_group_id", "!=", False),
            ]
        )

        grouped = partner._group_fields_by_group(fields)

        # Extract group sequences (excluding None)
        group_sequences = []
        for group_record, _ in grouped:
            if group_record:
                group_sequences.append(group_record.sequence)

        # Check groups are ordered by sequence
        self.assertEqual(group_sequences, sorted(group_sequences))
