from odoo import fields, models


class TestEventDataType(models.Model):
    _name = "spp.event.data.test"
    _description = "Test Event Data Type"


class SPPCreateEventDataTestWizard(models.TransientModel):
    _name = "spp.create.event.data.test.wizard"
    _description = "Test Create Event Data Wizard"

    name = fields.Char(string="Name")
    event_id = fields.Many2one("spp.event.data", string="Event Data", required=True)
