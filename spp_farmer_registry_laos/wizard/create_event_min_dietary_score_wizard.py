# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SPPCreateEventMinimumDietaryDiversityScoreWizard(models.TransientModel):
    _name = "spp.create.event.min.dietary.score.wizard"
    _description = "XVII. Minimum Dietary Diversity Score"

    event_id = fields.Many2one("spp.event.data")

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

    def create_event(self):
        for rec in self:
            vals_list = {
                "food_made_grains_roots_tubers": rec.food_made_grains_roots_tubers,
                "any_beans_peas": rec.any_beans_peas,
                "any_nuts_seeds": rec.any_nuts_seeds,
                "any_milk_milk_products": rec.any_milk_milk_products,
                "any_meat_poultry_fish": rec.any_meat_poultry_fish,
                "any_eggs": rec.any_eggs,
                "any_dark_green_leafy_vegetables": rec.any_dark_green_leafy_vegetables,
                "any_vitamin_a_rich_fruits_vegetables": rec.any_vitamin_a_rich_fruits_vegetables,
                "any_other_vegetables": rec.any_other_vegetables,
                "any_other_fruits": rec.any_other_fruits,
                "food_mentioned_not_listed": rec.food_mentioned_not_listed,
                "remarks": rec.remarks,
            }

            event = self.env["spp.event.min.dietary.score"].create(vals_list)
            rec.event_id.res_id = event.id

            return event
