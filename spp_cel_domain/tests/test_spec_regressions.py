from datetime import date, datetime

from odoo.tests import TransactionCase
from odoo.tests.common import tagged

from ..models.cel_queryplan import LeafDomain
from ..services import cel_parser as P


@tagged("post_install", "-at_install", "cel_domain")
class TestCelSpecRegressions(TransactionCase):
    def setUp(self):
        super().setUp()
        self.translator = self.env["cel.translator"]
        self.registry = self.env["cel.registry"]
        self.cfg_individuals = self.registry.load_profile("registry_individuals")
        self.partner_model = self.env["ir.model"].search([("model", "=", "res.partner")], limit=1)

    def test_between_translates_to_range_domain(self):
        expr = 'between(me.birthdate, date("2025-01-01"), date("2025-12-31"))'
        plan, explain = self.translator.translate("res.partner", expr, self.cfg_individuals)
        self.assertIsInstance(plan, LeafDomain)
        # between() should not degrade to a tautology domain
        self.assertNotEqual(plan.domain, [("id", "!=", 0)])
        # The range bounds should target the birthdate field explicitly
        self.assertTrue(
            any(term[0] == "birthdate" for term in plan.domain if isinstance(term, tuple)),
            f"Expected a birthdate range domain, got {plan.domain} with explain={explain}",
        )

    def test_today_lowered_to_python_date(self):
        expr = "me.create_date >= today()"
        plan, explain = self.translator.translate("res.partner", expr, self.cfg_individuals)
        self.assertIsInstance(plan, LeafDomain)
        self.assertTrue(plan.domain, f"Expected a domain for today(), got {plan.domain} (explain={explain})")
        literal = plan.domain[0][2] if plan.domain and isinstance(plan.domain[0], tuple) else None
        self.assertIsInstance(
            literal,
            (date, datetime),
            "today() should be materialised to a native date/datetime literal before building domains",
        )
        # Ensure we did not accidentally keep the parser Call node around
        self.assertNotIsInstance(literal, P.Call)

    def test_wizard_surfaces_preview_records(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Preview Target",
                "is_registrant": True,
                "is_group": False,
            }
        )
        wizard = self.env["cel.rule.wizard"].create(
            {
                "profile": "registry_individuals",
                "model_id": self.partner_model.id,
                "cel_expression": f"me.id == {partner.id}",
            }
        )
        wizard.action_validate_preview()
        # Analysts should see sample records after validation; currently this stays empty.
        self.assertTrue(
            wizard.sample_ids,
            "Preview wizard should expose matching records (e.g., via sample_ids) so analysts can inspect them",
        )
