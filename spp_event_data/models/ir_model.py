# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    is_event_model = fields.Boolean(
        string="Is Event Model",
        default=False,
        help="Indicates if this model represents an event type for the event tracking system",
    )
