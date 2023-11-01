# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class OpenSPPSchoolAttendanceRecord(models.Model):
    _name = "spp.event.schoolattendance.record"
    _description = "School Attendance Record"

    attendance_description = fields.Char()
    date = fields.Date()

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return (
            self.env["ir.ui.view"]
            .search([("model", "=", self._name), ("type", "=", "form")], limit=1)
            .id
        )
