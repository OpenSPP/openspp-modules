from odoo.tests import common, tagged


@tagged("post_install", "-at_install", "cel_domain")
class TestMetricsIntegration(common.TransactionCase):
    def setUp(self):
        super().setUp()
        # Create simple partners
        Partner = self.env["res.partner"]
        self.p1 = Partner.create({"name": "Alice", "is_registrant": True, "is_group": False})
        self.p2 = Partner.create({"name": "Bob", "is_registrant": True, "is_group": False})
        self.p3 = Partner.create({"name": "Cara", "is_registrant": True, "is_group": False})

    def test_push_and_filter_by_metric(self):
        # Push attendance % values for September 2024
        payload = {
            "metric": "education.attendance_pct",
            "subject_model": "res.partner",
            "period_key": "2024-09",
            "items": [
                {"subject_id": self.p1.id, "value": 92},
                {"subject_id": self.p2.id, "value": 80},
                # p3 missing
            ],
        }
        self.env["openspp.indicator.value"].sudo().upsert_values(
            [
                {
                    "metric": payload["metric"],
                    "subject_model": payload["subject_model"],
                    "subject_id": it["subject_id"],
                    "period_key": payload["period_key"],
                    "value_json": it["value"],
                    "value_type": "number",
                    "source": "test",
                }
                for it in payload["items"]
            ]
        )

        # Use CEL to filter individuals with attendance >= 85
        cfg = self.env["cel.registry"].load_profile("registry_individuals")
        expr = 'metric("education.attendance_pct", me, "2024-09") >= 85'
        res = self.env["cel.executor"].with_context(cel_cfg=cfg).compile_and_preview(cfg["root_model"], expr, limit=100)
        ids = set(res["ids"])
        assert self.p1.id in ids
        assert self.p2.id not in ids
        assert self.p3.id not in ids

    def test_household_size_provider(self):
        # Register an isolated provider for the test metric to avoid clashing with the
        # real household.size provider that may be loaded in the environment.
        class _TestHouseholdSizeProvider:
            def compute_batch(self, env, ctx, subject_ids):
                Membership = env["g2p.group.membership"]
                rows = Membership.read_group(
                    [("is_ended", "=", False), ("group", "in", subject_ids)], ["group"], ["group"]
                )
                counts = {r["group"][0]: r["group_count"] for r in rows if r.get("group")}
                return {int(sid): int(counts.get(sid, 0)) for sid in subject_ids}

        self.env["openspp.indicator.registry"].register(
            name="test_household.size",
            handler=_TestHouseholdSizeProvider(),
            return_type="number",
            subject_model="res.partner",
            capabilities={"supports_batch": True, "default_ttl": 0},
            provider="test.household",
        )

        # Create a group and 2 active members
        Partner = self.env["res.partner"]
        group = Partner.create({"name": "HH-X", "is_registrant": True, "is_group": True})
        ind1 = Partner.create({"name": "M1", "is_registrant": True, "is_group": False})
        ind2 = Partner.create({"name": "M2", "is_registrant": True, "is_group": False})
        Membership = self.env["g2p.group.membership"]
        Membership.create({"group": group.id, "individual": ind1.id, "is_ended": False})
        Membership.create({"group": group.id, "individual": ind2.id, "is_ended": False})

        # Seed the value (cache path) to make the test robust across environments
        self.env["openspp.indicator.value"].sudo().upsert_values(
            [
                {
                    "metric": "test_household.size",
                    "subject_model": "res.partner",
                    "subject_id": group.id,
                    "period_key": "current",
                    "value_json": 2,
                    "value_type": "number",
                    "source": "test",
                }
            ]
        )

        cfg = self.env["cel.registry"].load_profile("registry_groups")
        expr = 'metric("test_household.size", me, "current") >= 2'
        res = self.env["cel.executor"].with_context(cel_cfg=cfg).compile_and_preview(cfg["root_model"], expr, limit=100)
        ids = set(res["ids"])
        assert group.id in ids
