# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class OpenSPPIDQueue(models.Model):
    _name = "spp.print.queue.id"
    _description = "ID Queue"

    name = fields.Char("Request Name")
    id_type = fields.Many2one("g2p.id.type", required=True)
    idpass_id = fields.Many2one("spp.id.pass")
    requested_by = fields.Many2one("res.users", required=True)
    approved_by = fields.Many2one("res.users")
    printed_by = fields.Many2one("res.users")
    registrant_id = fields.Many2one("res.partner", required=True)
    date_requested = fields.Date()
    date_approved = fields.Date()
    date_printed = fields.Date()
    date_distributed = fields.Date()
    status = fields.Selection(
        [
            ("new", "New"),
            ("approved", "Approved"),
            ("generated", "Generated"),
            ("printed", "Printed"),
            ("distributed", "Distributed"),
            ("cancelled", "Cancelled"),
        ],
        default="new",
    )
    id_pdf = fields.Binary("ID PASS")
    id_pdf_filename = fields.Char("ID File Name")

    batch_id = fields.One2many("spp.print.queue.batch", "queued_ids", string="Batch")

    def on_approve(self):
        for rec in self:
            rec.date_approved = date.today()
            rec.approved_by = self.env.user.id
            rec.status = "approved"

    def on_generate(self):
        # Make sure the ID is in the correct state before generating
        # we allow to re-generate cards
        self.generate_cards()

    def on_print(self):
        # as we return the PDF, we need to make sure that there is only 1 card selected
        self.ensure_one()

        # Make sure the ID is in the correct state before printing
        if self.filtered(lambda x: x.status not in ["generated", "approved"]):
            raise ValidationError(_("ID must be approved before printing"))

        if self.filtered(lambda x: x.batch_id):
            raise ValidationError(_("ID in a batch cannot be printed individually"))

        if self.status == "approved":
            # Not generated yet, generate it
            res_id = self.generate_card(self)
        else:
            res_id = self.id_pdf

        self.date_printed = date.today()
        self.printed_by = self.env.user.id
        self.status = "printed"
        return res_id

    def generate_cards(self):
        if self.filtered(
            lambda x: x.status not in ["generated", "approved", "added_to_batch"]
        ):
            raise ValidationError(_("ID must be approved before printing"))

        for rec in self:
            self.generate_card(rec)
            rec.status = "generated"

    def generate_card(self, card):
        """
        Generate ID card
        Override this method to change the backend used to generate the ID card
        """
        if card.id_type.id == self.env.ref("spp_idpass.id_type_idpass").id:
            vals = {"idpass": self.idpass_id.id, "id_queue": self.id}
            self.registrant_id.send_idpass_parameters(vals)

    def on_cancel(self):
        if self.filtered(lambda x: x.status in ["printed", "distributed"]):
            raise ValidationError(_("ID cannot be canceled if it has been printed"))
        for rec in self:
            rec.status = "cancelled"

    def on_distribute(self):
        if self.filtered(lambda x: x.status in ["printed"]):
            raise ValidationError(
                _("ID can only be distributed if it has been printed")
            )
        for rec in self:
            rec.date_distributed = date.today()
            rec.status = "distributed"


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auto_approve_id_request = fields.Boolean(
        default=True,
        help="Check if you want to auto-approve ID requests",
        string="Auto-approve ID Requests",
    )

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].set_param(
            "spp_id_queue.auto_approve_id_request", self.auto_approve_id_request
        )
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env["ir.config_parameter"].sudo()
        res.update(
            auto_approve_id_request=params.get_param(
                "spp_id_queue.auto_approve_id_request"
            )
        )
        return res
