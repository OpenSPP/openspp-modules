# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class OpenSPPFarmEventData(models.Model):
    _name = "spp.event.farm"
    _description = "Farm Event"

    no_hh_member = fields.Integer("No. of HH Member")
    no_indigenous = fields.Integer("No. of Indigenous")
    percent_indigenous = fields.Float("% of Indigenous")
    no_15_35 = fields.Integer("No. of Member in 15-35")
    percent_15_35 = fields.Float("% of Member in 15-35")
    no_woman_headed = fields.Integer("No. of Woman-headed HH")
    no_better_off = fields.Integer("No. of Better-off HH")
    no_medium = fields.Integer("No. of Medium HH")
    no_poor = fields.Integer("No. of Poor HH")
    no_male = fields.Integer("No. of Male")
    no_female = fields.Integer("No. of Female")
    no_both = fields.Integer("No. of Both")

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id
