from odoo import api, fields, models

from odoo.addons.spp_oauth.tools.rsa_encode_decode import calculate_signature


class SppUsersBearerToken(models.TransientModel):
    _name = "spp.users.bearer.token"
    _description = "Users Bearer Token"
    _transient_max_count = 1

    user_token = fields.Char(
        string="User OpenAPI Token",
        required=True,
        related="user_id.openapi_token",
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
        ondelete="cascade",
        readonly=True,
    )
    db_name = fields.Char(
        string="Database Name",
        default=lambda self: self.env.cr.dbname,
        readonly=True,
        required=True,
    )
    calculated_token = fields.Char(string="User Bearer Token", compute="_compute_bearer_token")

    @api.depends("user_id", "user_id.openapi_token", "db_name")
    def _compute_bearer_token(self):
        for rec in self:
            rec.calculated_token = calculate_signature(
                header=None,
                payload={
                    "database": rec.db_name,
                    "token": rec.user_token,
                },
            )
