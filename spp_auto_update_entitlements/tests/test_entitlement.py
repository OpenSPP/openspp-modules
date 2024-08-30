from odoo import fields
from odoo.tests.common import TransactionCase


class TestEntitlement(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.program = cls.env["g2p.program"].create({"name": "Test Program"})
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

        cls.cycle = cls.env["g2p.cycle"].create(
            {
                "name": "Test Cycle",
                "program_id": cls.program.id,
                "start_date": fields.Datetime.now(),
                "end_date": fields.Datetime.now(),
            }
        )

        cls.cycle_manager = cls.env["g2p.cycle.manager.default"].create(
            {
                "name": "Test Cycle Manager",
                "program_id": cls.program.id,
            }
        )

        cls.entitlement = cls.env["g2p.entitlement"].create(
            {
                "program_id": cls.program.id,
                "partner_id": cls.partner.id,
                "cycle_id": cls.cycle.id,
                "state": "draft",
                "initial_amount": 100.00,
            }
        )

    def test_compute_balance(self):
        self.entitlement._compute_balance()

        self.assertEqual(self.entitlement.entitlement_balance, self.entitlement.initial_amount)

        self.entitlement_transaction_1 = self.env["spp.entitlement.transactions"].create(
            {
                "entitlement_id": self.entitlement.id,
                "amount_charged_by_service_point": 100.00,
                "transaction_type": "VOID",
                "user_id": self.env.ref("base.user_root").id,
                "transaction_uuid": "test-uuid",
                "currency_id": self.env.ref("base.USD").id,
                "timestamp_transaction_created": fields.Datetime.now(),
            }
        )

        self.assertEqual(
            self.entitlement.entitlement_balance,
            self.entitlement.initial_amount + self.entitlement_transaction_1.amount_charged_by_service_point,
        )

        self.entitlement_transaction_2 = self.env["spp.entitlement.transactions"].create(
            {
                "entitlement_id": self.entitlement.id,
                "amount_charged_by_service_point": 300.00,
                "transaction_type": "PURCHASE",
                "user_id": self.env.ref("base.user_root").id,
                "transaction_uuid": "test-uuid2",
                "currency_id": self.env.ref("base.USD").id,
                "timestamp_transaction_created": fields.Datetime.now(),
            }
        )
        self.assertEqual(
            self.entitlement.entitlement_balance,
            (
                self.entitlement.initial_amount
                + self.entitlement_transaction_1.amount_charged_by_service_point
                - self.entitlement_transaction_2.amount_charged_by_service_point
            ),
        )
