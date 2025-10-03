"""
Test that bare field syntax works (without 'me.' prefix).

This test verifies Option 1: Make the prefix optional
Both syntaxes should work:
- me.gender == "Female"  (explicit)
- gender == "Female"     (bare field - cleaner!)
"""

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.tests import TransactionCase
from odoo.tests.common import tagged


@tagged("post_install", "-at_install", "cel_domain")
class TestBareFieldSyntax(TransactionCase):
    """Test that bare field names work without 'me.' prefix."""

    def setUp(self):
        super().setUp()

        # Set up gender types - ensure consistent capitalization
        Gender = self.env["gender.type"]
        # Always create our own to ensure we know the exact value
        self.gender_female = Gender.create({"code": "F", "value": "Female"})

        # Create test individual
        Partner = self.env["res.partner"]
        self.test_person = Partner.create(
            {
                "name": "Test Person",
                "is_registrant": True,
                "is_group": False,
                "birthdate": date.today() - relativedelta(years=25),
                "gender": self.gender_female.id,
                "phone": "+1234567890",
            }
        )

    def _exec(self, expr, profile="registry_individuals"):
        """Helper to execute CEL expression."""
        registry = self.env["cel.registry"]
        cfg = registry.load_profile(profile)
        executor = self.env["cel.executor"].with_context(cel_profile=profile, cel_cfg=cfg)
        model = cfg.get("root_model", "res.partner")
        return executor.compile_and_preview(model, expr, limit=50)

    def test_bare_field_gender(self):
        """Test that 'gender == \"Female\"' works without 'me.' prefix."""
        # Both syntaxes should work
        result_explicit = self._exec('me.gender == "Female"')
        result_bare = self._exec('gender == "Female"')

        # Both should return the same results
        self.assertEqual(
            set(result_explicit.get("ids", [])),
            set(result_bare.get("ids", [])),
            "Bare field syntax should return same results as explicit 'me.' prefix",
        )

        # Both should have same count
        self.assertEqual(
            result_explicit.get("count"),
            result_bare.get("count"),
            "Bare and explicit syntax should match same number of records",
        )

    def test_bare_field_age_years(self):
        """Test that 'age_years(birthdate)' works without 'me.' prefix."""
        # Both syntaxes should work
        result_explicit = self._exec("age_years(me.birthdate) < 30")
        result_bare = self._exec("age_years(birthdate) < 30")

        # Both should return the same results
        self.assertEqual(
            set(result_explicit.get("ids", [])),
            set(result_bare.get("ids", [])),
            "Bare birthdate should work same as me.birthdate",
        )

    def test_bare_field_phone(self):
        """Test that 'phone != \"\"' works without 'me.' prefix."""
        # Both syntaxes should work
        result_explicit = self._exec('me.phone != ""')
        result_bare = self._exec('phone != ""')

        # Both should return the same results
        self.assertEqual(
            set(result_explicit.get("ids", [])),
            set(result_bare.get("ids", [])),
            "Bare phone should work same as me.phone",
        )

    def test_bare_field_combined_expression(self):
        """Test complex expression with multiple bare fields."""
        # Combine multiple bare fields
        expr_bare = 'gender == "Female" and age_years(birthdate) < 30 and phone != ""'
        expr_explicit = 'me.gender == "Female" and age_years(me.birthdate) < 30 and me.phone != ""'

        result_bare = self._exec(expr_bare)
        result_explicit = self._exec(expr_explicit)

        # Both should return same results
        self.assertEqual(
            set(result_bare.get("ids", [])),
            set(result_explicit.get("ids", [])),
            "Combined bare field expression should work same as explicit",
        )
        self.assertEqual(
            result_bare.get("count"), result_explicit.get("count"), "Both syntaxes should match same count"
        )
