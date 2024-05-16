from odoo.tests import TransactionCase


class TestProductTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_get_is_locked(self):
        product_id = self.env.ref("spp_pos.entitlement_product")

        self.assertEqual(product_id.get_is_locked(), {"is_locked": product_id.is_locked})
        self.assertTrue(product_id.get_is_locked()["is_locked"])

    def test_get_entitlement_product(self):
        product_id = self.env.ref("spp_pos.entitlement_product")

        self.assertEqual(product_id.get_entitlement_product(), product_id.id)
