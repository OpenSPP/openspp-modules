from __future__ import annotations

from odoo.tests import TransactionCase, tagged

from odoo.addons.spp_indicators.controllers.main import IndicatorsController


@tagged("post_install", "-at_install", "spp_indicators")
class TestPeriodKeyValidation(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ctrl = IndicatorsController()

    def _ok(self, granularity: str, key: str):
        self.assertIsNone(self.ctrl._validate_period_key(granularity, key))

    def _bad(self, granularity: str, key: str):
        self.assertIsNotNone(self.ctrl._validate_period_key(granularity, key))

    def test_month(self):
        self._ok("month", "2025-09")
        self._bad("month", "2025-9")
        self._bad("month", "09-2025")

    def test_day(self):
        self._ok("day", "2025-10-01")
        self._bad("day", "2025-10-1")
        self._bad("day", "2025/10/01")

    def test_week(self):
        self._ok("week", "2025-W40")
        self._bad("week", "2025-40")

    def test_quarter(self):
        self._ok("quarter", "2025-Q4")
        self._ok("quarter", "2025-FY25-Q1")
        self._bad("quarter", "2025-Q5")

    def test_year(self):
        self._ok("year", "2025")
        self._bad("year", "25")

    def test_rolling(self):
        for ok in ("rolling_7d", "rolling_14d", "rolling_30d", "rolling_60d", "rolling_90d"):
            self._ok("rolling", ok)
        self._bad("rolling", "rolling_5d")

    def test_snapshot_and_static(self):
        self._ok("snapshot", "asof:2025-10-01")
        self._bad("snapshot", "asof:2025-10-1")
        self._ok("static", "always")
        self._bad("static", "ALWAYS")
