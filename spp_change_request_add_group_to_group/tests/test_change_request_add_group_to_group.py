from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestChangeRequestAddGroupToGroup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test groups
        cls.parent_group = cls.env["res.partner"].create(
            {
                "name": "Parent Group",
                "is_registrant": True,
                "is_group": True,
            }
        )

        cls.child_group = cls.env["res.partner"].create(
            {
                "name": "Child Group",
                "is_registrant": True,
                "is_group": True,
            }
        )

        # Create test role
        cls.role = cls.env["g2p.group.membership.kind"].create({"name": "Member"})

        # Create base change request
        cls.change_request = cls.env["spp.change.request"].create(
            {
                "request_type": "spp.change.request.add.group.to.group",
            }
        )

        # Create add group to group change request
        cls.add_group_to_group_request = cls.env["spp.change.request.add.group.to.group"].create(
            {
                "change_request_id": cls.change_request.id,
                "registrant_id": cls.parent_group.id,
            }
        )

    def test_selection_request_type_ref_id(self):
        """Test the request type selection includes 'Add Group to a Group'"""
        selection = self.env["spp.change.request"]._selection_request_type_ref_id()
        self.assertIn(("spp.change.request.add.group.to.group", "Add Group to a Group"), selection)

    def test_check_phone_exist(self):
        """Test phone validation"""
        # Should pass with phone
        self.change_request._check_phone_exist()

    def test_onchange_registrant_id(self):
        """Test registrant change clears group members"""
        # Create test group member
        member = self.env["spp.change.request.group.members"].create(
            {
                "group_add_group_to_group_id": self.add_group_to_group_request.id,
                "individual_id": self.child_group.id,
                "kind_ids": [(4, self.role.id)],
                "start_date": date.today(),
            }
        )
        self.add_group_to_group_request.group_member_ids = member

        # Change registrant
        new_group = self.env["res.partner"].create(
            {
                "name": "New Group",
                "is_registrant": True,
                "is_group": True,
            }
        )
        self.add_group_to_group_request.registrant_id = new_group
        self.add_group_to_group_request._onchange_registrant_id()

        # Check group members cleared
        self.assertFalse(self.add_group_to_group_request.group_member_ids)
        self.assertEqual(self.add_group_to_group_request.change_request_id.registrant_id.id, new_group.id)

    def test_validate_data(self):
        """Test data validation"""
        # Should fail without group members
        with self.assertRaises(ValidationError) as cm:
            self.add_group_to_group_request.validate_data()
        self.assertIn("Need to add at least one farmer!", str(cm.exception))

        # Should pass with group members
        member = self.env["spp.change.request.group.members"].create(
            {
                "group_add_group_to_group_id": self.add_group_to_group_request.id,
                "individual_id": self.child_group.id,
                "kind_ids": [(4, self.role.id)],
                "start_date": date.today(),
            }
        )
        self.add_group_to_group_request.group_member_ids = member
        self.add_group_to_group_request.validate_data()

    def test_update_live_data(self):
        """Test updating live data"""
        # Add group member
        member = self.env["spp.change.request.group.members"].create(
            {
                "group_add_group_to_group_id": self.add_group_to_group_request.id,
                "individual_id": self.child_group.id,
                "kind_ids": [(4, self.role.id)],
                "start_date": date.today(),
            }
        )
        self.add_group_to_group_request.group_member_ids = member

        # Update live data
        self.add_group_to_group_request.update_live_data()

        # Check membership created
        membership = self.env["g2p.group.membership"].search(
            [("group", "=", self.parent_group.id), ("individual", "=", self.child_group.id)]
        )
        self.assertTrue(membership)
        self.assertEqual(membership.kind.ids, self.role.ids)
        self.assertEqual(membership.start_date.date(), date.today())

    def test_open_registrant_details_form(self):
        """Test opening registrant details form"""
        action = self.add_group_to_group_request.open_registrant_details_form()

        self.assertEqual(action["res_id"], self.parent_group.id)
        self.assertEqual(action["target"], "new")
        self.assertFalse(action["context"]["create"])
        self.assertFalse(action["context"]["edit"])
        self.assertEqual(action["context"]["hide_from_cr"], 1)
        self.assertEqual(action["flags"]["mode"], "readonly")
