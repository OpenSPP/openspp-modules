from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class MembershipTest(TransactionCase):
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
                "allow_all_member_type": True,
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

    def test_compute_individual_domain(self):
        self.group_membership_1._compute_individual_domain()

        self.assertIsInstance(self.group_membership_1.individual_domain, list)
        self.assertEqual(len(self.group_membership_1.individual_domain), 2)
        self.assertIn(("is_registrant", "=", True), self.group_membership_1.individual_domain)
        self.assertIn(("id", "!=", self.group_membership_1.group.id), self.group_membership_1.individual_domain)

        self.group_1.kind = False
        self.group_membership_1._compute_individual_domain()

        self.assertIsInstance(self.group_membership_1.individual_domain, list)
        self.assertEqual(len(self.group_membership_1.individual_domain), 2)
        self.assertIn(("is_registrant", "=", True), self.group_membership_1.individual_domain)
        self.assertIn(("is_group", "=", False), self.group_membership_1.individual_domain)

    def test_open_member_form(self):
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

        self.registrant_1.is_group = True
        member_form = self.group_membership_1.open_member_form()
        self.assertIsInstance(member_form, dict)
        self.assertEqual(member_form["name"], "Group Membership")
        self.assertEqual(member_form["view_mode"], "form")
        self.assertEqual(member_form["res_model"], "res.partner")
        self.assertEqual(member_form["res_id"], self.registrant_1.id)
        self.assertEqual(member_form["view_id"], self.env.ref("g2p_registry_group.view_groups_form").id)
        self.assertEqual(member_form["type"], "ir.actions.act_window")
        self.assertEqual(member_form["target"], "new")
        self.assertEqual(member_form["context"], {"default_is_group": True})
        self.assertEqual(member_form["flags"], {"mode": "readonly"})

        self.group_membership_1.individual = False
        with self.assertRaisesRegex(UserError, "A group or individual must be speficied for this member."):
            self.group_membership_1.open_member_form()
