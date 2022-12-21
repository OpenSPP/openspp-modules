# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class EntitlementBasketTest(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(EntitlementBasketTest, cls).setUpClass()

        # Initial Setup of Variables
        cls.group_1 = cls.env["res.partner"].create(
            {
                "name": "Group 1",
                "is_registrant": True,
                "is_group": True,
            }
        )
        cls.group_2 = cls.env["res.partner"].create(
            {
                "name": "Group 2",
                "is_registrant": True,
                "is_group": True,
            }
        )
        cls.group_3 = cls.env["res.partner"].create(
            {
                "name": "Group 3",
                "is_registrant": True,
                "is_group": True,
            }
        )

        # Products
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Flour 1", "type": "product", "list_price": 35.00}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Food 1", "type": "product", "list_price": 62.00}
        )

        # Food Basket
        cls.food_basket = cls.env["spp.entitlement.basket"].create(
            {
                "name": "Food Basket 1",
                "product_ids": [
                    (
                        Command.create(
                            {
                                "product_id": cls.product_1.id,
                                "qty": 5,
                            }
                        )
                    ),
                    (
                        Command.create(
                            {
                                "product_id": cls.product_2.id,
                                "qty": 3,
                            }
                        )
                    ),
                ],
            }
        )

        # Create Program Wizard
        # cls.new_program = cls.env['g2p.program.create.wizard'].create(
        #    {
        #
        #    }
        # )

    def test_01_add_food_basket(self):
        product_names = f"1.) {self.product_1.name} - 5 {self.product_1.uom_id.name}\n"
        product_names += f"2.) {self.product_2.name} - 3 {self.product_2.uom_id.name}\n"

        self.assertEqual(
            self.food_basket.product_names,
            product_names,
            f"Food Basket creation FAILED (EXPECTED {product_names} but RESULT is {self.food_basket.product_names})",
        )
