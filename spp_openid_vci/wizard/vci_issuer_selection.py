from odoo import fields, models


class IssueCardWiz(models.TransientModel):
    _name = "spp.issue.card.wizard"

    partner_id = fields.Many2one("res.partner", "Registrant", required=True)
    issuer_id = fields.Many2one("g2p.openid.vci.issuers", "Issuer", required=True)

    def issue_card(self):
        self.ensure_one()
        return self.partner_id._issue_vc_qr(self.issuer_id)
