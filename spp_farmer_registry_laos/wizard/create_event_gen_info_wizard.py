# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class SPPCreateEventGenInfoWizard(models.TransientModel):
    _name = "spp.create.event.gen.info.wizard"
    _description = "II. General Information"

    event_id = fields.Many2one("spp.event.data")
    survey_sched = fields.Selection(
        [("1", "Baseline"), ("2", "Midline"), ("3", "Endline")],
        string="Survey Schedule",
    )
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

    tech_supported_by_project_org_fert = fields.Selection(
        [("1", "Selected"), ("2", "Not Selected")],
        string="Techniques/Technologies Introduced/Supported by Project (Organic Fertilizer)",
    )
    tech_supported_by_project_greenhouse = fields.Selection(
        [("1", "Selected"), ("2", "Not Selected")],
        string="Techniques/Technologies Introduced/Supported by Project (Greenhouse)",
    )
    tech_supported_by_project_mulching = fields.Selection(
        [("1", "Selected"), ("2", "Not Selected")],
        string="Techniques/Technologies Introduced/Supported by Project (Mulching)",
    )
    tech_supported_by_project_gravity_irrig = fields.Selection(
        [("1", "Selected"), ("2", "Not Selected")],
        string="Techniques/Technologies Introduced/Supported by Project (Gravity Irrigation)",
    )
    tech_supported_by_project_water_pump = fields.Selection(
        [("1", "Selected"), ("2", "Not Selected")],
        string="Techniques/Technologies Introduced/Supported by Project (Water Pump)",
    )
    tech_supported_by_project_drip_irrig = fields.Selection(
        [("1", "Selected"), ("2", "Not Selected")],
        string="Techniques/Technologies Introduced/Supported by Project (Drip Irrigation)",
    )
    tech_supported_by_project_drip_sprinkler = fields.Selection(
        [("1", "Selected"), ("2", "Not Selected")],
        string="Techniques/Technologies Introduced/Supported by Project (Sprinkler)",
    )
    tech_supported_by_project_machine_harvest = fields.Selection(
        [("1", "Selected"), ("2", "Not Selected")],
        string="Techniques/Technologies Introduced/Supported by Project (Machine Harvest)",
    )
    tech_supported_by_project_dry_processing = fields.Selection(
        [("1", "Selected"), ("2", "Not Selected")],
        string="Techniques/Technologies Introduced/Supported by Project (Dry Processing)",
    )
    tech_supported_by_project_agri_oth = fields.Char("Other techniques/ technologies for crops")

    tech_supported_by_project_concent_feed = fields.Selection(
        [("1", "Selected"), ("2", "Not Selected")],
        string="Techniques/Technologies Introduced/Supported by Project (Concentrated Feed)",
    )
    tech_supported_by_project_grass_planting = fields.Selection(
        [("1", "Selected"), ("2", "Not Selected")],
        string="Techniques/Technologies Introduced/Supported by Project (Grass Planting for Forage)",
    )
    tech_supported_by_project_vaccination = fields.Selection(
        [("1", "Selected"), ("2", "Not Selected")],
        string="Techniques/Technologies Introduced/Supported by Project (Vaccination)",
    )
    tech_supported_by_project_livestock_oth = fields.Char("Other techniques/ technologies for livestock")

    irrigation_area_supported = fields.Float("Irrigation area supported by PICSA project (ha)")
    participation_oth_proj = fields.Selection(
        [("1", "Yes"), ("2", "No")],
        string="Participation in other projects",
    )
    hhq_number_baseline_survey = fields.Integer("HH.Q No. of Baseline Survey")

    def create_event(self):
        for rec in self:
            vals_list = {
                "interviewees_name": rec.interviewees_name,
                "ethnic_group_id": rec.ethnic_group_id.id,
                "sex": rec.sex,
                "marital_status": rec.marital_status,
                "age": rec.age,
                "educational_qualification": rec.educational_qualification,
                "head_of_household": rec.head_of_household,
                "poverty_status": rec.poverty_status,
                "gps_location": rec.gps_location,
                "phone_number1": rec.phone_number1,
                "phone_number2": rec.phone_number2,
                "participating": rec.participating,
                "date_participated": rec.date_participated,
                "grp_act_supported_by_project_agri": rec.grp_act_supported_by_project_agri,
                "grp_act_supported_by_project_livestock_fisheries": rec.grp_act_supported_by_project_livestock_fisheries,
                "tech_supported_by_project_org_fert": rec.tech_supported_by_project_org_fert,
                "tech_supported_by_project_greenhouse": rec.tech_supported_by_project_greenhouse,
                "tech_supported_by_project_mulching": rec.tech_supported_by_project_mulching,
                "tech_supported_by_project_gravity_irrig": rec.tech_supported_by_project_gravity_irrig,
                "tech_supported_by_project_water_pump": rec.tech_supported_by_project_water_pump,
                "tech_supported_by_project_drip_irrig": rec.tech_supported_by_project_drip_irrig,
                "tech_supported_by_project_drip_sprinkler": rec.tech_supported_by_project_drip_sprinkler,
                "tech_supported_by_project_machine_harvest": rec.tech_supported_by_project_machine_harvest,
                "tech_supported_by_project_dry_processing": rec.tech_supported_by_project_dry_processing,
                "tech_supported_by_project_agri_oth": rec.tech_supported_by_project_agri_oth,
                "tech_supported_by_project_concent_feed": rec.tech_supported_by_project_concent_feed,
                "tech_supported_by_project_grass_planting": rec.tech_supported_by_project_grass_planting,
                "tech_supported_by_project_vaccination": rec.tech_supported_by_project_vaccination,
                "tech_supported_by_project_livestock_oth": rec.tech_supported_by_project_livestock_oth,
                "irrigation_area_supported": rec.irrigation_area_supported,
                "participation_oth_proj": rec.participation_oth_proj,
                "hhq_number_baseline_survey": rec.hhq_number_baseline_survey,
                "survey_sched": rec.survey_sched,
            }

            event = self.env["spp.event.gen.info"].create(vals_list)
            rec.event_id.res_id = event.id

            return event
