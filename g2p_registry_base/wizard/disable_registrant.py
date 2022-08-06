# Part of Newlogic G2P. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class G2PDisableRegistryWiz(models.TransientModel):
    _name = "g2p.disable.registrant.wizard"
    _description = "Disable Registrant Wizard"

    @api.model
    def default_get(self, fields):
        res = super(G2PDisableRegistryWiz, self).default_get(fields)
        if self.env.context.get("active_id"):
            res["partner_id"] = self.env.context["active_id"]
        return res

    partner_id = fields.Many2one("res.partner", "Registrant", required=True)
    disabled_reason = fields.Text("Reason for disabling", required=True)

    def disable_registrant(self):
        group_mem_ids = self.env["g2p.group.membership"].search(
            [
                ("individual", "=", self.partner_id.id),
                ("end_date", ">", fields.Date.today()),
            ]
        )
        program_mem_ids = self.env["g2p.program_membership"].search(
            [
                ("partner_id", "=", self.partner_id.id),
                ("program_id.state", "!=", "ended"),
            ]
        )

        not_expired_group_name = []
        for line in group_mem_ids:
            if line:
                not_expired_group_name.append(line.group.name)
            else:
                pass

        active_program_name = []
        for prog in active_program_name:
            if prog:
                active_program_name.append(prog.program_id.name)
            else:
                pass

        for rec in self:
            if any(not_expired for not_expired in group_mem_ids):
                raise ValidationError(
                    _("Still part of group membership in: %s.")
                    % ",".join(map(str, not_expired_group_name))
                )

            elif any(active_prog for active_prog in program_mem_ids):
                raise ValidationError(
                    _("The program is not ended yet. Please check in program: %s.")
                    % ",".join(map(str, active_program_name))
                )

            else:
                rec.partner_id.update(
                    {
                        "disabled": fields.Datetime.now(),
                        "disabled_reason": rec.disabled_reason,
                        "disabled_by": self.env.user,
                    }
                )
