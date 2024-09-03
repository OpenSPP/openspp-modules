from odoo.tests.common import TransactionCase


class TestUserRole(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = cls.env["res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "role_line_ids": [
                    (0, 0, {"role_id": cls.env.ref("base.default_user").id}),
                    (0, 0, {"role_id": cls.env.ref("base.group_user").id}),
                ],
            }
        )

    def test_set_groups_from_roles(self):
        result = self.user.set_groups_from_roles()
        self.assertTrue(result)

        result = self.user.set_groups_from_roles(force=True)
        self.assertTrue(result)
