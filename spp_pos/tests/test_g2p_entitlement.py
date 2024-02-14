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
            }
        )

    def test_01_get_entitlement_code_correct_code(self):
        with self.assertLogs("odoo.addons.spp_pos.models.entitlement") as log_catcher:
            res = self.env["g2p.entitlement"].get_entitlement_code({"code": self._test_entitlement.code})
            log = log_catcher.output[0]
            self.assertIn("Code:", log, "Code should be in log!")
            self.assertIn(self._test_entitlement.code, log, "Log should has input code!")
            self.assertEqual(type(res), dict, "Should be Json Response!")
            for key in ("code", "amount", "status"):
                self.assertIn(key, res.keys(), f"Key `{key}` is missing!")
            self.assertEqual(res["code"], self._test_entitlement.code, "Code should be correct!")
            self.assertEqual(
                res["amount"],
                self._test_entitlement.initial_amount,
                "Amount should be correct!",
            )
            self.assertEqual(res["status"], "Success", "Status should be success!")

    def test_02_get_entitlement_code_incorrect_code(self):
        with self.assertLogs("odoo.addons.spp_pos.models.entitlement") as log_catcher:
            res = self.env["g2p.entitlement"].get_entitlement_code({"code": "self._test_entitlement.code"})
            log = log_catcher.output[0]
            self.assertIn("Code:", log, "Code should be in log!")
            self.assertIn("self._test_entitlement.code", log, "Log should has input code!")
            self.assertEqual(type(res), dict, "Should be Json Response!")
            for key in ("code", "amount", "status"):
                self.assertIn(key, res.keys(), f"Key `{key}` is missing!")
            self.assertFalse(res["code"], "Code should not return!")
            self.assertEqual(res["amount"], 0, "Amount should be 0!")
            self.assertEqual(
                res["status"],
                "QR Doesn't Exist",
                "Status should be `QR Doesn't Exist`!",
            )
