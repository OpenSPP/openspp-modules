from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "cel_domain")
class TestPrefetchWizard(TransactionCase):
    def setUp(self):
        super().setUp()
        P = self.env["res.partner"]
        self.partners = [P.create({"name": f"S{i}", "is_registrant": True, "is_group": False}) for i in range(5)]

    def test_prefetch_chunking(self):
        Wiz = self.env["openspp.indicator.prefetch.wizard"]
        domain_text = str([("id", "in", [p.id for p in self.partners])])
        w = Wiz.create(
            {
                "metric": "education.attendance_pct",
                "subject_model": "res.partner",
                "period_key": "2024-09",
                "domain_text": domain_text,
                "enqueue": True,
                "chunk_size": 2,
            }
        )
        act = w.action_run()
        # Expect 3 chunks for 5 subjects with chunk_size=2
        msg = act.get("params", {}).get("message", "")
        assert "Created 3 refresh job(s) for 5 subjects" in msg
