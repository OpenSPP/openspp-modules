import logging
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.tests import TransactionCase
from odoo.tests.common import tagged

_logger = logging.getLogger("odoo.addons.spp_cel_domain")


@tagged("post_install", "-at_install", "cel_domain")
class TestAgeYearsTranslator(TransactionCase):
    def setUp(self):
        super().setUp()
        P = self.env["res.partner"]
        today = date.today()
        # Exactly 1, 5, 10 years old today
        self.p1 = P.create(
            {
                "name": "Age 1",
                "is_registrant": True,
                "is_group": False,
                "birthdate": today - relativedelta(years=1),
            }
        )
        self.p5 = P.create(
            {
                "name": "Age 5",
                "is_registrant": True,
                "is_group": False,
                "birthdate": today - relativedelta(years=5),
            }
        )
        self.p10 = P.create(
            {
                "name": "Age 10",
                "is_registrant": True,
                "is_group": False,
                "birthdate": today - relativedelta(years=10),
            }
        )
        self.cfg = self.env["cel.registry"].load_profile("registry_individuals")
        # Restrict searches to the records created in this test for determinism
        self.cfg = dict(self.cfg)
        self.cfg["base_domain"] = [("id", "in", [self.p1.id, self.p5.id, self.p10.id])]
        self.exec = self.env["cel.executor"].with_context(cel_profile="registry_individuals", cel_cfg=self.cfg)

    def _ids(self, expr):
        res = self.exec.compile_and_preview("res.partner", expr, limit=0)
        _logger.info("[CEL AGE TEST] %s -> ids=%s count=%s", expr, res["ids"], res["count"])
        return set(res["ids"])

    def test_age_lt_gt_eq(self):
        # age < 3 => only 1y
        self.assertEqual(self._ids("age_years(me.birthdate) < 3"), {self.p1.id})
        # age > 3 => 5y and 10y
        self.assertEqual(self._ids("age_years(me.birthdate) > 3"), {self.p5.id, self.p10.id})
        # age <= 5 => 1y and 5y
        self.assertEqual(self._ids("age_years(me.birthdate) <= 5"), {self.p1.id, self.p5.id})
        # age == 5 => exactly 5y
        self.assertEqual(self._ids("age_years(me.birthdate) == 5"), {self.p5.id})
        # age != 5 => 1y and 10y
        self.assertEqual(self._ids("age_years(me.birthdate) != 5"), {self.p1.id, self.p10.id})
        # age >= 10 => 10y
        self.assertEqual(self._ids("age_years(me.birthdate) >= 10"), {self.p10.id})
        _logger.info("CELTEST: TestAgeYearsTranslator.test_age_lt_gt_eq PASS")
