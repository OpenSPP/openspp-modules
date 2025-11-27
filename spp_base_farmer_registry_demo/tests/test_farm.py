# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestFarm(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.registrant_1 = cls.env["res.partner"].create(
            {
                "family_name": "Butay",
                "given_name": "Red",
                "name": "Red Butay",
                "is_group": False,
                "is_registrant": True,
            }
        )
        cls.kind_1 = cls.env["g2p.group.kind"].create(
            {
                "name": "Test Kind",
            }
        )
        cls.group_1 = cls.env["res.partner"].create(
            {
                "name": "Group 1",
                "is_group": True,
                "is_registrant": True,
                "kind": cls.kind_1.id,
            }
        )
        cls.group_membership_1 = cls.env["g2p.group.membership"].create(
            {
                "group": cls.group_1.id,
                "individual": cls.registrant_1.id,
                "start_date": fields.Datetime.now(),
            }
        )

    def test_01_open_member_form(self):
        """Test opening member form"""
        member_form = self.group_membership_1.open_member_form()

        self.assertIsInstance(member_form, dict)
        self.assertEqual(member_form["name"], "Individual Member")
        self.assertEqual(member_form["view_mode"], "form")
        self.assertEqual(member_form["res_model"], "res.partner")
        self.assertEqual(member_form["res_id"], self.registrant_1.id)
        self.assertEqual(member_form["view_id"], self.env.ref("g2p_registry_individual.view_individuals_form").id)
        self.assertEqual(member_form["type"], "ir.actions.act_window")
        self.assertEqual(member_form["target"], "new")
        self.assertEqual(member_form["context"], {"default_is_group": False})
        self.assertEqual(member_form["flags"], {"mode": "readonly"})

    def test_02_open_member_form_group(self):
        """Test opening member form for group"""
        farm_id = self.env["res.partner"].create(
            {
                "family_name": "Test",
                "given_name": "Head",
                "name": "Test Head",
                "is_group": True,
                "is_registrant": True,
            }
        )

        membership = self.env["g2p.group.membership"].create(
            {
                "group": self.registrant_1.id,
                "individual": farm_id.id,
                "start_date": fields.Datetime.now(),
                "kind": [(4, self.env.ref("g2p_registry_membership.group_membership_kind_head").id)],
            }
        )

        member_form = membership.open_member_form()
        self.assertIsInstance(member_form, dict)
        self.assertEqual(member_form["name"], "Group Membership")
        self.assertEqual(member_form["view_mode"], "form")
        self.assertEqual(member_form["res_model"], "res.partner")
        self.assertEqual(member_form["res_id"], farm_id.id)
        self.assertEqual(member_form["view_id"], self.env.ref("g2p_registry_group.view_groups_form").id)
        self.assertEqual(member_form["type"], "ir.actions.act_window")
        self.assertEqual(member_form["target"], "new")
        self.assertEqual(member_form["context"], {"default_is_group": True})
        self.assertEqual(member_form["flags"], {"mode": "readonly"})

    def test_03_household_size_field_exists(self):
        """Test that household_size field exists on partner"""
        partner = self.env["res.partner"].create(
            {
                "name": "Test Farm Partner",
                "is_group": True,
                "is_registrant": True,
            }
        )

        self.assertIn("household_size", partner._fields)

    def test_04_household_size_can_be_set(self):
        """Test that household_size can be set and retrieved"""
        partner = self.env["res.partner"].create(
            {
                "name": "Test Farm Household",
                "is_group": True,
                "is_registrant": True,
                "household_size": 5,
            }
        )

        self.assertEqual(partner.household_size, 5)

    def test_05_household_size_can_be_updated(self):
        """Test that household_size can be updated"""
        partner = self.env["res.partner"].create(
            {
                "name": "Test Farm Update",
                "is_group": True,
                "is_registrant": True,
                "household_size": 3,
            }
        )

        partner.write({"household_size": 7})
        self.assertEqual(partner.household_size, 7)

    def test_06_household_size_filter(self):
        """Test filtering by household_size"""
        partner1 = self.env["res.partner"].create(
            {
                "name": "Farm 1",
                "is_group": True,
                "is_registrant": True,
                "household_size": 5,
            }
        )

        partner2 = self.env["res.partner"].create(
            {
                "name": "Farm 2",
                "is_group": True,
                "is_registrant": True,
                "household_size": 10,
            }
        )

        # Test filtering
        found = self.env["res.partner"].search([("household_size", "=", 5)])
        self.assertIn(partner1, found)
        self.assertNotIn(partner2, found)

    def test_07_household_size_default_value(self):
        """Test household_size default value"""
        partner = self.env["res.partner"].create(
            {
                "name": "Test Farm Default",
                "is_group": True,
                "is_registrant": True,
            }
        )

        # Default should be 0 or False
        self.assertIn(partner.household_size, [0, False])

    def test_08_household_size_various_values(self):
        """Test household_size with various values"""
        test_values = [0, 1, 5, 10, 20, 50, 100]

        for value in test_values:
            partner = self.env["res.partner"].create(
                {
                    "name": f"Farm Size {value}",
                    "is_group": True,
                    "is_registrant": True,
                    "household_size": value,
                }
            )
            self.assertEqual(partner.household_size, value)

    def test_09_household_size_search_operators(self):
        """Test household_size search with different operators"""
        # Create test data
        self.env["res.partner"].create(
            {
                "name": "Small Farm",
                "is_group": True,
                "is_registrant": True,
                "household_size": 2,
            }
        )
        self.env["res.partner"].create(
            {
                "name": "Medium Farm",
                "is_group": True,
                "is_registrant": True,
                "household_size": 5,
            }
        )
        self.env["res.partner"].create(
            {
                "name": "Large Farm",
                "is_group": True,
                "is_registrant": True,
                "household_size": 10,
            }
        )

        # Test greater than
        large = self.env["res.partner"].search([("household_size", ">", 5)])
        self.assertGreaterEqual(len(large), 1)

        # Test less than
        small = self.env["res.partner"].search([("household_size", "<", 5)])
        self.assertGreaterEqual(len(small), 1)

        # Test range
        medium = self.env["res.partner"].search([("household_size", ">=", 2), ("household_size", "<=", 10)])
        self.assertGreaterEqual(len(medium), 3)

    def test_10_household_size_on_individual(self):
        """Test household_size field on individual (non-group) partner"""
        individual = self.env["res.partner"].create(
            {
                "name": "Individual Farmer",
                "is_group": False,
                "is_registrant": True,
                "household_size": 4,
            }
        )

        # Field should work on individuals too
        self.assertEqual(individual.household_size, 4)

    def test_11_household_size_bulk_update(self):
        """Test bulk updating household_size"""
        partners = self.env["res.partner"].create(
            [
                {
                    "name": "Farm A",
                    "is_group": True,
                    "is_registrant": True,
                    "household_size": 5,
                },
                {
                    "name": "Farm B",
                    "is_group": True,
                    "is_registrant": True,
                    "household_size": 5,
                },
            ]
        )

        # Bulk update
        partners.write({"household_size": 8})

        for partner in partners:
            self.assertEqual(partner.household_size, 8)

    def test_12_household_size_with_members(self):
        """Test household_size field with actual group members"""
        farm = self.env["res.partner"].create(
            {
                "name": "Farm with Members",
                "is_group": True,
                "is_registrant": True,
                "household_size": 0,
            }
        )

        # Create members
        member1 = self.env["res.partner"].create(
            {
                "name": "Member 1",
                "is_group": False,
                "is_registrant": True,
            }
        )
        member2 = self.env["res.partner"].create(
            {
                "name": "Member 2",
                "is_group": False,
                "is_registrant": True,
            }
        )

        # Add members to group
        self.env["g2p.group.membership"].create(
            {
                "group": farm.id,
                "individual": member1.id,
            }
        )
        self.env["g2p.group.membership"].create(
            {
                "group": farm.id,
                "individual": member2.id,
            }
        )

        # Set household_size to match actual members
        farm.write({"household_size": 2})
        self.assertEqual(farm.household_size, 2)

    def test_13_household_size_integer_field_type(self):
        """Test that household_size is an integer field"""
        partner = self.env["res.partner"].create(
            {
                "name": "Type Test Farm",
                "is_group": True,
                "is_registrant": True,
            }
        )

        field = partner._fields["household_size"]
        self.assertEqual(field.type, "integer")
