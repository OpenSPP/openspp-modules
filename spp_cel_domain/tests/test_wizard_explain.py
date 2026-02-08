from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "cel_domain")
class TestWizardExplain(TransactionCase):
    def setUp(self):
        super().setUp()
        # Seed a group with 2 members to ensure metric stats are non-empty
        P = self.env["res.partner"]
        self.g = P.create({"name": "WG", "is_registrant": True, "is_group": True})
        m1 = P.create({"name": "M1", "is_registrant": True, "is_group": False})
        m2 = P.create({"name": "M2", "is_registrant": True, "is_group": False})
        M = self.env["g2p.group.membership"]
        M.create({"group": self.g.id, "individual": m1.id})
        M.create({"group": self.g.id, "individual": m2.id})

    def test_metrics_explain_tab(self):
        # Seed attendance metrics for both members to drive metrics explain
        FV = self.env["openspp.indicator.value"]
        member_ids = [
            m.id for m in self.env["g2p.group.membership"].search([("group", "=", self.g.id)]).mapped("individual")
        ]
        rows = [
            {
                "metric": "education.attendance_pct",
                "subject_model": "res.partner",
                "subject_id": mid,
                "period_key": "2024-09",
                "value_json": 90,
                "value_type": "number",
                "source": "test",
            }
            for mid in member_ids
        ]
        if rows:
            FV.sudo().upsert_values(rows)
        W = self.env["cel.rule.wizard"].create(
            {
                "profile": "registry_groups",
                "model_id": self.env["ir.model"]._get_id("res.partner"),
                "cel_expression": 'avg_over(members, metric("education.attendance_pct", m, "2024-09")) >= 0',
            }
        )
        W.action_validate_preview()
        assert W.preview_count >= 1
        # Metrics explain string present and structured lines populated
        assert W.metrics_explain_text is not None
        assert len(W.metric_line_ids) >= 1
