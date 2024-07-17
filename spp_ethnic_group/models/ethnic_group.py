from odoo import fields, models


class OpenSPPEthnicGroup(models.Model):
    _name = "spp.ethnic.group"
    _description = "Ethnic Group"

    name = fields.Char("Ethnic Group", required=True)
    ethnic_group_id = fields.Char("Code", required=True)
