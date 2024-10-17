from odoo import fields, models


class SPPResConfigAttendanceType(models.Model):
    _name = "spp.res.config.attendance.type"
    _description = "Config Attendance Type"
    _order = "name ASC"

    name = fields.Char(required=True)
    description = fields.Char()
    external_id = fields.Integer(required=True)
    external_source = fields.Char(required=True)
