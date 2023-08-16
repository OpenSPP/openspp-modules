from odoo import fields, models


class Users(models.Model):
    _inherit = "res.users"

    is_service_point_user = fields.Boolean()
    service_point_id = fields.Many2one(
        "spp.service.point",
        "Service Point",
    )
