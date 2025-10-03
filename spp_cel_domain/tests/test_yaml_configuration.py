"""
Test YAML configuration loading and merging.

Tests that the configuration system correctly loads and merges profiles from:
1. System parameters (highest priority)
2. YAML file (middle priority)
3. Hardcoded defaults (lowest priority)
"""

import logging

from odoo.tests import TransactionCase
from odoo.tests.common import tagged

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install", "cel_domain")
class TestYAMLConfiguration(TransactionCase):
    """Test YAML configuration loading and merging."""

    def setUp(self):
        super().setUp()
        self.registry = self.env["cel.registry"]

    def test_yaml_file_exists(self):
        """
        Test that the YAML configuration file exists and can be loaded.
        """
        _logger.info("[CEL TEST] Testing YAML configuration file existence")

        # The YAML loading should not crash
        yaml_config = self.registry._load_yaml_profiles()

        # Should load at least the profiles defined in the YAML
        self.assertIsInstance(yaml_config, dict, "YAML config should be a dict")

        # Expected profiles from cel_symbols.template.yaml
        expected_profiles = [
            "registry_individuals",
            "registry_groups",
            "program_memberships",
            "entitlements",
        ]

        for profile_name in expected_profiles:
            self.assertIn(profile_name, yaml_config, f"Profile '{profile_name}' should be in YAML config")

        _logger.info(f"✅ YAML loaded {len(yaml_config)} profiles: {list(yaml_config.keys())}")

    def test_yaml_merges_with_defaults(self):
        """
        Test that YAML configuration properly merges with hardcoded defaults.

        YAML should override specific fields while keeping other defaults intact.
        """
        _logger.info("[CEL TEST] Testing YAML merge with defaults")

        # Load a profile that exists in both YAML and defaults
        config = self.registry.load_profile("registry_groups")

        # Should have root_model from either YAML or defaults
        self.assertEqual(config.get("root_model"), "res.partner", "Should have correct root_model")

        # Should have base_domain
        self.assertIn("base_domain", config, "Should have base_domain")

        # Should have symbols
        self.assertIn("symbols", config, "Should have symbols section")
        symbols = config.get("symbols", {})

        # Should have the 'me' symbol
        self.assertIn("me", symbols, "Should have 'me' symbol")

        # Should have the 'members' symbol with default_domain
        self.assertIn("members", symbols, "Should have 'members' symbol")
        members = symbols.get("members", {})
        self.assertIn("default_domain", members, "members should have default_domain (active members by default)")

        # default_domain should filter to active members
        default_domain = members.get("default_domain", [])
        self.assertEqual(
            default_domain, [["is_ended", "=", False]], "Members should default to active (is_ended=False)"
        )

        # Should have roles section
        self.assertIn("roles", config, "Should have roles section")
        roles = config.get("roles", {})
        self.assertIn("head", roles, "Should have 'head' role definition")

        _logger.info("✅ YAML merge with defaults works correctly")

    def test_all_profiles_loadable(self):
        """
        Test that all expected profiles can be loaded without errors.
        """
        _logger.info("[CEL TEST] Testing all profile loading")

        profiles = [
            "registry_individuals",
            "registry_groups",
            "program_memberships",
            "entitlements",
        ]

        for profile_name in profiles:
            config = self.registry.load_profile(profile_name)

            self.assertIsInstance(config, dict, f"Profile '{profile_name}' should return dict")
            self.assertGreater(len(config), 0, f"Profile '{profile_name}' should not be empty")
            self.assertIn("root_model", config, f"Profile '{profile_name}' should have root_model")

            _logger.info(f"✅ Profile '{profile_name}' loaded successfully")

    def test_system_parameter_overrides_yaml(self):
        """
        Test that system parameters have highest priority over YAML.
        """
        _logger.info("[CEL TEST] Testing system parameter override")

        # Create a test system parameter
        custom_config = {
            "root_model": "custom.model",
            "base_domain": [["custom_field", "=", True]],
            "symbols": {"custom": {"model": "custom.model"}},
        }

        import json

        self.env["ir.config_parameter"].sudo().set_param("cel_domain.profile.test_custom", json.dumps(custom_config))

        # Load the custom profile
        config = self.registry.load_profile("test_custom")

        # Should use system parameter config
        self.assertEqual(config.get("root_model"), "custom.model")
        self.assertIn("custom", config.get("symbols", {}))

        # Clean up
        self.env["ir.config_parameter"].sudo().search([("key", "=", "cel_domain.profile.test_custom")]).unlink()

        _logger.info("✅ System parameter override works")

    def test_active_members_is_default(self):
        """
        Test that active members (is_ended=False) is the default for member queries.

        This is important: users don't need an active_members() function because
        it's already the default behavior!
        """
        _logger.info("[CEL TEST] Testing that active members is default")

        config = self.registry.load_profile("registry_groups")
        members_symbol = config.get("symbols", {}).get("members", {})

        # Should have default_domain
        self.assertIn("default_domain", members_symbol)

        # Should filter to active members by default
        default_domain = members_symbol.get("default_domain")
        self.assertEqual(
            default_domain,
            [["is_ended", "=", False]],
            "Members should be active by default (no need for active_members() function)",
        )

        _logger.info(
            "✅ Active members is the default! "
            "Users can use members.exists() and it automatically filters to active members."
        )

    def test_deep_merge_logic(self):
        """
        Test that the deep merge properly combines nested dictionaries.
        """
        _logger.info("[CEL TEST] Testing deep merge logic")

        base = {
            "root_model": "base.model",
            "symbols": {
                "me": {"model": "base.model"},
                "other": {"field": "base_field"},
            },
            "base_only": "value",
        }

        override = {
            "root_model": "override.model",  # Should override
            "symbols": {
                "me": {"model": "override.model"},  # Should override
                "new": {"model": "new.model"},  # Should add
            },
            "override_only": "value",  # Should add
        }

        result = self.registry._deep_merge(base, override)

        # Root level override
        self.assertEqual(result["root_model"], "override.model")

        # Nested override
        self.assertEqual(result["symbols"]["me"]["model"], "override.model")

        # Nested preservation
        self.assertEqual(result["symbols"]["other"]["field"], "base_field")

        # Nested addition
        self.assertIn("new", result["symbols"])

        # Top level preservation
        self.assertEqual(result["base_only"], "value")

        # Top level addition
        self.assertEqual(result["override_only"], "value")

        _logger.info("✅ Deep merge works correctly")

    def test_individuals_profile_has_groups_symbol(self):
        """
        Test that the Individuals profile has the 'groups' symbol
        (reverse relationship from groups profile's 'members').
        """
        _logger.info("[CEL TEST] Testing individuals profile groups symbol")

        config = self.registry.load_profile("registry_individuals")
        symbols = config.get("symbols", {})

        # Should have 'groups' symbol (Individual → Groups relationship)
        self.assertIn("groups", symbols, "Individuals profile should have 'groups' symbol")

        groups_symbol = symbols.get("groups", {})
        self.assertEqual(
            groups_symbol.get("through"), "g2p.group.membership", "Should use group.membership through model"
        )
        self.assertEqual(groups_symbol.get("parent"), "individual", "Should link from individual side")

        _logger.info("✅ Individuals can query their groups")
