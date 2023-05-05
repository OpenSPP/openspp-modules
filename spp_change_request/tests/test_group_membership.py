from odoo.tests import TransactionCase


class SPPGroupMembershipTempTest(TransactionCase):
    def setUp(self):
        super().setUp()
        self._test_individual_1 = self._create_registrant({"name": "Liu Bei"})

        self._group_members = self._create_group_membership(
            {"individual_id": self._test_individual_1.id}
        )

    def _create_registrant(self, vals):
        assert type(vals) == dict
        vals.update({"is_registrant": True})
        return self.env["res.partner"].create(vals)

    def _create_group_membership(self, vals):
        assert type(vals) == dict
        return self.env["spp.change.request.group.members"].create(vals)

    def test_01_open_individual_form(self):
        action = self._group_members.open_individual_form()

        self.assertEqual(action.get("name"), "Individual Member")
