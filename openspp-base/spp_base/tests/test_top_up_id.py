from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestTopUpID(TransactionCase):
    def setUp(self):
        super().setUp()
        vals = {"name": "Test Group 1", "is_group": True, "is_registrant": True}
        self.test_group = self.env["res.partner"].create(vals)

    def test_01_create_and_check_error(self):
        vals = {
            "id_type": self.env.ref("spp_base.id_top_up_card").id,
            "card_uid": 123456789,
        }
        with self.assertRaisesRegex(
            ValidationError, "Top-up Card UID should have 10 characters"
        ):
            self.test_group.write([0, 0, vals])
