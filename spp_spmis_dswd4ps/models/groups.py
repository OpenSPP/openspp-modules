from odoo import fields, models


class SPPGroups(models.Model):
    _inherit = "res.partner"

    ethnic_group_id = fields.Many2one("spp.ethnic.group", "Ethnic Group")
