# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SPPCreateEventSchoolEnrolmentWizard(models.TransientModel):
    _name = "spp.create.event.schoolenrolment.record.wizard"
    _description = "Create Event School Enrolment Wizard"

    event_id = fields.Many2one("spp.event.data")
    school_name = fields.Char()
    enrolment_type = fields.Char()
    date = fields.Date()

    def create_event(self):
        for rec in self:
            vals_list = [
                {
                    "school_name": rec.school_name or False,
                    "enrolment_type": rec.enrolment_type or False,
                    "date": rec.date or False,
                }
            ]
            event = self.env["spp.event.schoolenrolment.record"].create(vals_list)
            rec.event_id.res_id = event.id

            return event
