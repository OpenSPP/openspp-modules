# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SPPCreateEventWizard(models.TransientModel):
    _inherit = "spp.create.event.wizard"

    event_data_model = fields.Selection(
        selection_add=[
            ("spp.event.house.visit", "House Visit"),
            ("spp.event.phone.survey", "Phone Survey"),
            ("spp.event.schoolenrolment.record", "School Enrolment Record"),
        ]
    )
