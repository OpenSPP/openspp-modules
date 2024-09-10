# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class G2PCycle(models.Model):
    _inherit = "g2p.cycle"

    is_manual_eligibility = fields.Boolean(related="program_id.is_manual_eligibility")
