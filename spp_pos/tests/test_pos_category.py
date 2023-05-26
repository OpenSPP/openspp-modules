from odoo.tests import TransactionCase


class TestPosCateg(TransactionCase):
    def test_01_get_entitlement_categ(self):
        res = self.env["pos.category"].get_entitlement_categ()
        self.assertEqual(
            res,
            self.env.ref("spp_pos.entitlement_product_categ_pos").id,
            "Should return correct pos category!",
        )
