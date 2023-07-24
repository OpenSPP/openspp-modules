from odoo import api, fields, models


class SppServicePointTermialDevice(models.Model):
    _name = "spp.service.point.device"
    _description = "Service Point Terminal Device"

    service_point_id = fields.Many2one(
        comodel_name="spp.service.point",
        string="Service Point",
        required=True,
        copy=False,
    )
    device_model = fields.Char(
        string="Model",
        required=True,
        copy=False,
    )
    android_version = fields.Integer(
        required=True,
        copy=False,
    )
    service_point_terminal_device_id = fields.Char(
        string="External Identifier",
        required=True,
        copy=False,
    )
    status = fields.Boolean(
        readonly=True,
        default=True,
    )
    name = fields.Char(
        compute="_compute_name",
        store=True,
        copy=False,
    )

    @api.depends(
        "device_model",
        "android_version",
        "service_point_id",
    )
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.device_model}-{rec.android_version} [{rec.service_point_id.name}]"

    def action_change_status(self):
        self.ensure_one()
        self.status = not self.status
