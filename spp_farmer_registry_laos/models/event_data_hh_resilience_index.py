from odoo import api, fields, models


class OpenSPPEventDataHouseholdResilienceIndex(models.Model):
    _name = "spp.event.hh.resilience.index"
    _description = "Household Resilience Index"

    village_engaged_in_flood_landslide_prevention = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Village engaged in flood or land-slides prevention infrastructure construction",
    )
    experience_losses_due_to_floods_landslides = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Experienced loss of your crops, livestock, or physical property due to floods or land-slide",
    )
    significant_losses_48 = fields.Selection(
        [
            ("0", "Very Significant"),
            ("1", "Significant"),
            ("2", "Not Significant"),
        ]
    )

    access_to_secure_water_source = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Access to a secure water source",
    )
    member_water_user_group = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Member of a water users group/unit",
    )
    score_49 = fields.Selection(
        [
            ("0", "No"),
            ("1", "Yes to one question"),
            ("2", "Yes to both questions"),
        ],
        string="Score",
        compute="_compute_score_49",
    )

    exp_loss_crops_due_no_access_water = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Experienced loss of crops due to lack of access to water",
    )
    significant_losses_49 = fields.Selection(
        [
            ("0", "Lost more than 40%"),
            ("1", "Lost between 10% to 40%"),
            ("2", "No Significant Loss (<10%)"),
        ],
        string="Significant Losses",
    )
    access_services_diversification = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Access to quality extension services and technical advice "
        + "related to crop diversification and climate adaptation ",
    )
    adopted_new_techniques = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Adopted new techniques",
    )
    score_50 = fields.Selection(
        [
            ("0", "No"),
            ("1", "Yes to one question"),
            ("2", "Yes to both questions"),
        ],
        string="Score",
        compute="_compute_score_50",
    )
    ben_part_prod_grp = fields.Selection(
        [
            ("0", "Not Important"),
            ("1", "Important"),
            ("2", "Very Important"),
        ],
        string="Benefit of participating in producers' groups",
    )

    grow_veg_oth = fields.Selection(
        [
            ("0", "No"),
            ("1", "Only Wet or Dry Season"),
            ("2", "Both Seasons"),
        ],
        string="Grow vegetables or other cash crops during the wet season and dry",
    )
    hh_members_eat_veg = fields.Selection(
        [
            ("0", "< 3 times per week and/or in <10 months per year"),
            ("1", "> 3 times per week in > 10 months per year"),
            ("2", "> 5 times per week throughout the year"),
        ],
        string="All household members eat vegetables at least once a day",
    )

    part_training_nutr_food = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Participated in training and activities that have improved knowledge about nutritious food ",
    )
    intro_health_food_meal = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string=" Introduced more healthy food in the meals",
    )
    score_53 = fields.Selection(
        [
            ("0", "No"),
            ("1", "Yes to one question"),
            ("2", "Yes to both questions"),
        ],
        string="Score",
        compute="_compute_score_53",
    )
    eat_animal_protein = fields.Selection(
        [
            ("0", "Lest than 2 days per week"),
            ("1", "2-4 days per week"),
            ("2", "more than 4 days per week"),
        ],
        string="Eat animal sourced proteins",
    )

    inc_2_sources = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Income from at least two different sources",
    )
    inc_sale_crop_livestock = fields.Selection(
        [
            ("1", "Selected"),
            ("0", "Not Selected"),
        ],
        string="Sale of crops and/or livestock",
    )
    inc_processing_trading = fields.Selection(
        [
            ("1", "Selected"),
            ("0", "Not Selected"),
        ],
        string="Processing or trading",
    )
    inc_employment = fields.Selection(
        [
            ("1", "Selected"),
            ("0", "Not Selected"),
        ]
    )
    inc_own_business = fields.Selection(
        [
            ("1", "Selected"),
            ("0", "Not Selected"),
        ]
    )
    inc_other = fields.Selection(
        [
            ("1", "Selected"),
            ("0", "Not Selected"),
        ]
    )
    inc_other_sources = fields.Char(string="Other")

    support_2_sources = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Access to at least two different sources of support",
    )
    src_savings = fields.Selection(
        [
            ("1", "Selected"),
            ("0", "Not Selected"),
        ],
        string="Savings",
    )
    src_asset_livestock_sell = fields.Selection(
        [
            ("1", "Selected"),
            ("0", "Not Selected"),
        ],
        string="assets or livestock you can sell",
    )
    src_village_rice_bank = fields.Selection(
        [
            ("1", "Selected"),
            ("0", "Not Selected"),
        ],
        string="Village rice bank",
    )
    src_other = fields.Selection(
        [
            ("1", "Selected"),
            ("0", "Not Selected"),
        ],
        string="Other",
    )
    src_other_sources = fields.Char(string="Other sources")
    ability_to_cope = fields.Selection(
        [
            ("0", "No, not sufficient to cope and support recovery"),
            (
                "1",
                "Yes, sufficient to cope with and support recovery, but could experience "
                + "short term impacts on access to food and basic needs",
            ),
            ("2", "Yes, sufficient to cope with and support full recovery"),
        ],
        string="Ability to cope with and recover from an emergency or sudden difficult situation and avoid impacts",
    )

    comm_engage_contract_farming = fields.Selection(
        [
            ("1", "Yes"),
            ("2", "No"),
        ],
        string="Community engaging in contract farming or has a common initiative to sell their production",
    )
    issue_sell_prod = fields.Selection(
        [
            ("0", "Non acceptable"),
            ("1", "Acceptable but not always predictable"),
            ("2", "A very good and predictable price"),
        ],
        string="Issues selling production at a predictable decent price",
    )

    @api.depends("access_to_secure_water_source", "member_water_user_group")
    def _compute_score_49(self):
        for rec in self:
            score = "0"
            if rec.access_to_secure_water_source == "1" and rec.member_water_user_group == "1":
                score = "2"
            elif rec.access_to_secure_water_source == "1" or rec.member_water_user_group == "1":
                score = "1"
            rec.score_49 = score

    @api.depends("access_services_diversification", "adopted_new_techniques")
    def _compute_score_50(self):
        for rec in self:
            score = "0"
            if rec.access_services_diversification == "1" and rec.adopted_new_techniques == "1":
                score = "2"
            elif rec.access_services_diversification == "1" or rec.adopted_new_techniques == "1":
                score = "1"
            rec.score_50 = score

    @api.depends("part_training_nutr_food", "intro_health_food_meal")
    def _compute_score_53(self):
        for rec in self:
            score = "0"
            if rec.part_training_nutr_food == "1" and rec.intro_health_food_meal == "1":
                score = "2"
            elif rec.part_training_nutr_food == "1" or rec.intro_health_food_meal == "1":
                score = "1"
            rec.score_53 = score
