from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    suffix_id = fields.Many2one(
        comodel_name="spp.name.suffix",
        string="Suffix",
        ondelete="restrict",
        help="Name suffix such as Jr., Sr., III, IV, PhD, MD, etc.",
    )

    @api.depends(
        "is_registrant",
        "is_group",
        "family_name",
        "given_name",
        "addl_name",
        "suffix_id",
    )
    def _compute_name(self):
        """Extend name computation to include suffix for individuals."""
        super()._compute_name()
        for rec in self:
            if not rec.is_registrant or rec.is_group:
                continue
            if rec.suffix_id:
                rec.name = f"{rec.name}, {rec.suffix_id.name.upper()}"
