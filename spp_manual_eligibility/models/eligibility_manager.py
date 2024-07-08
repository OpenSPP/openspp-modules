# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class DefaultEligibilityManager(models.Model):
    _inherit = "g2p.program_membership.manager.default"

    is_manual_eligibility = fields.Boolean(default=False)
