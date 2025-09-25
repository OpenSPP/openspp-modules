from odoo import _, fields, models
from odoo.exceptions import UserError


class G2PGroupMembership(models.Model):
    _inherit = "g2p.group.membership"

    individual_gender = fields.Many2one("gender.type", related="individual.gender", readonly=True)

    def unlink(self):
        # Skip head check if specified in context
        if self.env.context.get("skip_head_check"):
            return super().unlink()

        # Group records by their group to check head members
        groups_to_check = self.mapped("group")

        # Perform the unlink operation
        result = super().unlink()

        # Check if any group lost its head member
        for group in groups_to_check:
            if (
                self.env.ref("g2p_registry_membership.group_membership_kind_head").id
                not in group.group_membership_ids.mapped("kind").ids
            ):
                raise UserError(_("Farm must have a head member."))

        return result
