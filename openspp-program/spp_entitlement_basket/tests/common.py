from odoo.tests import TransactionCase


class Common(TransactionCase):
    def setUp(self):
        super().setUp()
        self._test_products = self.env["product.product"].create(
            [
                {
                    "name": "Flour [TEST]",
                    "detailed_type": "product",
                    "categ_id": self.env.ref("product.product_category_all").id,
                    "uom_id": self.env.ref("uom.product_uom_unit").id,
                    "uom_po_id": self.env.ref("uom.product_uom_unit").id,
                },
                {
                    "name": "Food [TEST]",
                    "detailed_type": "product",
                    "categ_id": self.env.ref("product.product_category_all").id,
                    "uom_id": self.env.ref("uom.product_uom_unit").id,
                    "uom_po_id": self.env.ref("uom.product_uom_unit").id,
                },
            ]
        )
