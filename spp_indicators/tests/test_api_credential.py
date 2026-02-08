from __future__ import annotations

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "spp_indicators")
class TestApiCredential(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Cred = self.env["openspp.indicator.api_credential"].sudo()

    def test_token_hash_and_lookup(self):
        cred = self.Cred.create(
            {
                "name": "Unit Token",
                "token_plain": "abc123456",
                "allowed_metric_pattern": "test.*",
                "company_id": self.env.company.id,
            }
        )
        self.assertTrue(cred.token_hash)
        self.assertEqual(cred.token_prefix, "abc123")
        found = self.Cred.find_by_token("abc123456")
        self.assertEqual(found.id, cred.id)
        self.assertFalse(self.Cred.find_by_token("wrong"))

    def test_active_inactive_and_expiry(self):
        cred = self.Cred.create(
            {
                "name": "Status Token",
                "token_plain": "stat-1",
                "company_id": self.env.company.id,
            }
        )
        # Active by default
        self.assertTrue(cred.check_active())

        cred.write({"status": "inactive"})
        with self.assertRaises(ValidationError):
            cred.check_active()

        cred.write({"status": "active", "expires_at": fields.Datetime.now() - timedelta(hours=1)})
        with self.assertRaises(ValidationError):
            cred.check_active()

    def test_rate_limit_rolling_window(self):
        cred = self.Cred.create(
            {
                "name": "Rate Token",
                "token_plain": "rate-1",
                "request_limit": 1,
                "company_id": self.env.company.id,
            }
        )
        # First usage allowed
        cred.bump_usage("127.0.0.1")
        # Second within same window should raise
        with self.assertRaises(ValidationError):
            cred.bump_usage("127.0.0.1")
        # Move window back and try again
        cred.write(
            {
                "request_window_start": fields.Datetime.now() - timedelta(hours=2),
                "request_count": 0,
            }
        )
        cred.bump_usage("127.0.0.1")
