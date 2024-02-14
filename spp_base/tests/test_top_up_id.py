from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase
from odoo.tools import mute_logger


class TestTopUpID(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        vals = {"name": "Test Group 1", "is_group": True, "is_registrant": True}
        cls.test_group = cls.env["res.partner"].create(vals)

    @mute_logger("py.warnings")
    def test_01_create_and_check_error(self):
        vals = {
            "id_type": self.env.ref("spp_base.id_top_up_card").id,
            "card_uid": 123456789,
        }
        with self.assertRaisesRegex(ValidationError, "Top-up Card UID should have 10 characters"):
            self.test_group.write({"reg_ids": [(0, 0, vals)]})
