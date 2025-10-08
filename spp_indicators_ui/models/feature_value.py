import json

from odoo import fields, models


class OpensppIndicatorValueUI(models.Model):
    _inherit = "openspp.indicator.value"

    value_text = fields.Char(string="Value", compute="_compute_value_text")
    value_pretty = fields.Text(string="Value (pretty)", compute="_compute_value_pretty")

    def _compute_value_text(self):
        for rec in self:
            v = rec.value_json
            display = ""
            try:
                if isinstance(v, int | float):
                    display = str(v)
                elif isinstance(v, str):
                    display = v
                elif isinstance(v, dict):
                    if "value" in v and isinstance(v["value"], int | float | str):
                        display = str(v["value"])
                    else:
                        display = json.dumps(v, ensure_ascii=False, sort_keys=True)
                elif isinstance(v, list):
                    display = json.dumps(v, ensure_ascii=False)
                else:
                    display = "" if v is None else str(v)
            except Exception:
                display = "" if v is None else str(v)
            # Keep it short in list view
            rec.value_text = display[:512] if display else ""

    def _compute_value_pretty(self):
        for rec in self:
            v = rec.value_json
            try:
                if isinstance(v, int | float):
                    rec.value_pretty = str(v)
                elif isinstance(v, str):
                    rec.value_pretty = v
                else:
                    rec.value_pretty = json.dumps(v, ensure_ascii=False, indent=2)
            except Exception:
                rec.value_pretty = "" if v is None else str(v)
