# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SPPCreateEventWizard(models.TransientModel):
    _inherit = "spp.create.event.wizard"

    event_data_model = fields.Selection(
        selection_add=[
            ("spp.event.cycle", "Event Cycle"),
            ("spp.event.gen.info", "II. General Information"),
            ("spp.event.poverty.indicator", "III. Poverty Indicators"),
        ]
    )
