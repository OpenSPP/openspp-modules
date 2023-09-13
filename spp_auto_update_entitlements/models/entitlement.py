# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SPPEntitlement(models.Model):
    _inherit = "g2p.entitlement"

    state = fields.Selection(
        selection_add=[("parrdpd2ben", "Partially Redeemed/Paid to Beneficiary")]
    )
    transaction_ids = fields.One2many(
        "spp.entitlement.transactions", "entitlement_id", "Transactions"
    )
