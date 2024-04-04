from odoo import api, models


class CustomOpenIDVCIssuer(models.Model):
    _inherit = "g2p.openid.vci.issuers"

    @api.constrains("auth_allowed_issuers", "issuer_type")
    def onchange_auth_allowed_issuers(self):
        for rec in self:
            if not rec.auth_allowed_issuers:
                args = [rec, f"set_default_auth_allowed_issuers_{rec.issuer_type}"]
                if hasattr(*args):
                    getattr(*args)()
