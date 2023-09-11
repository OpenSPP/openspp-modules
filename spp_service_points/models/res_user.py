from odoo import fields, models


class Users(models.Model):
    _inherit = "res.users"

    service_point_ids = fields.Many2many(
        comodel_name="spp.service.point",
        relation="service_point_ids_user_ids_rel",
        column1="service_point_id",
        column2="user_id",
        string="Service Points",
    )
