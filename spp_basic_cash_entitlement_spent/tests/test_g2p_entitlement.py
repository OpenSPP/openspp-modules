from odoo import fields
from odoo.tests import TransactionCase


class TestG2pEntitlement(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.registrant = cls.env["res.partner"].create(
            {
                "name": "Registrant 1 [TEST]",
                "is_registrant": True,
                "is_group": True,
            }
        )
        cls.program = cls.env["g2p.program"].create(
            {
                "name": "Program 1 [TEST]",
                "program_membership_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.registrant.id,
                            "state": "enrolled",
                        },
                    ),
                ],
            }
        )
        cls.program.create_journal()
        cls.cycle = cls.env["g2p.cycle"].create(
            {
                "name": "Cycle 1 [TEST]",
                "program_id": cls.program.id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today(),
            }
        )
        cls._test_entitlement = cls.env["g2p.entitlement"].create(
            {
                "partner_id": cls.registrant.id,
                "cycle_id": cls.cycle.id,
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
