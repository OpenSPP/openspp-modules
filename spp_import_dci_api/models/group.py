from odoo import fields, models


class OpenSPPGroup(models.Model):
    _inherit = "res.partner"

    grp_is_created_from_crvs = fields.Boolean("Imported from CRVS", store=True)
