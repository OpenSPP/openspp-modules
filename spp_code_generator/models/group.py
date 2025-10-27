import logging

from odoo import models

_logger = logging.getLogger(__name__)


class GroupRegistry(models.Model):
    _inherit = "res.partner"

    def _exec(self, expr, profile="registry_individuals"):
        """Helper to execute CEL expression."""
        registry = self.env["cel.registry"]
        cfg = registry.load_profile(profile)
        executor = self.env["cel.executor"].with_context(cel_profile=profile, cel_cfg=cfg)
        model = cfg.get("root_model", "res.partner")
        return executor.compile_and_preview(model, expr, limit=50)

    def compute_count_and_set_indicator(self, field_name, kinds, domain, presence_only=False, cel_expression=None):
        if cel_expression:
            domain += self._exec(cel_expression, profile="registry_groups").get("domain", [])
            _logger.info(f"CEL expression: {cel_expression} \n => domain: {domain}")
        return super().compute_count_and_set_indicator(field_name, kinds, domain, presence_only, cel_expression=None)
