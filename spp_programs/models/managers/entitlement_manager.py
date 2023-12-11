# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class BaseEntitlementManager(models.AbstractModel):
    _inherit = "g2p.base.program.entitlement.manager"

    id_type = fields.Many2one("g2p.id.type", "ID Type to store in entitlements")
