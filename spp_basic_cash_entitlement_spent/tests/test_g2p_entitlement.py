from odoo import fields
from odoo.tests import TransactionCase


class TestG2pEntitlement(TransactionCase):
    def setUp(self):
        super().setUp()
        self.registrant = self.env["res.partner"].create(
            {
                "name": "Registrant 1 [TEST]",
                "is_registrant": True,
                "is_group": True,
            }
        )
        self.program = self.env["g2p.program"].create(
            {
                "name": "Program 1 [TEST]",
                "program_membership_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": self.registrant.id,
                            "state": "enrolled",
                        },
                    ),
                ],
            }
        )
        self.program.create_journal()
        self.cycle = self.env["g2p.cycle"].create(
            {
                "name": "Cycle 1 [TEST]",
                "program_id": self.program.id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today(),
            }
        )
        self._test_entitlement = self.env["g2p.entitlement"].create(
            {
                "partner_id": self.registrant.id,
                "cycle_id": self.cycle.id,
                "valid_from": fields.Date.today(),
                "initial_amount": 5.0,
                "spent_amount": 3.0,
            }
        )

    def test_01_compute_balance(self):
        self.assertEqual(
            self._test_entitlement.balance,
            2.0,
            "Balance should be initial amount - spent amount",
        )
