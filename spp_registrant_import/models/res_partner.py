import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..tools import _generate_unique_id


class Registrant(models.Model):
    _inherit = "res.partner"

    registrant_id = fields.Char(
        string="Registrant ID",
        compute="_compute_registrant_id",
        store=True,
        readonly=False,
        index=True,
    )

    _sql_constraints = [
        (
            "registrant_id_uniq",
            "UNIQUE(registrant_id)",
            "registrant_id is an unique identifier!",
        )
    ]

    @api.constrains("registrant_id")
    def _check_registrant_id(self):
        match_pattern = r"^(IND|GRP)_[0-9A-Z]{8}$"
        not_correct_format = _("Registrant ID is not following correct format!")
        for rec in self:
            if not rec.is_registrant:
                continue
            if not re.match(match_pattern, rec.registrant_id):
                raise ValidationError(not_correct_format)
            if rec.is_group and rec.registrant_id.startswith("IND_"):
                raise ValidationError(not_correct_format)
            if any(
                [
                    char in rec.registrant_id.split("_")[-1]
                    for char in ("0", "O", "1", "I")
                ]
            ):
                raise ValidationError(not_correct_format)

    @api.depends("is_registrant", "is_group")
    def _compute_registrant_id(self):
        for rec in self:
            if not rec.is_registrant:
                rec.registrant_id = None
                continue
            prefix = "GRP" if rec.is_group else "IND"
            unique_id = _generate_unique_id()
            rec.registrant_id = "_".join([prefix, unique_id])
