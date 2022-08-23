# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from lxml import etree

from odoo import fields, models


class G2PProgramMembership(models.Model):
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # TODO: rename g2p.program_membership to g2p.program.beneficiaries
    _name = "g2p.program_membership"
    _description = "Program Membership"
    _order = "id desc"

    partner_id = fields.Many2one(
        "res.partner",
        "Registrant",
        help="A beneficiary",
        required=True,
        domain=[("is_registrant", "=", True)],
    )
    program_id = fields.Many2one("g2p.program", "", help="A program", required=True)

    # TODO: When the state is changed from "exited", "not_eligible" or "duplicate" to something else
    #      then reset the deduplication date.
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("enrolled", "Enrolled"),
            ("paused", "Paused"),
            ("exited", "Exited"),
            ("not_eligible", "Not Eligible"),
            ("duplicated", "Duplicated"),
        ],
        default="draft",
        copy=False,
    )

    enrollment_date = fields.Date(default=lambda self: fields.Datetime.now())
    last_deduplication = fields.Date("Last Deduplication Date")
    exit_date = fields.Date()

    _sql_constraints = [
        (
            "program_membership_unique",
            "unique (partner_id, program_id)",
            "Beneficiary must be unique per program.",
        ),
    ]

    # TODO: Implement exit reasons
    # exit_reason_id = fields.Many2one("Exit Reason") Default: Completed, Opt-Out, Other

    # TODO: Implement not eligible reasons
    # Default: "Missing data", "Does not match the criterias", "Duplicate", "Other"
    # not_eligible_reason_id = fields.Many2one("Not Eligible Reason")

    # TODO: Add a field delivery_mechanism_id
    # delivery_mechanism_id = fields.Many2one("Delivery mechanism type", help="Delivery mechanism")
    # the phone number, bank account, etc.
    delivery_mechanism_value = fields.Char()

    # TODO: JJ - Add a field for the preferred notification method

    deduplication_status = fields.Selection(
        selection=[
            ("new", "New"),
            ("processing", "Processing"),
            ("verified", "Verified"),
            ("duplicated", "duplicated"),
        ],
        default="new",
        copy=False,
    )

    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        context = self.env.context
        result = super(G2PProgramMembership, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if view_type == "form":
            update_arch = False
            doc = etree.XML(result["arch"])

            # Check if we need to change the partner_id domain filter
            target_type = context.get("target_type", False)
            if target_type:
                domain = None
                if context.get("target_type", False) == "group":
                    domain = "[('is_registrant', '=', True), ('is_group','=',True)]"
                elif context.get("target_type", False) == "individual":
                    domain = "[('is_registrant', '=', True), ('is_group','=',False)]"
                if domain:
                    update_arch = True
                    nodes = doc.xpath("//field[@name='partner_id']")
                    for node in nodes:
                        node.set("domain", domain)

            if update_arch:
                result["arch"] = etree.tostring(doc, encoding="unicode")
        return result

    def name_get(self):
        res = super(G2PProgramMembership, self).name_get()
        for rec in self:
            name = ""
            if rec.program_id:
                name += "[" + rec.program_id.name + "] "
            if rec.partner_id:
                name += rec.partner_id.name
            res.append((rec.id, name))
        return res

    def open_beneficiaries_form(self):
        for rec in self:
            return {
                "name": "Program Beneficiaries",
                "view_mode": "form",
                "res_model": "g2p.program_membership",
                "res_id": rec.id,
                "view_id": self.env.ref("g2p_programs.view_program_membership_form").id,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": {
                    "target_type": rec.program_id.target_type,
                    "default_program_id": rec.program_id.id,
                },
            }

    def open_registrant_form(self):
        if self.partner_id.is_group:
            return {
                "name": "Group Member",
                "view_mode": "form",
                "res_model": "res.partner",
                "res_id": self.partner_id.id,
                "view_id": self.env.ref("g2p_registry_group.view_groups_form").id,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": {"default_is_group": True},
                "flags": {"mode": "readonly"},
            }
        else:
            return {
                "name": "Individual Member",
                "view_mode": "form",
                "res_model": "res.partner",
                "res_id": self.partner_id.id,
                "view_id": self.env.ref(
                    "g2p_registry_individual.view_individuals_form"
                ).id,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": {"default_is_group": False},
                "flags": {"mode": "readonly"},
            }
