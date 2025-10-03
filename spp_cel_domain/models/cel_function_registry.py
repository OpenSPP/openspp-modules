"""
CEL Function Registry - Dynamic function registration for extensibility.

Allows other modules to contribute CEL functions without depending on cel_domain.
"""

import logging
from typing import Any

from odoo import api, models

_logger = logging.getLogger(__name__)


class CelFunctionRegistry(models.AbstractModel):
    """
    Registry for dynamically registered CEL functions.

    Allows other modules to contribute functions without hard dependencies.
    Functions registered here take precedence over built-in functions.

    Usage in extension modules:
        # In spp_farmer/__init__.py post_init_hook:
        env['cel.function.registry'].register('crop_season', my_function)
    """

    _name = "cel.function.registry"
    _description = "CEL Function Registry"

    # Historically stored at class level; now kept per-registry to avoid cross-DB leaks.

    def _get_registry(self) -> dict[str, Any]:
        registry = self.env.registry
        funcs = getattr(registry, "_cel_functions", None)
        if funcs is None:
            funcs = {}
            registry._cel_functions = funcs
        return funcs

    @api.model
    def register(self, name, handler):
        """
        Register a CEL function.

        :param name: Function name (e.g., 'crop_season', 'is_harvest_time')
        :param handler: Callable that implements the function
        :return: True if registered successfully

        Example:
            def my_function(date_val):
                return date_val.year

            registry = env['cel.function.registry']
            registry.register('get_year', my_function)
        """
        if not callable(handler):
            _logger.error(f"[CEL Function Registry] Handler for '{name}' is not callable")
            return False

        registry_map = self._get_registry()

        if name in registry_map:
            _logger.warning(f"[CEL Function Registry] Overriding existing function '{name}'")

        registry_map[name] = handler
        _logger.info(f"[CEL Function Registry] Registered function '{name}'")
        return True

    @api.model
    def unregister(self, name):
        """
        Unregister a CEL function.

        :param name: Function name to remove
        :return: True if unregistered, False if not found
        """
        registry_map = self._get_registry()
        if name in registry_map:
            del registry_map[name]
            _logger.info(f"[CEL Function Registry] Unregistered function '{name}'")
            return True
        return False

    @api.model
    def get_handler(self, name):
        """
        Get function handler by name.

        :param name: Function name
        :return: Callable handler or None if not found
        """
        return self._get_registry().get(name)

    @api.model
    def is_registered(self, name):
        """
        Check if a function is registered.

        :param name: Function name
        :return: True if registered
        """
        return name in self._get_registry()

    @api.model
    def list_functions(self):
        """
        List all registered function names.

        :return: List of function name strings
        """
        return sorted(self._get_registry().keys())

    @api.model
    def clear_all(self):
        """
        Clear all registered functions.
        Useful for testing.

        :return: Number of functions cleared
        """
        registry_map = self._get_registry()
        count = len(registry_map)
        registry_map.clear()
        _logger.info(f"[CEL Function Registry] Cleared {count} function(s)")
        return count
