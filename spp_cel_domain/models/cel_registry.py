import json
import logging
import os

from odoo import api, models
from odoo.tools.misc import file_path

_logger = logging.getLogger(__name__)


DEFAULT_PRESETS = {
    "registry_individuals": {
        "root_model": "res.partner",
        "base_domain": [["is_registrant", "=", True], ["is_group", "=", False]],
        "m2o_name_match": "equals",
        "symbols": {
            "me": {"model": "res.partner"},
            "enrollments": {
                "relation": "rel",
                "through": "g2p.program_membership",
                "parent": "partner_id",
                "link_field": "id",
                "child_model": "g2p.program_membership",
            },
            "entitlements": {
                "relation": "rel",
                "through": "g2p.entitlement",
                "parent": "partner_id",
                "link_field": "id",
                "child_model": "g2p.entitlement",
            },
        },
    },
    "registry_groups": {
        "root_model": "res.partner",
        "base_domain": [["is_registrant", "=", True], ["is_group", "=", True]],
        "m2o_name_match": "equals",
        "symbols": {
            "me": {"model": "res.partner"},
            "members": {
                "relation": "rel",
                "through": "g2p.group.membership",
                "parent": "group",
                "link_to": "individual",
                "default_domain": [["is_ended", "=", False]],
            },
            "enrollments": {
                "relation": "rel",
                "through": "g2p.program_membership",
                "parent": "partner_id",
                "link_field": "id",
                "child_model": "g2p.program_membership",
            },
            "entitlements": {
                "relation": "rel",
                "through": "g2p.entitlement",
                "parent": "partner_id",
                "link_field": "id",
                "child_model": "g2p.entitlement",
            },
        },
        "roles": {"head": ["Head", "Household Head", "HoH"]},
    },
    "program_memberships": {
        "root_model": "g2p.program_membership",
        "symbols": {
            "me": {"model": "g2p.program_membership"},
            "registrant": {"relation": "many2one", "field": "partner_id", "model": "res.partner"},
            "program": {"relation": "many2one", "field": "program_id", "model": "g2p.program"},
        },
    },
    "entitlements": {
        "root_model": "g2p.entitlement",
        "symbols": {
            "me": {"model": "g2p.entitlement"},
            "registrant": {"relation": "many2one", "field": "partner_id", "model": "res.partner"},
            "program": {"relation": "many2one", "field": "program_id", "model": "g2p.program"},
        },
    },
}


class CelRegistry(models.AbstractModel):
    _name = "cel.registry"
    _description = "CEL Symbol Registry"

    @api.model
    def load_profile(self, profile: str) -> dict:
        """
        Load a CEL profile configuration from multiple sources (in priority order):
        1. System parameter (ir.config_parameter) - highest priority
        2. YAML file in module's data/ directory
        3. Hardcoded DEFAULT_PRESETS - lowest priority (fallback)

        YAML profiles override/merge with defaults.
        """
        # Priority 1: System parameter (for admin customization)
        params = self.env["ir.config_parameter"]
        key = f"cel_domain.profile.{profile}"
        raw = params.sudo().get_param(key)
        if raw:
            try:
                config = json.loads(raw)
                _logger.info(f"[CEL Registry] Loaded profile '{profile}' from system parameter")
                return config
            except Exception as e:
                _logger.warning(f"[CEL Registry] Failed to parse system parameter for profile '{profile}': {e}")

        # Priority 2: YAML file (for deployment customization)
        yaml_config = self._load_yaml_profiles()
        if yaml_config and profile in yaml_config:
            yaml_profile = yaml_config[profile]
            # Merge with defaults (YAML overrides defaults)
            default_profile = DEFAULT_PRESETS.get(profile, {})
            merged = self._deep_merge(default_profile, yaml_profile)
            _logger.info(f"[CEL Registry] Loaded profile '{profile}' from YAML (merged with defaults)")
            return merged

        # Priority 3: Hardcoded defaults (fallback)
        if profile in DEFAULT_PRESETS:
            _logger.debug(f"[CEL Registry] Using hardcoded defaults for profile '{profile}'")
            return DEFAULT_PRESETS[profile]

        _logger.warning(f"[CEL Registry] Profile '{profile}' not found in any source")
        return {}

    @api.model
    def _load_yaml_profiles(self) -> dict:
        """
        Load profile configurations from YAML files in ALL installed modules.

        Scans for 'data/cel_profiles.yaml' in every installed module,
        allowing modules to contribute CEL profiles without depending on cel_domain.

        Returns dict of profile_name -> config, or empty dict if no profiles found.
        Later modules can override profiles from earlier modules.
        """
        try:
            # Try importing PyYAML
            try:
                import yaml
            except ImportError:
                _logger.warning("[CEL Registry] PyYAML not installed, YAML configuration disabled")
                return {}

            all_profiles = {}
            modules_with_profiles = []

            # First, load from cel_domain itself (for backward compatibility)
            module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cel_domain_yaml = os.path.join(module_path, "data", "cel_symbols.template.yaml")

            if os.path.exists(cel_domain_yaml):
                try:
                    with open(cel_domain_yaml, encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if data and isinstance(data, dict):
                            presets = data.get("presets", {})
                            if presets:
                                all_profiles.update(presets)
                                modules_with_profiles.append("cel_domain")
                except Exception as e:
                    _logger.warning(f"[CEL Registry] Error loading cel_domain YAML: {e}")

            # Then, scan ALL installed modules for cel_profiles.yaml
            try:
                # Get all installed modules
                IrModule = self.env["ir.module.module"]
                installed_modules = IrModule.search([("state", "=", "installed")])

                for module in installed_modules:
                    if module.name == "cel_domain":
                        continue  # Already loaded above

                    try:
                        # Look for cel_profiles.yaml in this module using the supported helper
                        yaml_path = file_path(f"{module.name}/data/cel_profiles.yaml")

                        with open(yaml_path, encoding="utf-8") as f:
                            data = yaml.safe_load(f)

                        if data and isinstance(data, dict):
                            presets = data.get("presets", {})
                            if presets and isinstance(presets, dict):
                                # Merge profiles from this module
                                all_profiles.update(presets)
                                modules_with_profiles.append(module.name)
                                _logger.info(f"[CEL Registry] Loaded {len(presets)} profile(s) from {module.name}")
                    except FileNotFoundError:
                        # Module does not expose CEL profiles; skip quietly
                        continue
                    except Exception as e:
                        _logger.debug(f"[CEL Registry] No CEL profiles in {module.name}: {e}")

            except Exception as e:
                _logger.warning(f"[CEL Registry] Error scanning modules for profiles: {e}")

            if all_profiles:
                _logger.info(
                    f"[CEL Registry] Loaded {len(all_profiles)} profile(s) from YAML: "
                    f"{list(all_profiles.keys())} (from modules: {', '.join(modules_with_profiles)})"
                )
            else:
                _logger.debug("[CEL Registry] No YAML profiles found in any module")

            return all_profiles

        except Exception as e:
            _logger.error(f"[CEL Registry] Error loading YAML profiles: {e}", exc_info=True)
            return {}

    @api.model
    def _deep_merge(self, base: dict, override: dict) -> dict:
        """
        Deep merge two dictionaries. Override values take precedence.
        Used to merge YAML profiles with hardcoded defaults.
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override takes precedence
                result[key] = value

        return result

    @api.model
    def profile_root_model(self, profile: str) -> str:
        cfg = self.load_profile(profile)
        return cfg.get("root_model")
