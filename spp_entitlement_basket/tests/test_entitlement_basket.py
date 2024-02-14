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
        super().setUpClass()

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
        cls.product_1 = cls.env["product.product"].create({"name": "Flour 1", "type": "product", "list_price": 35.00})
        cls.product_2 = cls.env["product.product"].create({"name": "Food 1", "type": "product", "list_price": 62.00})

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

        # Create Program Wizard (do not automatically generate beneficiaries)
        cls.new_program_nogen = cls.env["g2p.program.create.wizard"].create(
            {
                "name": "Food Basket",
                "currency_id": cls.env.user.company_id.currency_id.id,
                "auto_approve_entitlements": True,
                "cycle_duration": 30,
                "approver_group_id": cls.env.ref("g2p_registry_base.group_g2p_admin").id,
                "entitlement_validation_group_id": cls.env.ref("g2p_registry_base.group_g2p_admin").id,
                "import_beneficiaries": "no",  # Do not import beneficiaries
                "state": "step1",  # Do not proceed to step 2 (generate beneficiaries)
            }
        )

    def test_01_add_food_basket(self):
        product_names = f"1.) {self.product_1.name} - 5 {self.product_1.uom_id.name}\n"
        product_names += f"2.) {self.product_2.name} - 3 {self.product_2.uom_id.name}\n"

        self.assertEqual(
            self.food_basket.product_names,
            product_names,
            f"Food Basket creation FAILED (EXPECTED {product_names} but RESULT is {self.food_basket.product_names})",
        )

    # def test_01_create_program_nogen(self):
    #    new_program = self.new_program_nogen.update({
    #        'entitlement_kind': 'basket_entitlement',
    #        'entitlement_basket_id':
    #    })
