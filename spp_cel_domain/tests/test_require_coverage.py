from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "cel_domain")
class TestRequireCoverage(TransactionCase):
    def setUp(self):
        super().setUp()
        P = self.env["res.partner"]
        self.p1 = P.create({"name": "S1", "is_registrant": True, "is_group": False})
        self.p2 = P.create({"name": "S2", "is_registrant": True, "is_group": False})
        self.cfg = self.env["cel.registry"].load_profile("registry_individuals")
        self.cfg = dict(self.cfg)
        self.cfg["base_domain"] = [("id", "in", [self.p1.id, self.p2.id])]
        self.exec = self.env["cel.executor"].with_context(cel_profile="registry_individuals", cel_cfg=self.cfg)

    def test_require_coverage_gate(self):
        FV = self.env["openspp.indicator.value"]
        # Only one value present → coverage=0.5 < 0.8
        FV.sudo().upsert_values(
            [
                {
                    "metric": "education.attendance_pct",
                    "subject_model": "res.partner",
                    "subject_id": self.p1.id,
                    "period_key": "2024-09",
                    "value_json": 70,
                    "value_type": "number",
                    "source": "test",
                }
            ]
        )
        expr = 'require_coverage(metric("education.attendance_pct", me, "2024-09") >= 0, 0.8)'
        res = self.exec.compile_and_preview("res.partner", expr, limit=0)
        assert res["ids"] == []
        # Add missing value → coverage=1.0 >= 0.8; both match >=0
        FV.sudo().upsert_values(
            [
                {
                    "metric": "education.attendance_pct",
                    "subject_model": "res.partner",
                    "subject_id": self.p2.id,
                    "period_key": "2024-09",
                    "value_json": 10,
                    "value_type": "number",
                    "source": "test",
                }
            ]
        )
        res2 = self.exec.compile_and_preview("res.partner", expr, limit=0)
        assert set(res2["ids"]) == {self.p1.id, self.p2.id}
