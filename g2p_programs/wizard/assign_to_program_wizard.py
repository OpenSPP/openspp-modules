# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class G2PAssignToProgramWizard(models.TransientModel):
    _name = "g2p.assign.program.wizard"
    _description = "Add Registrants to Program Wizard"

    @api.model
    def default_get(self, fields):
        res = super(G2PAssignToProgramWizard, self).default_get(fields)
        if self.env.context.get("active_ids"):
            # Get the first selected registrant and check if group or individual
            partner_id = self.env.context.get("active_ids")[0]
            registrant = self.env["res.partner"].search(
                [
                    ("id", "=", partner_id),
                ]
            )
            target_type = "group" if registrant.is_group else "individual"
            res["target_type"] = target_type
            return res
        else:
            raise UserError(_("There are no selected registrants!"))

    target_type = fields.Selection(
        selection=[("group", "Group"), ("individual", "Individual")]
    )
    program_id = fields.Many2one(
        "g2p.program",
        "",
        domain="[('target_type', '=', target_type)]",
        help="A program",
        required=True,
    )

    def assign_registrant(self):
        if self.env.context.get("active_ids"):
            partner_ids = self.env.context.get("active_ids")
            _logger.info(
                "Adding to Program Wizard with registrant record IDs: %s" % partner_ids
            )
            ctr = 0
            ig_ctr = 0
            ok_ctr = 0
            for rec in self.env["res.partner"].search([("id", "in", partner_ids)]):
                if self.program_id not in rec.program_membership_ids.program_id:
                    ctr += 1
                    _logger.info("Processing (%s): %s" % (ctr, rec.name))
                    proceed = False
                    if rec.is_group:  # Get only group registrants
                        if self.target_type == "group":
                            proceed = True
                        else:
                            ig_ctr += 1
                            _logger.info(
                                "Ignored because registrant is not a group: %s"
                                % rec.name
                            )
                    else:  # Get only individual registrants
                        if self.target_type == "individual":
                            proceed = True
                        else:
                            ig_ctr += 1
                            _logger.info(
                                "Ignored because registrant is not an individual: %s"
                                % rec.name
                            )
                    if proceed:
                        ok_ctr += 1
                        vals = {
                            "partner_id": rec.id,
                            "program_id": self.program_id.id,
                        }
                        _logger.info("Adding to Program Membership: %s" % vals)
                        self.env["g2p.program_membership"].create(vals)
                else:
                    ig_ctr += 1
                    _logger.info(
                        "%s was ignored because the registrant is already in the Program %s"
                        % (rec.name, self.program_id.name)
                    )
            _logger.info(
                "Total selected registrants:%s, Total ignored:%s, Total added to group:%s"
                % (ctr, ig_ctr, ok_ctr)
            )

    def open_wizard(self):

        _logger.info("Registrant IDs: %s" % self.env.context.get("active_ids"))
        return {
            "name": "Add to Program",
            "view_mode": "form",
            "res_model": "g2p.assign.program.wizard",
            "view_id": self.env.ref(
                "g2p_programs.assign_to_program_wizard_form_view"
            ).id,
            "type": "ir.actions.act_window",
            "target": "new",
            "context": self.env.context,
        }


class G2PAssignToProgramRegistrants(models.TransientModel):
    _name = "g2p.assign.program.registrants"
    _description = "Registrant Assign to Program"

    state = fields.Selection(
        [
            ("New", "New"),
            ("Okay", "Okay"),
            ("Conflict", "Conflict"),
            ("Assigned", "Assigned"),
        ],
        "Status",
        readonly=True,
        default="New",
    )
