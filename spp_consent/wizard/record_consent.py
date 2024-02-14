# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OpenSPPRecordConsentWizard(models.TransientModel):
    _name = "spp.record.consent.wizard"
    _description = "Record Consent Wizard"

    name = fields.Char("Consent", compute="_compute_name")
    group_id = fields.Many2one(
        "res.partner",
        "Group",
        domain=[("is_registrant", "=", True), ("is_group", "=", True)],
    )
    signatory_id = fields.Many2one(
        "res.partner",
        "Signatory",
        domain=[("is_registrant", "=", True), ("is_group", "=", False)],
    )
    expiry = fields.Date("Expiry Date")
    is_group = fields.Boolean("Consent For Group", default=False)
    config_id = fields.Many2one("spp.consent.config", "Config")

    def _get_view(self, view_id=None, view_type="form", **options):
        context = self.env.context
        arch, view = super()._get_view(view_id, view_type, **options)

        if view_type == "form":
            update_arch = False
            doc = arch

            # Check if we need to change the partner_id domain filter
            id_group = context.get("active_id", False)
            if id_group:
                domain = None
                members = self.env["g2p.group.membership"].search(
                    [
                        ("group", "=", id_group),
                    ]
                )
                vals = []
                if members:
                    for line in members:
                        vals.append(line.individual.id)
                    domain = "[('id', 'in', %s)]" % vals

                if domain:
                    update_arch = True
                    nodes = doc.xpath("//field[@name='signatory_id']")
                    for node in nodes:
                        node.set("domain", domain)
            if update_arch:
                arch = doc
        return arch, view

    def record_consent(self):
        if self.signatory_id:
            vals = {
                "name": self.name,
                "signatory_id": self.signatory_id.id,
                "expiry": self.expiry,
                "config_id": self.config_id.id,
            }
            if self.is_group:
                vals = {
                    "name": self.name,
                    "signatory_id": self.signatory_id.id,
                    "expiry": self.expiry,
                    "config_id": self.config_id.id,
                    "group_id": self.group_id.id,
                }
                return self.group_id.write({"consent_ids": [(0, 0, vals)]})
            else:
                return self.signatory_id.write({"consent_ids": [(0, 0, vals)]})
        else:
            raise UserError(_("There are no selected Signatory!"))

    @api.depends("config_id", "signatory_id")
    def _compute_name(self):
        for rec in self:
            rec.name = rec.signatory_id.name
            if rec.config_id:
                rec.name = rec.config_id.name + "-" + rec.signatory_id.name

    @api.onchange("group_id")
    def _get_members(self):
        members = self.env["g2p.group.membership"].search(
            [
                ("group", "=", self.group_id.id),
            ]
        )
        vals = []
        if members:
            for line in members:
                vals.append(line.individual.id)
        res = {}
        res["domain"] = {"signatory_id": [("id", "in", vals)]}

        return res
