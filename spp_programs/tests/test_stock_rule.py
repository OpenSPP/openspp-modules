from odoo.tests import TransactionCase


class TestStockRule(TransactionCase):
    def test_01_get_custom_move_fields(self):
        res = self.env["stock.rule"]._get_custom_move_fields()
        self.assertIn("entitlement_id", res, "`entitlement_id` should be in custom move fields!")
