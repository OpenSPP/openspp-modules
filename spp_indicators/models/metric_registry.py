from __future__ import annotations

import logging
from typing import Any

from odoo import api, models

_logger = logging.getLogger(__name__)


_REGISTRY: dict[str, dict[str, Any]] = {}


class OpensppIndicatorRegistry(models.AbstractModel):
    _name = "openspp.indicator.registry"
    _description = "OpenSPP Metric Provider Registry"

    @api.model
    def register(
        self,
        name: str,
        handler: Any,
        *,
        return_type: str = "number",
        subject_model: str = "res.partner",
        id_mapping: dict[str, Any] | None = None,
        capabilities: dict[str, Any] | None = None,
        provider: str | None = None,
    ):
        """Register a metric provider handler under a qualified name.

        - name: dotted metric name, e.g., 'education.attendance_pct'
        - handler: object exposing compute_batch(env, ctx, subject_ids: list[int],
                   period_key: str, params: dict) -> dict[int, Any]
        - return_type: 'number' | 'string' | 'json'
        - subject_model: Odoo model name for subjects
        - id_mapping: configuration for mapping subject IDs (reserved for external systems)
        - capabilities: dict such as {'supports_batch': True, 'max_batch_size': 5000, 'default_ttl': 86400}
        """
        _REGISTRY[name] = {
            "handler": handler,
            "return_type": return_type,
            "subject_model": subject_model,
            "id_mapping": id_mapping or {},
            "capabilities": capabilities or {},
            "provider": provider or name,
        }
        _logger.info("[openspp.indicator] Registered indicator provider %s", name)

    @api.model
    def get(self, name: str) -> dict[str, Any] | None:
        return _REGISTRY.get(name)

    @api.model
    def list(self) -> dict[str, dict[str, Any]]:
        return dict(_REGISTRY)


# Static registration API (independent from Odoo env)
def register_static(
    name: str,
    handler: Any,
    *,
    return_type: str = "number",
    subject_model: str = "res.partner",
    id_mapping: dict[str, Any] | None = None,
    capabilities: dict[str, Any] | None = None,
    provider: str | None = None,
):
    _REGISTRY[name] = {
        "handler": handler,
        "return_type": return_type,
        "subject_model": subject_model,
        "id_mapping": id_mapping or {},
        "capabilities": capabilities or {},
        "provider": provider or name,
    }
    _logger.info("[openspp.indicator] (static) Registered indicator provider %s", name)
