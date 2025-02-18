import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SPPGroupMembership(models.Model):
    _inherit = "spp.change.request.group.members"

    group_add_group_to_group_id = fields.Many2one("spp.change.request.add.group.to.group")
    individual_id = fields.Many2one(
        "res.partner",
        string="Registrant",
        domain=lambda self: self._compute_individual_domain(),
    )

    def _compute_individual_domain(self):
        """Compute domain for individual_id field to filter available registrants"""
        domain = [
            ("is_group", "=", True),
            ("is_registrant", "=", True),
            ("individual_membership_ids", "=", False),
        ]

        return domain
