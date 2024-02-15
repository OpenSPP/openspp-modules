from odoo import fields
from odoo.tests import TransactionCase


class TestG2pEntitlements(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_group = cls.env["res.partner"].create(
            {
                "name": "group 1",
                "is_registrant": True,
                "is_group": True,
            }
        )
        cls.test_program_1 = cls.env["g2p.program"].create(
            {
                "name": "program 1",
            }
        )
        cls.test_cycle_1 = cls.env["g2p.cycle"].create(
            {
                "name": "cycle 1",
                "program_id": cls.test_program_1.id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.add(fields.Date.today(), days=30),
            }
        )
        cls.test_entitlement = cls.env["g2p.entitlement"].create(
            {
                "cycle_id": cls.test_cycle_1.id,
                "partner_id": cls.test_group.id,
                "initial_amount": 50_000,
            }
        )
        cls.test_entitlement_inkind = cls.env["g2p.entitlement.inkind"].create(
            {
                "cycle_id": cls.test_cycle_1.id,
                "partner_id": cls.test_group.id,
            }
        )

    def test_01_compute_partner_type(self):
        self.assertEqual(self.test_entitlement.partner_type, "group")
        self.test_group.is_group = False
        self.test_entitlement._compute_partner_type()
        self.assertEqual(self.test_entitlement.partner_type, "individual")

    def test_02_compute_type(self):
        self.assertEqual(self.test_entitlement.type, "inkind")
        self.test_entitlement.is_cash_entitlement = True
        self.assertEqual(self.test_entitlement.type, "cash")

    def test_01_compute_partner_type_inkind(self):
        self.assertEqual(self.test_entitlement_inkind.partner_type, "group")
        self.test_group.is_group = False
        self.test_entitlement_inkind._compute_partner_type()
        self.assertEqual(self.test_entitlement_inkind.partner_type, "individual")

    def test_02_compute_type_inkind(self):
        self.assertEqual(self.test_entitlement_inkind.type, "inkind")
