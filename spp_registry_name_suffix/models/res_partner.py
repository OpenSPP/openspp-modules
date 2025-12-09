from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    suffix_ids = fields.Many2many(
        comodel_name="spp.name.suffix",
        relation="res_partner_name_suffix_rel",
        column1="partner_id",
        column2="suffix_id",
        string="Suffixes",
        help="Name suffixes",
    )

    @api.constrains("suffix_ids")
    def _check_generational_suffix_conflict(self):
        """Validate that only one generational suffix is selected."""
        for record in self:
            if not record.suffix_ids:
                continue
            generational_suffixes = record.suffix_ids.filtered(lambda s: s.is_generational)
            if len(generational_suffixes) > 1:
                suffix_names = ", ".join(generational_suffixes.mapped("name"))
                raise ValidationError(
                    _(
                        "Only one generational suffix can be used at a time. "
                        "The following are generational suffixes: %(suffixes)s",
                        suffixes=suffix_names,
                    )
                )

    @api.onchange("is_group", "family_name", "given_name", "addl_name", "suffix_ids")
    def name_change(self):
        """Extend name change to include suffixes for individuals."""
        super().name_change()
        if not self.is_group and self.suffix_ids and self.name:
            # Join all suffixes in sequence order, separated by comma
            suffixes_str = ", ".join(self.suffix_ids.sorted("sequence").mapped(lambda s: s.name.upper()))
            suffix_part = f", {suffixes_str}"
            # Only append suffixes if not already present (avoid double-append)
            if not self.name.endswith(suffix_part):
                self.name = f"{self.name}{suffix_part}"
