import logging
from datetime import date, timedelta

from odoo import fields
from odoo.tests import TransactionCase
from odoo.tests.common import tagged

_logger = logging.getLogger("odoo.addons.spp_cel_domain")


@tagged("post_install", "-at_install", "cel_domain")
class TestProgramAndEntitlements(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Partner = self.env["res.partner"]
        self.Program = self.env["g2p.program"]
        self.Cycle = self.env["g2p.cycle"]
        self.Membership = self.env["g2p.program_membership"]
        self.Entitlement = self.env["g2p.entitlement"]
        self.AccountJournal = self.env["account.journal"]

        # Create a registrant (individual)
        self.alice = self.Partner.create(
            {
                "name": "Alice",
                "is_registrant": True,
                "is_group": False,
            }
        )

        # Minimal journal for program currency
        self.journal = self.AccountJournal.create(
            {
                "name": "Beneficiary Cash",
                "code": "BCS1",
                "type": "cash",
                "beneficiary_disb": True,
                "company_id": self.env.company.id,
                "currency_id": self.env.company.currency_id.id,
            }
        )

        # Program A and B
        self.progA = self.Program.create({"name": "Cash Transfer A", "journal_id": self.journal.id})
        self.progB = self.Program.create({"name": "Cash Transfer B", "journal_id": self.journal.id})

        # Cycle for B (for entitlements)
        self.cycleB = self.Cycle.create(
            {
                "name": "Cycle B1",
                "program_id": self.progB.id,
                "start_date": fields.Date.to_date(date.today()),
                "end_date": fields.Date.to_date(date.today() + timedelta(days=30)),
            }
        )

        # Enrollment: Alice enrolled in Program A
        self.memA = self.Membership.create(
            {
                "partner_id": self.alice.id,
                "program_id": self.progA.id,
                "state": "enrolled",
            }
        )

        # Entitlement: Alice approved in Program B/CycleB
        self.entB = self.Entitlement.create(
            {
                "partner_id": self.alice.id,
                "cycle_id": self.cycleB.id,
                "is_cash_entitlement": True,
                "initial_amount": 10.0,
                "state": "approved",
            }
        )

        # Prepare executor
        self.cfg_indiv = self.env["cel.registry"].load_profile("registry_individuals")
        self.exec_indiv = self.env["cel.executor"].with_context(
            cel_profile="registry_individuals", cel_cfg=self.cfg_indiv
        )

    def test_exists_enrollments_enrolled(self):
        _logger.info("[CEL TEST] Running test_exists_enrollments_enrolled")
        expr = 'exists(enrollments, e, e.program == program("Cash Transfer A") and e.state == "enrolled")'
        res = self.exec_indiv.compile_and_preview("res.partner", expr, limit=50)
        self.assertIn(self.alice.id, res["ids"])  # Alice is enrolled in Program A

        expr_no = 'exists(enrollments, e, e.program == program("Cash Transfer B") and e.state == "enrolled")'
        res_no = self.exec_indiv.compile_and_preview("res.partner", expr_no, limit=50)
        self.assertNotIn(self.alice.id, res_no["ids"])  # Not enrolled in Program B
        _logger.info("CELTEST: TestProgramAndEntitlements.test_exists_enrollments_enrolled PASS")

    def test_exists_entitlements_approved(self):
        _logger.info("[CEL TEST] Running test_exists_entitlements_approved")
        expr = 'exists(entitlements, t, t.program == program("Cash Transfer B") and t.state == "approved")'
        res = self.exec_indiv.compile_and_preview("res.partner", expr, limit=50)
        self.assertIn(self.alice.id, res["ids"])  # Alice has approved entitlement in Program B
        _logger.info("CELTEST: TestProgramAndEntitlements.test_exists_entitlements_approved PASS")
