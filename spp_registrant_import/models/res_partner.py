import random
import string

from odoo import api, fields, models


class Registrant(models.Model):
    _inherit = "res.partner"

    registrant_id = fields.Char(
        string="Registrant ID",
        compute="_compute_registrant_id",
        store=True,
        readonly=True,  # Never ever change this to false
        index=True,
    )

    _sql_constraints = [
        (
            "registrant_id_uniq",
            "UNIQUE(registrant_id)",
            "registrant_id is an unique identifier!",
        )
    ]

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
