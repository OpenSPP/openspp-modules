import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SPPGroupMembership(models.Model):
    _inherit = "g2p.group.membership"

    individual_domain = fields.Binary(
        compute="_compute_individual_domain",
        readonly=True,
        store=False,
    )

    @api.depends("group", "group.kind")
    def _compute_individual_domain(self):
        """
        Called whenever kind field is changed

        This method is used for dynamic domain of individual field
        """
        for rec in self:
            domain = [("is_group", "=", False), ("is_registrant", "=", True)]
            if rec.group and rec.group.kind and rec.group.kind.allow_all_member_type:
                if rec.group:
                    try:
                        group_id = int(rec.group.id)
                    except Exception:
                        group_id = rec.group._origin.id
                    domain = [("is_registrant", "=", True), ("id", "!=", group_id)]
            rec.individual_domain = domain
