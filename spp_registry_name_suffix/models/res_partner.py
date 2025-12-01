from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    suffix_id = fields.Many2one(
        comodel_name="spp.name.suffix",
        string="Suffix",
        ondelete="restrict",
        help="Name suffix such as Jr., Sr., III, IV, PhD, MD, etc.",
    )

    @api.onchange("is_group", "family_name", "given_name", "addl_name", "suffix_id")
    def name_change(self):
        """Extend name change to include suffix for individuals."""
        super().name_change()
        if not self.is_group and self.suffix_id:
            self.name = f"{self.name}, {self.suffix_id.name.upper()}"
