from .common import Common


class TestFoodBasket(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._test_entitlement_basket = cls.env["spp.entitlement.basket"].create(
            {
                "name": "Basket 1 [TEST]",
                "product_ids": [
                    (
                        0,
                        0,
                        {"product_id": cls._test_products[0].id},
                    ),
                    (
                        0,
                        0,
                        {"product_id": cls._test_products[-1].id},
                    ),
                ],
            }
        )

    def test_01_compute_product_names(self):
        result_product_names = "1.) Flour [TEST] - 1 Units" + "\n" + "2.) Food [TEST] - 1 Units" + "\n"
        self.assertEqual(
            self._test_entitlement_basket.product_names,
            result_product_names,
            "Product names should contains all products and its units!",
        )
