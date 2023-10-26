# Part of OpenG2P. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SPPCreateEventSchoolAttendanceWizard(models.TransientModel):
    _name = "spp.create.event.schoolattendance.record.wizard"
    _description = "Create Event School Attendance Wizard"

    event_id = fields.Many2one("spp.event.data")
    attendance_description = fields.Char()
    date = fields.Date()

    def create_event(self):
        for rec in self:
            vals_list = [
                {
                    "attendance_description": rec.attendance_description or False,
                    "date": rec.date or False,
                }
            ]
            event = self.env["spp.event.schoolattendance.record"].create(vals_list)
            rec.event_id.res_id = event.id

            return event
