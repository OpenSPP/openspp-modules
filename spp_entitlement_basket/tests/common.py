from odoo.tests import TransactionCase


class Common(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._test_products = cls.env["product.product"].create(
            [
                {
                    "name": "Flour [TEST]",
                    "detailed_type": "product",
                    "categ_id": cls.env.ref("product.product_category_all").id,
                    "uom_id": cls.env.ref("uom.product_uom_unit").id,
                    "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                },
                {
                    "name": "Food [TEST]",
                    "detailed_type": "product",
                    "categ_id": cls.env.ref("product.product_category_all").id,
                    "uom_id": cls.env.ref("uom.product_uom_unit").id,
                    "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                },
            ]
        )
