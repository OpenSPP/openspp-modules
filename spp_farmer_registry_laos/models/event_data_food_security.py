from odoo import api, fields, models


class OpenSPPEventDataFoodSecurity(models.Model):
    _name = "spp.event.food.security"
    _description = "VII. Food Security"

    hungry_season_past_12 = fields.Integer("Experience a Hungry season in the past 12 months")
    shortage_january = fields.Integer("January")
    shortage_february = fields.Integer("February")
    shortage_march = fields.Integer("March")
    shortage_april = fields.Integer("April")
    shortage_may = fields.Integer("May")
    shortage_june = fields.Integer("June")
    shortage_july = fields.Integer("July")
    shortage_august = fields.Integer("August")
    shortage_september = fields.Integer("September")
    shortage_october = fields.Integer("October")
    shortage_november = fields.Integer("November")
    shortage_december = fields.Integer("December")

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id
