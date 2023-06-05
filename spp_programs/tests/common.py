from odoo import fields
from odoo.tests import TransactionCase


class Common(TransactionCase):
    def setUp(self):
        super().setUp()

        self.program = self.env["g2p.program"].create({"name": "Test Program"})

        self.registrant = self.env["res.partner"].create(
            {
                "name": "test registrant",
                "is_registrant": True,
            }
        )

        self.cycle = self.env["g2p.cycle"].create(
            {
                "name": "Test Cycle",
                "program_id": self.program.id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today(),
            }
        )

        self.entitlement = self.env["g2p.entitlement.inkind"].create(
            {
                "partner_id": self.registrant.id,
                "cycle_id": self.cycle.id,
            }
        )
