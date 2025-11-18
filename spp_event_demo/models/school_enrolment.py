# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class OpenSPPSchoolEnrolmentRecord(models.Model):
    _name = "spp.event.schoolenrolment.record"
    _inherit = "spp.event.mixin"
    _description = "School Enrolment Record"

    school_name = fields.Char()
    enrolment_type = fields.Char()
    date = fields.Date()
