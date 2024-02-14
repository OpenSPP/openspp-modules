# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class OpenSPPSchoolEnrolmentRecord(models.Model):
    _name = "spp.event.schoolenrolment.record"
    _description = "School Enrolment Record"

    school_name = fields.Char()
    enrolment_type = fields.Char()
    date = fields.Date()

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id
