from odoo import fields, models


class Attendance(models.Model):
    _name = "spp.attendance.list"
    _description = "Attendance List"

    subscriber_id = fields.Many2one("spp.attendance.subscriber", required=True, readonly=True)
    attendance_date = fields.Date(required=True, default=lambda self: fields.Date.today(), string="Date")
    attendance_time = fields.Char(required=True, string="Time", default="00:00:00")

    attendance_type_id = fields.Many2one("spp.attendance.type", string="Type")
    # attendance_location = fields.Char(required=True, string="Location")
    attendance_location_id = fields.Many2one("spp.attendance.location", string="Location")
    attendance_description = fields.Text(Char="Description")
    attendance_external_url = fields.Char(string="External URL")

    submitted_by = fields.Char(required=True)
    submitted_datetime = fields.Char(
        required=True, default=lambda self: fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    submission_source = fields.Char()
