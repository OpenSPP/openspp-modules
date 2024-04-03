from odoo import fields, models


class OpenSPPEventDataMinDietaryDiversifyScore(models.Model):
    _name = "spp.event.min.dietary.score"
    _description = "Minimum Dietary Diversiyy Score"

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
    any_meat_paultry_fish = fields.Selection(
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
