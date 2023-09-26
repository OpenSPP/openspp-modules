from odoo import api, fields, models


class Users(models.Model):
    _inherit = "res.users"

    service_point_ids = fields.Many2many(
        comodel_name="spp.service.point",
        relation="service_point_ids_user_ids_rel",
        column1="service_point_id",
        column2="user_id",
        string="Service Points",
        compute="_compute_service_point_ids",
        inverse="_inverse_service_point_ids",
        store=True,
    )

    @api.depends("partner_id.parent_id")
    def _compute_service_point_ids(self):
        for rec in self:
            if rec.partner_id.parent_id:
                service_points_ids = self.env["spp.service.point"].search(
                    [("res_partner_company_id", "=", rec.partner_id.parent_id.id)]
                )
                service_points_ids.update_user_ids()
            else:
                rec.service_point_ids.update_user_ids()

    def _inverse_service_point_ids(self):
        pass
