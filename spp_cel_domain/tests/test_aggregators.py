from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "cel_domain")
class TestAggregators(TransactionCase):
    def setUp(self):
        super().setUp()
        P = self.env["res.partner"]
        # Two groups
        self.g1 = P.create({"name": "G1", "is_registrant": True, "is_group": True})
        self.g2 = P.create({"name": "G2", "is_registrant": True, "is_group": True})
        # Members
        self.m1 = P.create({"name": "M1", "is_registrant": True, "is_group": False})
        self.m2 = P.create({"name": "M2", "is_registrant": True, "is_group": False})
        self.m3 = P.create({"name": "M3", "is_registrant": True, "is_group": False})
        M = self.env["g2p.group.membership"]
        M.create({"group": self.g1.id, "individual": self.m1.id, "is_ended": False})
        M.create({"group": self.g1.id, "individual": self.m2.id, "is_ended": False})
        M.create({"group": self.g2.id, "individual": self.m3.id, "is_ended": False})
        # Push metric values for September
        FV = self.env["openspp.indicator.value"]
        # G1 avg = (90 + 100) / 2 = 95, coverage=1.0
        FV.sudo().upsert_values(
            [
                {
                    "metric": "education.attendance_pct",
                    "subject_model": "res.partner",
                    "subject_id": self.m1.id,
                    "period_key": "2024-09",
                    "value_json": 90,
                    "value_type": "number",
                    "source": "test",
                },
                {
                    "metric": "education.attendance_pct",
                    "subject_model": "res.partner",
                    "subject_id": self.m2.id,
                    "period_key": "2024-09",
                    "value_json": 100,
                    "value_type": "number",
                    "source": "test",
                },
            ]
        )
        # G2 has no values -> avg undefined, coverage 0
        self.cfg = self.env["cel.registry"].load_profile("registry_groups")
        self.exec = self.env["cel.executor"].with_context(cel_profile="registry_groups", cel_cfg=self.cfg)

    def _ids(self, expr):
        res = self.exec.compile_and_preview("res.partner", expr, limit=0)
        return set(res["ids"])

    def test_avg_over_metric(self):
        expr = 'avg_over(members, metric("education.attendance_pct", m, "2024-09")) >= 80'
        ids = self._ids(expr)
        assert self.g1.id in ids
        assert self.g2.id not in ids

    def test_coverage_over_metric(self):
        expr = 'coverage_over(members, metric("education.attendance_pct", m, "2024-09")) >= 0.5'
        ids = self._ids(expr)
        assert self.g1.id in ids
        assert self.g2.id not in ids

    def test_all_over_metric(self):
        # All members of g1 must have attendance >= 80; g1 passes (90,100), g2 fails (no data)
        expr = 'all_over(members, metric("education.attendance_pct", m, "2024-09") >= 80)'
        ids = self._ids(expr)
        assert self.g1.id in ids
        assert self.g2.id not in ids
