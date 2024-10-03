from odoo import fields, models


class Attendance(models.Model):
    _name = "spp.attendance.list"
    _description = "Attendance List"

    subscriber_id = fields.Many2one("spp.attendance.subscriber", required=True, readonly=True)
    attendance_date = fields.Date(required=True, default=lambda self: fields.Date.today(), tracking=True, string="Date")
    attendance_time = fields.Char(required=True, string="Time", tracking=True, default="00:00:00")

    attendance_location = fields.Char(required=True, string="Location")

    submitted_by = fields.Char(required=True)
    submitted_date = fields.Date(required=True, default=lambda self: fields.Date.today())
