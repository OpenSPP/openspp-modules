from odoo import api, fields, models


class OpenSPPEventDataMinDietaryDiversifyScore(models.Model):
    _name = "spp.event.min.dietary.score"
    _description = "XVII. Minimum Dietary Diversity Score"

    survey_sched = fields.Selection(
        [("1", "Baseline"), ("2", "Midline"), ("3", "Endline")],
        string="Survey Schedule",
    )
    food_made_grains_roots_tubers = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Food made from grains and any white roots or tuber or plantains",
    )
    any_beans_peas = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Any beans or peas",
    )
    any_nuts_seeds = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Any nuts or seeds",
    )
    any_milk_milk_products = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Any milk or milk products",
    )
    any_meat_poultry_fish = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Any meat, poultry and fish products",
    )
    any_eggs = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ]
    )
    any_dark_green_leafy_vegetables = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ]
    )
    any_vitamin_a_rich_fruits_vegetables = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Any vitamin A rich fruits, vegetables and roots",
    )
    any_other_vegetables = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ]
    )
    any_other_fruits = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ]
    )
    food_mentioned_not_listed = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Food mentioned by the respondent not listed in any category, or "
        + "the enumerator is unsure on where to categorize the food.",
    )
    remarks = fields.Text(string="Remarks")

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id


class OpenSPPEventDataMinDietaryDiversifyScoreResPartner(models.Model):
    _inherit = "res.partner"

    active_event_min_dietary_score = fields.Many2one(
        "spp.event.min.dietary.score",
        compute="_compute_active_event_min_dietary_score",
        store=True
    )

    xvii_survey_schedule = fields.Selection(
        string="Survey Schedule", related="active_event_min_dietary_score.survey_sched"
    )
    xvii_food_made_grains_roots_tubers = fields.Selection(
        string="Food made from grains and any white roots or tuber or plantains",
        related="active_event_min_dietary_score.food_made_grains_roots_tubers",
    )
    xvii_any_beans_peas = fields.Selection(
        string="Any beans or peas", related="active_event_min_dietary_score.any_beans_peas"
    )
    xvii_any_nuts_seeds = fields.Selection(
        string="Any nuts or seeds", related="active_event_min_dietary_score.any_nuts_seeds"
    )
    xvii_any_milk_milk_products = fields.Selection(
        string="Any milk or milk products", related="active_event_min_dietary_score.any_milk_milk_products"
    )
    xvii_any_meat_poultry_fish = fields.Selection(
        string="Any meat, poultry and fish products", related="active_event_min_dietary_score.any_meat_poultry_fish"
    )
    xvii_any_eggs = fields.Selection(string="Any eggs", related="active_event_min_dietary_score.any_eggs")
    xvii_any_dark_green_leafy_vegetables = fields.Selection(
        string="Any dark green leafy vegetables",
        related="active_event_min_dietary_score.any_dark_green_leafy_vegetables",
    )
    xvii_any_vitamin_a_rich_fruits_vegetables = fields.Selection(
        string="Any vitamin A rich fruits, vegetables and roots",
        related="active_event_min_dietary_score.any_vitamin_a_rich_fruits_vegetables",
    )
    xvii_any_other_vegetables = fields.Selection(
        string="Any other vegetables", related="active_event_min_dietary_score.any_other_vegetables"
    )
    xvii_any_other_fruits = fields.Selection(
        string="Any other fruits", related="active_event_min_dietary_score.any_other_fruits"
    )
    xvii_food_mentioned_not_listed = fields.Selection(
        string="Food mentioned by the respondent not listed in any category, or "
        + "the enumerator is unsure on where to categorize the food.",
        related="active_event_min_dietary_score.food_mentioned_not_listed",
    )
    xvii_remarks = fields.Text(string="Remarks", related="active_event_min_dietary_score.remarks")

    @api.depends("event_data_ids")
    def _compute_active_event_min_dietary_score(self):
        """
        This computes the active Minimum Dietary Diversity Score event of the group
        """
        for rec in self:
            event_data = rec._get_active_event_id("spp.event.min.dietary.score")
            rec.active_event_min_dietary_score = None
            if event_data:
                event_data_res_id = self.env["spp.event.data"].search([("id", "=", event_data)], limit=1).res_id
                rec.active_event_min_dietary_score = (
                    self.env["spp.event.min.dietary.score"].search([("id", "=", event_data_res_id)], limit=1).id
                )
