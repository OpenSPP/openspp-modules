from odoo.tests import TransactionCase


class Common(TransactionCase):
    def setUp(self):
        super().setUp()
        self._test_partner = self.env["res.partner"].create(
            {
                "name": "Cao Cao",
                "is_registrant": True,
            }
        )
