# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging
import textwrap

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class OpenSPPRegistrantID(models.Model):
    _inherit = "g2p.reg.id"

    card_uid = fields.Char("Card UID")

    @api.model
    def create(self, vals):
        if "id_type" in vals:
            if vals["id_type"] == self.env.ref("spp_base.id_top_up_card").id:
                if "card_uid" in vals and vals["card_uid"] and len(vals["card_uid"]) != 10:
                    raise ValidationError(_("Top-up Card UID should have 10 characters"))

        return super().create(vals)

    def write(self, vals):
        id_type = vals.get("id_type", self.id_type.id)
        card_uid = vals.get("card_uid", self.value)

        if id_type == self.env.ref("spp_base.id_top_up_card").id:
            if card_uid and len(card_uid) != 10:
                raise ValidationError(_("Top-up Card UID should have 10 characters"))

        return super().write(vals)
