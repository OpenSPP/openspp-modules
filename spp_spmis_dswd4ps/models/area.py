from odoo import fields, models


class OpenSPPArea(models.Model):
    _inherit = "spp.area"

    gida = fields.Selection(
        string="GIDA?",
        selection=[("yes", "Yes"), ("no", "No"), ("undetermined", "Undetermined")],
    )
