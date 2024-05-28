from odoo import api, fields, models


class MultiInKindEntitlementApprovalWiz(models.TransientModel):
    _name = "spp.multi.inkind.entitlement.approval.wizard"
    _description = "Multi In-Kind Entitlement Approval Wizard"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get("active_ids"):
            entitlement_ids = []
            for rec in self.env.context.get("active_ids"):
                entitlement = self.env["g2p.entitlement.inkind"].search(
                    [
                        ("id", "=", rec),
                    ]
                )
                if entitlement.state in ("draft", "pending_validation"):
                    entitlement_ids.append([0, 0, {"entitlement_id": rec}])
            res["entitlement_ids"] = entitlement_ids

        return res

    entitlement_ids = fields.One2many(
        "spp.multi.inkind.entitlement.approval",
        "wizard_id",
        string="Entitlements",
        required=True,
    )

    def approve_entitlements(self):
        if self.entitlement_ids:
            self.entitlement_ids.entitlement_id.approve_entitlement()

    def open_wizard(self):
        return {
            "name": "Multiple Inkind Entitlements Approval",
            "view_mode": "form",
            "res_model": "spp.multi.inkind.entitlement.approval.wizard",
            "view_id": self.env.ref("spp_programs.multi_inkind_entitlement_approval_wizard_form_view").id,
            "type": "ir.actions.act_window",
            "target": "new",
            "nodestroy": True,
            "context": self.env.context,
        }

    def close_wizard(self):
        return {"type": "ir.actions.act_window_close"}


class MultiInKindEntitlementApproval(models.TransientModel):
    _name = "spp.multi.inkind.entitlement.approval"
    _description = "In-Kind Entitlement Approval"

    entitlement_id = fields.Many2one(
        "g2p.entitlement.inkind",
        "In-kind Entitlement",
        required=True,
    )

    wizard_id = fields.Many2one(
        "spp.multi.inkind.entitlement.approval.wizard",
        "Multi In-kind Entitlement Approval Wizard",
        required=True,
    )

    partner_id = fields.Many2one(
        "res.partner",
        "Registrant",
        related="entitlement_id.partner_id",
    )
    code = fields.Char(related="entitlement_id.code")

    product_id = fields.Many2one(
        "product.product",
        "Product",
        related="entitlement_id.product_id",
    )

    qty = fields.Integer("QTY", related="entitlement_id.qty")
    currency_id = fields.Many2one("res.currency", related="entitlement_id.currency_id")
    unit_price = fields.Monetary(string="Value/Unit", currency_field="currency_id", related="entitlement_id.unit_price")
    total_amount = fields.Monetary(
        string="Total Value", currency_field="currency_id", related="entitlement_id.total_amount"
    )

    state = fields.Selection(
        [
            ("New", "New"),
            ("Okay", "Okay"),
            ("Conflict", "Conflict"),
            ("Approved", "Approved"),
        ],
        "Status",
        readonly=True,
        default="New",
    )
