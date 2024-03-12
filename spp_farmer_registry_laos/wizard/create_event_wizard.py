# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SPPCreateEventWizard(models.TransientModel):
    _inherit = "spp.create.event.wizard"

    event_data_model = fields.Selection(
        selection_add=[
            ("spp.event.cycle2a", "FG member in round 1"),
            ("spp.event.cycle3a", "WU member, but not received production grant"),
            ("spp.event.cycle3b", "FG member in round 2"),
            ("spp.event.cycle2b", "Implementation of agriculture production grants (round 1)"),
            ("spp.event.cycle2c", "Implementation of livestock production grants (round 1)"),
        ]
    )
