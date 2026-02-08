from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "cel_domain")
class TestMetricsNamespaced(TransactionCase):
    def setUp(self):
        super().setUp()
        P = self.env["res.partner"]
        self.p1 = P.create({"name": "NS-Alice", "is_registrant": True, "is_group": False})
        self.p2 = P.create({"name": "NS-Bob", "is_registrant": True, "is_group": False})

    def test_namespaced_metric_compare_individuals(self):
        # Seed cached values without provider (provider-agnostic push)
        FV = self.env["openspp.indicator.value"]
        FV.sudo().upsert_values(
            [
                {
                    "metric": "education.attendance_pct",
                    "subject_model": "res.partner",
                    "subject_id": self.p1.id,
                    "period_key": "2024-09",
                    "value_json": 90,
                    "value_type": "number",
                    "source": "test",
                },
                {
                    "metric": "education.attendance_pct",
                    "subject_model": "res.partner",
                    "subject_id": self.p2.id,
                    "period_key": "2024-09",
                    "value_json": 70,
                    "value_type": "number",
                    "source": "test",
                },
            ]
        )

        cfg = self.env["cel.registry"].load_profile("registry_individuals")
        expr = 'education.attendance_pct("2024-09", me) >= 85'
        res = self.env["cel.executor"].with_context(cel_cfg=cfg).compile_and_preview(cfg["root_model"], expr, limit=100)
        ids = set(res["ids"])
        assert self.p1.id in ids
        assert self.p2.id not in ids

    def test_namespaced_metric_aggregator_groups(self):
        # Group with two children and cached attendance values
        P = self.env["res.partner"]
        G = P.create({"name": "NS-HH", "is_registrant": True, "is_group": True})
        c1 = P.create({"name": "NS-C1", "is_registrant": True, "is_group": False})
        c2 = P.create({"name": "NS-C2", "is_registrant": True, "is_group": False})
        M = self.env["g2p.group.membership"]
        M.create({"group": G.id, "individual": c1.id, "is_ended": False})
        M.create({"group": G.id, "individual": c2.id, "is_ended": False})
        FV = self.env["openspp.indicator.value"]
        # Values 90 and 100 → avg 95
        FV.sudo().upsert_values(
            [
                {
                    "metric": "education.attendance_pct",
                    "subject_model": "res.partner",
                    "subject_id": c1.id,
                    "period_key": "2024-09",
                    "value_json": 90,
                    "value_type": "number",
                    "source": "test",
                },
                {
                    "metric": "education.attendance_pct",
                    "subject_model": "res.partner",
                    "subject_id": c2.id,
                    "period_key": "2024-09",
                    "value_json": 100,
                    "value_type": "number",
                    "source": "test",
                },
            ]
        )
        cfg = self.env["cel.registry"].load_profile("registry_groups")
        expr = 'avg_over(members, education.attendance_pct("2024-09", m)) >= 80'
        res = self.env["cel.executor"].with_context(cel_cfg=cfg).compile_and_preview(cfg["root_model"], expr, limit=100)
        ids = set(res["ids"])
        assert G.id in ids
