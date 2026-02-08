from __future__ import annotations

from odoo import api, fields, models


class IndicatorsRegistryInspect(models.TransientModel):
    _name = "openspp.indicator.registry.inspect"
    _description = "Indicator Runtime Registry"

    line_ids = fields.One2many("openspp.indicator.registry.inspect.line", "wizard_id", string="Entries")

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        lines = []
        reg = self.env["openspp.indicator.registry"]
        data = reg.list() or {}
        for name, info in sorted(data.items()):
            id_fields = []
            idmap = (info or {}).get("id_mapping") or {}
            if isinstance(idmap, dict):
                id_fields = idmap.get("fields") or []
            caps = (info or {}).get("capabilities") or {}
            lines.append(
                (
                    0,
                    0,
                    {
                        "name": name,
                        "provider": (info or {}).get("provider") or name,
                        "subject_model": (info or {}).get("subject_model") or "res.partner",
                        "return_type": (info or {}).get("return_type") or "number",
                        "id_mapping_fields": ",".join(id_fields),
                        "max_batch_size": int(caps.get("max_batch_size") or 0),
                        "default_ttl": int(caps.get("default_ttl") or 0),
                    },
                )
            )
        vals["line_ids"] = lines
        return vals


class IndicatorsRegistryInspectLine(models.TransientModel):
    _name = "openspp.indicator.registry.inspect.line"
    _description = "Indicator Runtime Registry Entry"

    wizard_id = fields.Many2one("openspp.indicator.registry.inspect", ondelete="cascade")
    name = fields.Char(required=True)
    provider = fields.Char()
    subject_model = fields.Char()
    return_type = fields.Char()
    id_mapping_fields = fields.Char()
    max_batch_size = fields.Integer()
    default_ttl = fields.Integer()
