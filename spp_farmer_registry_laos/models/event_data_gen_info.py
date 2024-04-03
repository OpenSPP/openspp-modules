from odoo import fields, models


class OpenSPPEventDataGenInfo(models.Model):
    _name = "spp.event.gen.info"
    _description = "Event General Information"

    interviewees_name = fields.Char("Interviewee's Name")
    ethnic_group_id = fields.Many2one("spp.ethnic.group", "Ethnic Group")
    sex = fields.Selection([("1", "Female"), ("2", "Male")])
    marital_status = fields.Selection(
        [("1", "Married"), ("2", "Never-married"), ("3", "Widow/er"), ("4", "Divorced/Separated")]
    )
    age = fields.Integer()
    educational_qualification = fields.Selection(
        [
            ("1", "None"),
            ("2", "Primary"),
            ("3", "Secondary"),
            ("4", "Tertiary"),
            ("5", "Vocational"),
            ("6", "Post-graduate"),
        ]
    )
    head_of_household = fields.Selection([("1", "Yes"), ("2", "No")])
    poverty_status = fields.Selection([("1", "Poor"), ("2", "Medium"), ("3", "Rich")])
    gps_location = fields.GeoPointField("GPS Location")
    phone_number1 = fields.Char("Phone Number 1")
    phone_number2 = fields.Char("Phone Number 2")
    participating = fields.Selection(
        [("1", "Since the beginning of the project"), ("2", "Not participating from the beginning")]
    )
    date_participated = fields.Date()
    grp_act_supported_by_project_agri = fields.Selection(
        [
            ("0", "Not in this group"),
            ("1", "Vegetable"),
            ("2", "Rice"),
            ("3", "Onion"),
            ("4", "Cabbage"),
            ("5", "Peanuts"),
            ("6", "Cucumber"),
            ("7", "Garlic"),
            ("8", "Potato"),
            ("9", "Cassava"),
            ("10", "Chili"),
            ("11", "Tea"),
            ("12", "Maize"),
            ("13", "Sugarcane"),
            ("14", "Job'tears"),
            ("15", "Grass planting for forage"),
            ("16", "Sesame"),
        ],
        string="Project Group/Activity/Supported by Project (Agriculture Product)",
    )
    grp_act_supported_by_project_livestock_fisheries = fields.Selection(
        [
            ("0", "Not in this group"),
            ("19", "Pig"),
            ("20", "Chicken"),
            ("21", "Goat"),
        ],
        string="Project Group/Activity/Supported by Project (Live Stock and Fisheries Product)",
    )
