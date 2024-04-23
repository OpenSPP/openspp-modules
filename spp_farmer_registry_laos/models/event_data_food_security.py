from odoo import api, fields, models


class OpenSPPEventDataFoodSecurity(models.Model):
    _name = "spp.event.food.security"
    _description = "VII. Food Security"

    survey_sched = fields.Selection(
        [("1", "Baseline"), ("2", "Midline"), ("3", "Endline")],
        string="Survey Schedule",
    )
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


class OpenSPPEventDataFoodSecurityResPartner(models.Model):
    _inherit = "res.partner"

    active_event_food_security = fields.Many2one(
        "spp.event.food.security", compute="_compute_active_event_food_security"
    )

    vii_survey_schedule = fields.Selection(string="Survey Schedule", related="active_event_food_security.survey_sched")
    vii_hungry_season_past_12 = fields.Integer(
        "Experience a Hungry season in the past 12 months", related="active_event_food_security.hungry_season_past_12"
    )
    vii_shortage_january = fields.Integer("January", related="active_event_food_security.shortage_january")
    vii_shortage_february = fields.Integer("February", related="active_event_food_security.shortage_february")
    vii_shortage_march = fields.Integer("March", related="active_event_food_security.shortage_march")
    vii_shortage_april = fields.Integer("April", related="active_event_food_security.shortage_april")
    vii_shortage_may = fields.Integer("May", related="active_event_food_security.shortage_may")
    vii_shortage_june = fields.Integer("June", related="active_event_food_security.shortage_june")
    vii_shortage_july = fields.Integer("July", related="active_event_food_security.shortage_july")
    vii_shortage_august = fields.Integer("August", related="active_event_food_security.shortage_august")
    vii_shortage_september = fields.Integer("September", related="active_event_food_security.shortage_september")
    vii_shortage_october = fields.Integer("October", related="active_event_food_security.shortage_october")
    vii_shortage_november = fields.Integer("November", related="active_event_food_security.shortage_november")
    vii_shortage_december = fields.Integer("December", related="active_event_food_security.shortage_december")

    @api.depends("event_data_ids")
    def _compute_active_event_food_security(self):
        """
        This computes the active Food Security event of the group
        """
        for rec in self:
            event_data = rec._get_active_event_id("spp.event.food.security")
            rec.active_event_food_security = None
            if event_data:
                event_data_res_id = self.env["spp.event.data"].search([("id", "=", event_data)], limit=1).res_id
                rec.active_event_food_security = (
                    self.env["spp.event.food.security"].search([("id", "=", event_data_res_id)], limit=1).id
                )
