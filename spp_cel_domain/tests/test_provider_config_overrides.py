from datetime import datetime, timedelta

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "cel_domain")
class TestProviderConfigOverrides(TransactionCase):
    def test_ttl_override_for_household_size(self):
        # Create a small household
        P = self.env["res.partner"]
        hh = P.create({"name": "TTL-HH", "is_registrant": True, "is_group": True})
        ind = P.create({"name": "TTL-M1", "is_registrant": True, "is_group": False})
        M = self.env["g2p.group.membership"]
        M.create({"group": hh.id, "individual": ind.id, "is_ended": False})

        # Register a lightweight provider handler inline to avoid external dependencies
        class _MiniHHProvider:
            def compute_batch(self, env, ctx, subject_ids):
                return {int(s): 1 for s in subject_ids}

        self.env["openspp.indicator.registry"].register(
            name="test_household.size",
            handler=_MiniHHProvider(),
            return_type="number",
            subject_model="res.partner",
            capabilities={"supports_batch": True, "default_ttl": 0},
            provider="test.hh",
        )

        # Provider config override: very short TTL
        Prov = self.env["openspp.indicator.provider"]
        Prov.create(
            {
                "name": "Household Size TTL Short",
                "metric": "test_household.size",
                "default_ttl": 2,  # seconds
                "max_batch_size": 10,
            }
        )

        # Evaluate refresh to materialize the value with TTL override
        svc = self.env["openspp.indicator"]
        svc.evaluate("test_household.size", "res.partner", [hh.id], "current", mode="refresh")

        # Validate expires_at is close (<< 1 minute), and company_id is set
        row = self.env["openspp.indicator.value"].search(
            [
                ("metric", "=", "test_household.size"),
                ("subject_model", "=", "res.partner"),
                ("subject_id", "=", hh.id),
            ],
            order="id desc",
            limit=1,
        )
        assert row, "feature row not found after refresh"
        expires_at = row.expires_at
        company_id = row.company_id.id
        assert company_id == self.env.company.id
        assert expires_at is not None
        # Must be near now + 2s (allow some slack); definitely not ~24h away
        now = datetime.utcnow()
        assert expires_at < (now + timedelta(seconds=60))
