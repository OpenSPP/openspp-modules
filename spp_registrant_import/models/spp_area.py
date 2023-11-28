import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..tools import _generate_unique_id


class SppArea(models.Model):
    _inherit = "spp.area"

    unique_id = fields.Char(
        string="Unique ID",
        compute="_compute_unique_id",
        store=True,
        readonly=False,
        index=True,
    )

    _sql_constraints = [
        (
            "unique_id_uniq",
            "UNIQUE(unique_id)",
            "unique_id is an unique identifier!",
        )
    ]

    @api.constrains("unique_id")
    def _check_unique_id(self):
        match_pattern = r"^(LOC)_[0-9A-Z]{8}$"
        not_correct_format = _("Unique ID is not following correct format!")
        for rec in self:
            if not re.match(match_pattern, rec.unique_id):
                raise ValidationError(not_correct_format)
            if any(
                [char in rec.unique_id.split("_")[-1] for char in ("0", "O", "1", "I")]
            ):
                raise ValidationError(not_correct_format)

    def _compute_unique_id(self):
        for rec in self:
            unique_id = _generate_unique_id()
            rec.unique_id = "_".join(["LOC", unique_id])
