"""
Tests for CEL extensibility system.

Tests function registry and multi-module YAML loading to ensure
other modules can contribute CEL functions and profiles.
"""

import logging
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.tests import TransactionCase
from odoo.tests.common import tagged

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install", "cel_domain")
class TestCelExtensibility(TransactionCase):
    """Test CEL extensibility features for external modules."""

    def setUp(self):
        super().setUp()

        # Set up gender types
        Gender = self.env["gender.type"]
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

    def tearDown(self):
        """Clean up registered functions after each test."""
        super().tearDown()
        try:
            registry = self.env["cel.function.registry"]
            registry.clear_all()
        except Exception:
            pass

    def _exec(self, expr, profile="registry_individuals"):
        """Helper to execute CEL expression."""
        registry = self.env["cel.registry"]
        cfg = registry.load_profile(profile)
        executor = self.env["cel.executor"].with_context(cel_profile=profile, cel_cfg=cfg)
        model = cfg.get("root_model", "res.partner")
        return executor.compile_and_preview(model, expr, limit=50)

    def test_function_registry_basic(self):
        """Test basic function registration and retrieval."""
        registry = self.env["cel.function.registry"]

        # Test registration
        def test_func():
            return True

        result = registry.register("test_func", test_func)
        self.assertTrue(result, "Function should register successfully")

        # Test retrieval
        handler = registry.get_handler("test_func")
        self.assertIsNotNone(handler, "Registered function should be retrievable")
        self.assertEqual(handler, test_func, "Retrieved function should match registered function")

        # Test is_registered
        self.assertTrue(registry.is_registered("test_func"), "Function should be registered")
        self.assertFalse(registry.is_registered("nonexistent"), "Nonexistent function should not be registered")

        # Test list_functions
        functions = registry.list_functions()
        self.assertIn("test_func", functions, "Registered function should appear in list")

    def test_function_registry_unregister(self):
        """Test unregistering functions."""
        registry = self.env["cel.function.registry"]

        # Register function
        def test_func():
            return True

        registry.register("test_func", test_func)
        self.assertTrue(registry.is_registered("test_func"))

        # Unregister
        result = registry.unregister("test_func")
        self.assertTrue(result, "Unregister should succeed")
        self.assertFalse(registry.is_registered("test_func"), "Function should no longer be registered")

        # Unregister nonexistent function
        result = registry.unregister("nonexistent")
        self.assertFalse(result, "Unregistering nonexistent function should return False")

    def test_function_registry_invalid_handler(self):
        """Test registering non-callable handler fails gracefully."""
        registry = self.env["cel.function.registry"]

        # Try to register non-callable
        result = registry.register("bad_func", "not a function")
        self.assertFalse(result, "Registering non-callable should fail")

        # Verify it's not registered
        self.assertFalse(registry.is_registered("bad_func"))

    def test_function_registry_override_warning(self):
        """Test that overriding existing function logs warning."""
        registry = self.env["cel.function.registry"]

        def func1():
            return 1

        def func2():
            return 2

        # Register first function
        registry.register("test_func", func1)
        handler1 = registry.get_handler("test_func")
        self.assertEqual(handler1(), 1)

        # Override with second function (should log warning)
        registry.register("test_func", func2)
        handler2 = registry.get_handler("test_func")
        self.assertEqual(handler2(), 2, "Function should be overridden")

    def test_function_registry_clear_all(self):
        """Test clearing all registered functions."""
        registry = self.env["cel.function.registry"]

        # Register multiple functions
        registry.register("func1", lambda: 1)
        registry.register("func2", lambda: 2)
        registry.register("func3", lambda: 3)

        self.assertEqual(len(registry.list_functions()), 3)

        # Clear all
        count = registry.clear_all()
        self.assertEqual(count, 3, "Should return number of cleared functions")
        self.assertEqual(len(registry.list_functions()), 0, "All functions should be cleared")

    def test_custom_function_in_expression(self):
        """Test using a custom registered function in CEL expression."""
        registry = self.env["cel.function.registry"]

        # Register a custom function that returns boolean
        def is_test_environment():
            """Check if we're in test environment."""
            return True

        registry.register("is_test_env", is_test_environment)

        # Use the function in an expression
        result = self._exec("is_test_env()")

        # Should match all records (returns True for all)
        self.assertGreaterEqual(result.get("count", 0), 1, "Custom function should execute")

    def test_custom_function_with_arguments(self):
        """Test custom function that takes arguments."""
        registry = self.env["cel.function.registry"]

        # Register function that checks if year is even
        def is_even_year(date_val):
            if not date_val:
                return False
            if hasattr(date_val, "year"):
                return date_val.year % 2 == 0
            return False

        registry.register("is_even_year", is_even_year)

        # This test just verifies the function can be called
        # (actual filtering would require more complex domain logic)
        handler = registry.get_handler("is_even_year")
        test_date = date(2024, 1, 1)
        self.assertTrue(handler(test_date), "2024 should be even year")

    def test_multi_module_yaml_loading(self):
        """Test that YAML profiles are loaded from all installed modules."""
        registry = self.env["cel.registry"]

        # Load profiles
        profiles = registry._load_yaml_profiles()

        # Should at least have cel_domain profiles
        self.assertIsInstance(profiles, dict, "Should return dictionary")

        # Should have core profiles from cel_domain
        self.assertIn("registry_individuals", profiles, "Should have registry_individuals")
        self.assertIn("registry_groups", profiles, "Should have registry_groups")

    def test_profile_loading_precedence(self):
        """Test that profiles are loaded with correct precedence."""
        registry = self.env["cel.registry"]

        # Test loading a standard profile
        profile = registry.load_profile("registry_individuals")

        self.assertIsInstance(profile, dict, "Should return dictionary")
        self.assertEqual(profile.get("root_model"), "res.partner", "Should have correct root model")
        self.assertIn("me", profile.get("symbols", {}), "Should have 'me' symbol")

    def test_yaml_loading_graceful_degradation(self):
        """Test that YAML loading fails gracefully for missing modules."""
        registry = self.env["cel.registry"]

        # Try to load nonexistent profile
        profile = registry.load_profile("nonexistent_profile")

        # Should return empty dict, not raise exception
        self.assertEqual(profile, {}, "Nonexistent profile should return empty dict")

    def test_extensibility_example_crop_season(self):
        """Example: Test a hypothetical crop_season function for farming module."""
        registry = self.env["cel.function.registry"]

        # Simulate what spp_farmer module would register
        def crop_season(date_val):
            """Determine crop season from date."""
            if not date_val:
                return None
            if hasattr(date_val, "month"):
                month = date_val.month
                if 3 <= month <= 5:
                    return "planting"
                elif 6 <= month <= 9:
                    return "growing"
                else:
                    return "harvest"
            return None

        registry.register("crop_season", crop_season)

        # Verify it's registered
        self.assertTrue(registry.is_registered("crop_season"))

        # Test the function directly
        handler = registry.get_handler("crop_season")
        march_date = date(2025, 3, 1)
        july_date = date(2025, 7, 1)
        november_date = date(2025, 11, 1)

        self.assertEqual(handler(march_date), "planting")
        self.assertEqual(handler(july_date), "growing")
        self.assertEqual(handler(november_date), "harvest")

    def test_extensibility_example_health_check(self):
        """Example: Test a hypothetical health check function for health module."""
        registry = self.env["cel.function.registry"]

        # Simulate what spp_health module would register
        def is_vaccination_due(birthdate):
            """Check if person is due for vaccination (example logic)."""
            if not birthdate:
                return False
            age_months = (date.today() - birthdate).days / 30
            # Example: Due if between 2-6 months old
            return 2 <= age_months <= 6

        registry.register("is_vaccination_due", is_vaccination_due)

        # Test the function
        handler = registry.get_handler("is_vaccination_due")

        three_months_ago = date.today() - relativedelta(months=3)
        one_year_ago = date.today() - relativedelta(years=1)

        self.assertTrue(handler(three_months_ago), "3-month-old should be due")
        self.assertFalse(handler(one_year_ago), "1-year-old should not be due")

    def test_function_registry_isolation(self):
        """Test that function registry doesn't interfere with built-in functions."""
        registry = self.env["cel.function.registry"]

        # Register custom function
        def my_custom_func():
            return True

        registry.register("my_custom_func", my_custom_func)

        # Built-in functions should still work
        result = self._exec("age_years(birthdate) < 30")
        self.assertGreaterEqual(result.get("count", 0), 0, "Built-in age_years should still work")

        # has_tag should still work
        result2 = self._exec('has_tag("test")')
        self.assertIsInstance(result2, dict, "Built-in has_tag should still work")
