from odoo import _, fields, models


class OpenSPPArea(models.Model):
    _inherit = "spp.area"

    # NOTE: GIDA = Geographically Isolated and Disadvantaged Area
    gida = fields.Selection(
        string="GIDA",
        help=_("Geographically Isolated and Disadvantaged Area."),
        selection=[("yes", "Yes"), ("no", "No"), ("undetermined", "Undetermined")],
    )
