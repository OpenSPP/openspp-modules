from __future__ import annotations

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "spp_indicators")
class TestUpsertIdempotency(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Feature = self.env["openspp.indicator.value"].sudo()
        self.Def = self.env["openspp.indicator.definition"].sudo()
        self.metric = "test.upsert.idem"
        self.Def.create(
            {
                "name": self.metric,
                "subject_model": "res.partner",
                "value_type": "number",
                "period_granularity": "month",
                "company_id": self.env.company.id,
            }
        )
        # 50 subjects to keep test quick
        self.partners = self.env["res.partner"].create(
            [{"name": f"UP{i}", "is_registrant": True} for i in range(1, 51)]
        )

    def test_bulk_insert_then_update(self):
        rows = [
            {
                "metric": self.metric,
                "provider": "unit-bulk",
                "subject_model": "res.partner",
                "subject_id": pid,
                "period_key": "2025-09",
                "value_json": 1,
                "value_type": "number",
            }
            for pid in self.partners.ids
        ]
        res1 = self.Feature.upsert_values(rows)
        self.assertEqual(res1["inserted"], len(rows))
        self.assertEqual(res1["updated"], 0)

        # Update all rows with a different value; should be all updates
        for r in rows:
            r["value_json"] = 2
        res2 = self.Feature.upsert_values(rows)
        self.assertEqual(res2["inserted"], 0)
        self.assertEqual(res2["updated"], len(rows))

        # Idempotency: running again with identical values is still all updates
        res3 = self.Feature.upsert_values(rows)
        self.assertEqual(res3["inserted"], 0)
        self.assertEqual(res3["updated"], len(rows))
