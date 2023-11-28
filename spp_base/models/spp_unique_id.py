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

    registrant_id = fields.Char(
        string="Unique ID",
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

    def _get_registrant_id_prefix(self):
        raise NotImplementedError()

    def _get_match_registrant_id_pattern(self):
        raise NotImplementedError()

    @api.constrains("registrant_id")
    def _check_registrant_id(self):
        not_correct_format = _("Unique ID is not following correct format!")
        for rec in self:
            match_pattern = rec._get_match_registrant_id_pattern()
            if not match_pattern:
                continue
            if not re.match(match_pattern, rec.registrant_id):
                raise ValidationError(not_correct_format)
            if any(
                [
                    char in rec.registrant_id.split("_")[-1]
                    for char in ("0", "O", "1", "I")
                ]
            ):
                raise ValidationError(not_correct_format)

    def _compute_registrant_id(self):
        for rec in self:
            prefix = rec._get_registrant_id_prefix()
            if not prefix:
                rec.registrant_id = False
                continue
            registrant_id = _generate_unique_id()
            rec.registrant_id = "_".join([prefix, registrant_id])
