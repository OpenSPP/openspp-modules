import random
import re
import string

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


def _generate_unique_id():
    # Adjust the desired length of the unique identifier
    length = 8
    # Define the characters allowed in the unique identifier
    characters = string.digits + string.ascii_uppercase
    # Exclude characters that can be confused
    excluded_characters = ["0", "O", "1", "I"]
    # Filter the characters to exclude
    allowed_characters = [c for c in characters if c not in excluded_characters]
    # Generate the unique identifier by randomly selecting characters
    unique_id = "".join(random.choice(allowed_characters) for _ in range(length))

    return unique_id


class SppUniqueId(models.AbstractModel):
    _name = "spp.unique.id"
    _description = "Unique ID"

    spp_id = fields.Char(
        string="Unique ID",
        compute="_compute_spp_id",
        store=True,
        index=True,
    )

    _sql_constraints = [
        (
            "spp_id_uniq",
            "UNIQUE(spp_id)",
            "spp_id is an unique identifier!",
        )
    ]

    def _get_spp_id_prefix(self):
        raise NotImplementedError()

    def _get_match_spp_id_pattern(self):
        raise NotImplementedError()

    @api.constrains("spp_id")
    def _check_spp_id(self):
        not_correct_format = _("Unique ID is not following correct format!")
        for rec in self:
            match_pattern = rec._get_match_spp_id_pattern()
            if not match_pattern or not rec.spp_id:
                continue
            if not re.match(match_pattern, rec.spp_id):
                raise ValidationError(not_correct_format)
            if any([char in rec.spp_id.split("_")[-1] for char in ("0", "O", "1", "I")]):
                raise ValidationError(not_correct_format)

    @api.depends("create_date")
    def _compute_spp_id(self):
        for rec in self:
            if not rec.create_date:
                continue
            prefix = rec._get_spp_id_prefix()
            if not prefix:
                rec.spp_id = False
                continue
            spp_id = "_".join([prefix, _generate_unique_id()])
            while self.search([("spp_id", "=", spp_id)], limit=1):
                spp_id = "_".join([prefix, _generate_unique_id()])
            rec.spp_id = spp_id
