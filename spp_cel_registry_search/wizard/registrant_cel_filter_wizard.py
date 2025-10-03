from odoo import fields, models


class RegistrantCelFilterWizard(models.TransientModel):
    _name = "cel.registrant.filter.wizard"
    _description = "CEL Filter for Registry"

    profile = fields.Selection(
        selection=[
            ("registry_individuals", "Individuals"),
            ("registry_groups", "Groups"),
        ],
        default=lambda self: self.env.context.get("default_profile", "registry_individuals"),
        required=True,
    )
    cel_expression = fields.Text(required=True)
    result_domain_text = fields.Text(readonly=True)
    explain_text = fields.Text(readonly=True)
    preview_count = fields.Integer(readonly=True)

    def _compile(self):
        cfg = self.env["cel.registry"].load_profile(self.profile)
        model = cfg.get("root_model", "res.partner")
        ex = self.env["cel.executor"].with_context(cel_profile=self.profile, cel_cfg=cfg)
        return ex.compile_and_preview(model, self.cel_expression, limit=0)

    def action_preview(self):
        self.ensure_one()
        res = self._compile()
        self.result_domain_text = res.get("domain_text")
        self.explain_text = res.get("explain")
        self.preview_count = res.get("count")
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "CEL",
                "message": f"Found {self.preview_count} records",
                "type": "success",
                "sticky": False,
            },
        }

    def action_open_list(self):
        self.ensure_one()
        cfg = self.env["cel.registry"].load_profile(self.profile)
        model = cfg.get("root_model", "res.partner")
        res = self._compile()
        domain = res.get("domain") or []
        return {
            "type": "ir.actions.act_window",
            "name": f"{dict(self._fields['profile'].selection).get(self.profile)} (CEL)",
            "res_model": model,
            "view_mode": "tree,form",
            "domain": domain,
            "target": "current",
            "context": {},
        }
