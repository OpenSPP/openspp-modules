from odoo import fields, models


class SPPRegistrantRelationship(models.Model):
    _inherit = "g2p.reg.rel"

    relation_inverse = fields.Char(related="relation.name_inverse", string="Relation")
