# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class OpenG2PIDType(models.Model):
    _inherit = "g2p.id.type"

    target_type = fields.Selection(
        [("individual", "Individual"), ("group", "Group"), ("both", "Both")],
        default="individual",
    )

    def unlink(self):
        """
        This overrides the unlink function to stop default ID
        Types from being deleted
        """
        for rec in self:
            external_identifier = self.env["ir.model.data"].search(
                [("res_id", "=", rec.id), ("model", "=", "g2p.id.type")]
            )
            if external_identifier.name == "id_type_idpass":
                raise ValidationError(_("Can't delete default ID Type"))
            else:
                return super().unlink()

    def write(self, vals):
        """
        This overrides the write function to stop default ID
        Types from being edited
        :param vals: The Values being edited.
        :raises: :class:ValidationError: Can't edit default ID Type
        :return: super write.
        """
        external_identifier = self.env["ir.model.data"].search(
            [("res_id", "=", self.id), ("model", "=", "g2p.id.type")]
        )
        if external_identifier.name == "id_type_idpass":
            vals = {}
        else:
            return super().write(vals)
