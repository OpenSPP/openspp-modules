# Part of Newlogic OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class G2PCycle(models.Model):
    _inherit = "g2p.cycle"

    picking_ids = fields.One2many(
        "stock.picking", "cycle_id", string="In-kind Stock Transfers"
    )
    procurement_group_id = fields.Many2one("procurement.group", "Procurement Group")
