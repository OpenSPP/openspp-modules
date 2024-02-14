# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class OpenSPPPhoneSurvey(models.Model):
    _name = "spp.event.phone.survey"
    _description = "Phone Survey"

    summary = fields.Char()
    description = fields.Text()

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id
