import random
import re
import string

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
        match_pattern = r"^(IND|GRP)_[0-9a-zA-Z]{8}$"
        for rec in self:
            if not rec.is_registrant:
                continue
            if not re.match(match_pattern, rec.registrant_id):
                raise ValidationError(
                    _("Registrant ID is not following correct format!")
                )
            if any(
                [
                    char in rec.registrant_id.split("_")[-1]
                    for char in ("0", "O", "1", "I")
                ]
            ):
                raise ValidationError(
                    _("Registrant ID is not following correct format!")
                )

    @api.depends("is_registrant", "is_group")
    def _compute_registrant_id(self):
        for rec in self:
            if not rec.is_registrant:
                rec.registrant_id = None
                continue
            prefix = "GRP" if rec.is_group else "IND"
            unique_id = self._generate_unique_id()
            rec.registrant_id = "_".join([prefix, unique_id])

    def _generate_unique_id(self):
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
