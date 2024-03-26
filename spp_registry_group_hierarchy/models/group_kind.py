from odoo import fields, models


class SPPGroupKind(models.Model):
    _inherit = "g2p.group.kind"

    allow_all_member_type = fields.Boolean("Allow group and individual members", default=False)
