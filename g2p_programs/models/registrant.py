# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class G2PRegistrant(models.Model):
    _inherit = "res.partner"

    # Custom Fields
    program_membership_ids = fields.One2many(
        "g2p.program_membership", "partner_id", "Program Memberships"
    )
    cycle_ids = fields.One2many(
        "g2p.cycle.membership", "partner_id", "Cycle Memberships"
    )
    entitlement_ids = fields.One2many("g2p.entitlement", "partner_id", "Entitlements")
