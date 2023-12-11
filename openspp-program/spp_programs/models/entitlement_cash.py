# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class CashEntitlement(models.Model):
    _inherit = "g2p.entitlement"

    id_number = fields.Char()
