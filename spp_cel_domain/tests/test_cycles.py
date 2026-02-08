from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "cel_domain")
class TestCycles(TransactionCase):
    def setUp(self):
        super().setUp()
        # Create program and 3 cycles with sequence
        Program = self.env["g2p.program"]
        Cycle = self.env["g2p.cycle"]
        self.prog = Program.create({"name": "Edu Program"})
        base_start = fields.Date.today()

        def _cycle_vals(name_suffix: str, sequence: int, offset_months: int):
            start = base_start + relativedelta(months=offset_months)
            end = start + relativedelta(days=30)
            return {
                "name": f"{name_suffix}",
                "program_id": self.prog.id,
                "sequence": sequence,
                "start_date": start,
                "end_date": end,
            }

        self.c1 = Cycle.create(_cycle_vals("Cycle 1", 1, 0))
        self.c2 = Cycle.create(_cycle_vals("Cycle 2", 2, 1))
        self.c3 = Cycle.create(_cycle_vals("Cycle 3", 3, 2))

        self.cfg = self.env["cel.registry"].load_profile("registry_groups")
        self.exec = self.env["cel.executor"].with_context(cel_profile="registry_groups", cel_cfg=self.cfg)
        # Seed a group and one member so metric('test_household.size', ...) can match
        P = self.env["res.partner"]
        self.g = P.create({"name": "G1", "is_registrant": True, "is_group": True})
        self.m = P.create({"name": "M1", "is_registrant": True, "is_group": False})
        self.env["g2p.group.membership"].create({"group": self.g.id, "individual": self.m.id})

    def _ids(self, expr):
        res = self.exec.compile_and_preview("res.partner", expr, limit=0)
        return set(res["ids"])

    def test_last_first_previous_next(self):
        # Push values for each cycle to exercise cycle helpers with metrics
        FV = self.env["openspp.indicator.value"]
        FV.sudo().upsert_values(
            [
                {
                    "metric": "test_household.size",
                    "subject_model": "res.partner",
                    "subject_id": self.g.id,
                    "period_key": f"cycle:{self.c1.id}",
                    "value_json": 1,
                    "value_type": "number",
                    "source": "test",
                },
                {
                    "metric": "test_household.size",
                    "subject_model": "res.partner",
                    "subject_id": self.g.id,
                    "period_key": f"cycle:{self.c2.id}",
                    "value_json": 1,
                    "value_type": "number",
                    "source": "test",
                },
                {
                    "metric": "test_household.size",
                    "subject_model": "res.partner",
                    "subject_id": self.g.id,
                    "period_key": f"cycle:{self.c3.id}",
                    "value_json": 1,
                    "value_type": "number",
                    "source": "test",
                },
            ]
        )
        expr_last = 'metric("test_household.size", me, last_cycle("Edu Program")) >= 1'
        assert self.g.id in self._ids(expr_last)
        expr_prev = 'metric("test_household.size", me, previous(last_cycle("Edu Program"))) >= 1'
        assert self.g.id in self._ids(expr_prev)
        expr_first = 'metric("test_household.size", me, first_cycle("Edu Program")) >= 1'
        assert self.g.id in self._ids(expr_first)
