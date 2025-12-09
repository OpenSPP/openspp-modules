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
    def _check_suffix_exclusion_groups(self):
        """Validate that no two suffixes from the same exclusion group are selected."""
        for record in self:
            if not record.suffix_ids:
                continue
            # Get suffixes that have an exclusion group
            suffixes_with_groups = record.suffix_ids.filtered(lambda s: s.exclusion_group)
            # Group by exclusion_group
            groups = {}
            for suffix in suffixes_with_groups:
                group = suffix.exclusion_group
                if group not in groups:
                    groups[group] = []
                groups[group].append(suffix.name)
            # Check for conflicts
            for group, suffix_names in groups.items():
                if len(suffix_names) > 1:
                    raise ValidationError(
                        _(
                            "The following suffixes cannot be used together "
                            "as they belong to the same exclusion group '%(group)s': "
                            "%(suffixes)s",
                            group=group,
                            suffixes=", ".join(suffix_names),
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
