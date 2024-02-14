# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class OpenSPPRegistrantID(models.Model):
    _inherit = "g2p.reg.id"

    card_uid = fields.Char("Card UID")

    @api.constrains("card_uid", "id_type")
    def _check_card_uid(self):
        for rec in self:
            if rec.id_type.id == self.env.ref("spp_base.id_top_up_card").id and len(str(rec.card_uid)) != 10:
                raise ValidationError(_("Top-up Card UID should have 10 characters"))
