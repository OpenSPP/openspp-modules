from odoo import fields, models


class Users(models.Model):
    _inherit = "res.users"

    service_point_ids = fields.Many2many(related="partner_id.ind_service_points_ids", string="Service Points")
