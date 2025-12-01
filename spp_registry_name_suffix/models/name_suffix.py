from odoo import fields, models


class SPPNameSuffix(models.Model):
    _name = "spp.name.suffix"
    _description = "Name Suffix"
    _order = "sequence, name"

    name = fields.Char(
        string="Suffix",
        required=True,
        help="The suffix value (e.g., Jr., Sr., III, PhD)",
    )
    code = fields.Char(
        string="Code",
        required=True,
        help="Short code for the suffix",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Used to order suffixes in dropdown lists",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, the suffix will not be available for selection",
    )
    description = fields.Text(
        string="Description",
        help="Additional description or usage notes for this suffix",
    )

    _sql_constraints = [
        (
            "name_uniq",
            "unique(name)",
            "Suffix name must be unique!",
        ),
        (
            "code_uniq",
            "unique(code)",
            "Suffix code must be unique!",
        ),
    ]

    def name_get(self):
        """Display suffix name with code if different."""
        result = []
        for record in self:
            if record.code and record.code != record.name:
                name = f"{record.name} ({record.code})"
            else:
                name = record.name
            result.append((record.id, name))
        return result
