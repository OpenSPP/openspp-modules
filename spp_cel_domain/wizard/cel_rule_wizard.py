from odoo import api, fields, models


class CelRuleWizard(models.TransientModel):
    _name = "cel.rule.wizard"
    _description = "CEL Rule Preview"

    profile = fields.Selection(
        selection=[
            ("registry_individuals", "Registry / Individuals"),
            ("registry_groups", "Registry / Groups"),
            ("program_memberships", "Program Memberships"),
            ("entitlements", "Entitlements"),
        ],
        default="registry_groups",
        required=True,
    )
    model_id = fields.Many2one("ir.model", string="Target Model", required=True)
    cel_expression = fields.Text(string="CEL Expression", required=True)

    result_domain_text = fields.Text(readonly=True)
    explain_text = fields.Text(readonly=True)
    metrics_explain_text = fields.Text(readonly=True)
    metric_line_ids = fields.One2many("cel.rule.wizard.metric", "wizard_id", string="Metrics", readonly=True)
    preview_count = fields.Integer(readonly=True)
    # For now, surface sample records for the common Individuals use case
    # (res.partner). This can be extended to other models later.
    sample_ids = fields.Many2many("res.partner", string="Sample IDs", readonly=True)

    @api.onchange("profile")
    def _onchange_profile(self):
        if self.profile:
            model = self.env["cel.registry"].profile_root_model(self.profile)
            if model:
                self.model_id = self.env["ir.model"].search([("model", "=", model)], limit=1)

    def action_validate_preview(self):
        self.ensure_one()
        registry = self.env["cel.registry"]
        # Clear previous results
        self.result_domain_text = ""
        self.explain_text = ""
        self.preview_count = 0
        self.sample_ids = [(5, 0, 0)]

        # Build context config by profile
        cfg = registry.load_profile(self.profile)
        executor = self.env["cel.executor"].with_context(cel_profile=self.profile, cel_cfg=cfg)

        try:
            # Translate + execute
            result = executor.compile_and_preview(self.model_id.model, self.cel_expression, limit=50)
            self.result_domain_text = result.get("domain_text")
            self.explain_text = result.get("explain")
            exp = self.explain_text or ""
            marker = " | Metrics: "
            metrics_addendum = exp.split(marker, 1)[1] if marker in exp else ""
            # Append simple warnings if present in struct
            warnings_lines = []
            for mi in (result.get("explain_struct") or {}).get("metrics", []) or []:
                w = mi.get("warnings") or []
                if w:
                    warnings_lines.append(f"{mi.get('metric')}@{mi.get('period_key')}: {', '.join(w)}")
            if warnings_lines:
                metrics_addendum = (
                    metrics_addendum + ("; " if metrics_addendum else "") + "Warnings: " + "; ".join(warnings_lines)
                )
            self.metrics_explain_text = metrics_addendum
            self.preview_count = result.get("count")
            # Populate structured metrics lines
            lines = []
            for mi in (result.get("explain_struct") or {}).get("metrics", []) or []:
                lines.append(
                    (
                        0,
                        0,
                        {
                            "metric": mi.get("metric"),
                            "period_key": mi.get("period_key"),
                            "requested": mi.get("requested", 0),
                            "cache_hits": mi.get("cache_hits", 0),
                            "misses": mi.get("misses", 0),
                            "fresh_fetches": mi.get("fresh_fetches", 0),
                            "coverage": mi.get("coverage", 0.0),
                        },
                    )
                )
            if lines:
                self.metric_line_ids = [(5, 0, 0)] + lines
            else:
                self.metric_line_ids = [(5, 0, 0)]
            # Populate sample_ids for Individuals profile (res.partner)
            if self.model_id.model == "res.partner":
                self.sample_ids = [(6, 0, result.get("ids", []))]
            else:
                self.sample_ids = [(5, 0, 0)]
            return self._show_success(f"{self.preview_count} matching records")

        except SyntaxError as e:
            error_msg = str(e)
            pos = getattr(e, "offset", None)
            friendly_msg = "Syntax Error"
            if pos:
                friendly_msg += f" at position {pos}"
            friendly_msg += f": {error_msg}\n\nPlease check your expression for typos or missing parentheses."
            self.explain_text = friendly_msg
            return self._show_error("Invalid Syntax", friendly_msg)

        except KeyError as e:
            symbol = str(e).strip("'\"")
            available = list(cfg.get("symbols", {}).keys())
            suggestion = self._suggest_symbol(symbol, available)
            msg = f"Unknown symbol '{symbol}'."
            if suggestion:
                msg += f" Did you mean '{suggestion}'?"
            msg += f"\n\nAvailable symbols for {self.profile} profile: {', '.join(available)}"
            self.explain_text = msg
            return self._show_error("Unknown Symbol", msg)

        except NotImplementedError as e:
            msg = str(e)
            self.explain_text = f"Not Supported: {msg}"
            return self._show_error("Feature Not Supported", msg)

        except AttributeError as e:
            error_msg = str(e)
            msg = f"Invalid expression: {error_msg}\n\n"
            msg += "This usually means you're trying to access a field that doesn't exist. "
            msg += "Check field names and make sure you're using the correct profile."
            self.explain_text = msg
            return self._show_error("Invalid Field Access", msg)

        except Exception as e:
            error_msg = str(e)
            self.explain_text = f"Error: {error_msg}\n\nIf you need help, please contact support."
            return self._show_error("Processing Error", error_msg)

    def _suggest_symbol(self, wrong_symbol, available_symbols):
        """Simple string similarity for suggestions using difflib."""
        if not available_symbols:
            return None
        import difflib

        matches = difflib.get_close_matches(wrong_symbol, available_symbols, n=1, cutoff=0.6)
        return matches[0] if matches else None

    def _show_error(self, title, message):
        """Show error notification to user."""
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": title,
                "message": message,
                "type": "warning",
                "sticky": True,
            },
        }

    def _show_success(self, message):
        """Show success notification to user."""
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "CEL Preview",
                "message": message,
                "type": "success",
                "sticky": False,
            },
        }


class CelRuleWizardMetric(models.TransientModel):
    _name = "cel.rule.wizard.metric"
    _description = "CEL Preview Metric Explain Line"

    wizard_id = fields.Many2one("cel.rule.wizard", required=True, ondelete="cascade")
    metric = fields.Char(required=True)
    period_key = fields.Char()
    requested = fields.Integer()
    cache_hits = fields.Integer()
    misses = fields.Integer()
    fresh_fetches = fields.Integer()
    coverage = fields.Float()
