from odoo import fields, models


class EventData(models.Model):
    _inherit = "spp.event.data"

    change_request_id = fields.Many2one(
        "spp.change.request",
        string="Change Request",
        ondelete="set null",
    )
