from odoo import api, fields, models


class OpenSPPEventDataGenInfo(models.Model):
    _name = "spp.event.gen.info"
    _description = "II. General Information"

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

    def get_view_id(self):
        """
        This retrieves the View ID of this model
        """
        return self.env["ir.ui.view"].search([("model", "=", self._name), ("type", "=", "form")], limit=1).id


class OpenSPPEventDataGenInfoResPartner(models.Model):
    _inherit = "res.partner"

    active_event_gen_info = fields.Many2one("spp.event.gen.info", compute="_compute_active_event_gen_info")

    ii_survey_schedule = fields.Selection(string="Survey Schedule", related="active_event_gen_info.survey_sched")
    ii_interviewees_name = fields.Char("Interviewee's Name", related="active_event_gen_info.interviewees_name")
    ii_ethnic_group_id = fields.Many2one(
        "spp.ethnic.group", "Ethnic Group", related="active_event_gen_info.ethnic_group_id"
    )
    ii_sex = fields.Selection(related="active_event_gen_info.sex", string="Sex")
    ii_marital_status = fields.Selection(related="active_event_gen_info.marital_status", string="Marital Status")
    ii_age = fields.Integer(related="active_event_gen_info.age", string="Age")
    ii_educational_qualification = fields.Selection(
        string="Educational Qualification", related="active_event_gen_info.educational_qualification"
    )
    ii_head_of_household = fields.Selection(
        string="Head of Household", related="active_event_gen_info.head_of_household"
    )
    ii_poverty_status = fields.Selection(string="Poverty Status", related="active_event_gen_info.poverty_status")
    ii_gps_location = fields.GeoPointField("GPS Location", related="active_event_gen_info.gps_location")
    ii_phone_number1 = fields.Char("Phone Number 1", related="active_event_gen_info.phone_number1")
    ii_phone_number2 = fields.Char("Phone Number 2", related="active_event_gen_info.phone_number2")
    ii_participating = fields.Selection(string="Participating", related="active_event_gen_info.participating")
    ii_date_participated = fields.Date("Date Participated", related="active_event_gen_info.date_participated")
    ii_grp_act_supported_by_project_agri = fields.Selection(
        related="active_event_gen_info.grp_act_supported_by_project_agri",
        string="Project Group/Activity/Supported by Project (Agriculture Product)",
    )
    ii_grp_act_supported_by_project_livestock_fisheries = fields.Selection(
        related="active_event_gen_info.grp_act_supported_by_project_livestock_fisheries",
        string="Project Group/Activity/Supported by Project (Live Stock and Fisheries Product)",
    )

    ii_tech_supported_by_project_org_fert = fields.Selection(
        related="active_event_gen_info.tech_supported_by_project_org_fert",
        string="Techniques/Technologies Introduced/Supported by Project (Organic Fertilizer)",
    )
    ii_tech_supported_by_project_greenhouse = fields.Selection(
        related="active_event_gen_info.tech_supported_by_project_greenhouse",
        string="Techniques/Technologies Introduced/Supported by Project (Greenhouse)",
    )
    ii_tech_supported_by_project_mulching = fields.Selection(
        related="active_event_gen_info.tech_supported_by_project_mulching",
        string="Techniques/Technologies Introduced/Supported by Project (Mulching)",
    )
    ii_tech_supported_by_project_gravity_irrig = fields.Selection(
        related="active_event_gen_info.tech_supported_by_project_gravity_irrig",
        string="Techniques/Technologies Introduced/Supported by Project (Gravity Irrigation)",
    )
    ii_tech_supported_by_project_water_pump = fields.Selection(
        related="active_event_gen_info.tech_supported_by_project_water_pump",
        string="Techniques/Technologies Introduced/Supported by Project (Water Pump)",
    )
    ii_tech_supported_by_project_drip_irrig = fields.Selection(
        related="active_event_gen_info.tech_supported_by_project_drip_irrig",
        string="Techniques/Technologies Introduced/Supported by Project (Drip Irrigation)",
    )
    ii_tech_supported_by_project_drip_sprinkler = fields.Selection(
        related="active_event_gen_info.tech_supported_by_project_drip_sprinkler",
        string="Techniques/Technologies Introduced/Supported by Project (Sprinkler)",
    )
    ii_tech_supported_by_project_machine_harvest = fields.Selection(
        related="active_event_gen_info.tech_supported_by_project_machine_harvest",
        string="Techniques/Technologies Introduced/Supported by Project (Machine Harvest)",
    )
    ii_tech_supported_by_project_dry_processing = fields.Selection(
        related="active_event_gen_info.tech_supported_by_project_dry_processing",
        string="Techniques/Technologies Introduced/Supported by Project (Dry Processing)",
    )
    ii_tech_supported_by_project_agri_oth = fields.Char(
        "Other techniques/ technologies for crops", related="active_event_gen_info.tech_supported_by_project_agri_oth"
    )

    ii_tech_supported_by_project_concent_feed = fields.Selection(
        related="active_event_gen_info.tech_supported_by_project_concent_feed",
        string="Techniques/Technologies Introduced/Supported by Project (Concentrated Feed)",
    )
    ii_tech_supported_by_project_grass_planting = fields.Selection(
        related="active_event_gen_info.tech_supported_by_project_grass_planting",
        string="Techniques/Technologies Introduced/Supported by Project (Grass Planting for Forage)",
    )
    ii_tech_supported_by_project_vaccination = fields.Selection(
        related="active_event_gen_info.tech_supported_by_project_vaccination",
        string="Techniques/Technologies Introduced/Supported by Project (Vaccination)",
    )
    ii_tech_supported_by_project_livestock_oth = fields.Char(
        "Other techniques/ technologies for livestock",
        related="active_event_gen_info.tech_supported_by_project_livestock_oth",
    )
    ii_irrigation_area_supported = fields.Float(
        "Irrigation area supported by PICSA project (ha)", related="active_event_gen_info.irrigation_area_supported"
    )
    ii_participation_oth_proj = fields.Selection(
        related="active_event_gen_info.participation_oth_proj",
        string="Participation in other projects",
    )
    ii_hhq_number_baseline_survey = fields.Integer(
        "HH.Q No. of Baseline Survey",
        related="active_event_gen_info.hhq_number_baseline_survey",
    )

    @api.depends("event_data_ids")
    def _compute_active_event_gen_info(self):
        """
        This computes the active General Information event of the group
        """
        for rec in self:
            event_data = rec._get_active_event_id("spp.event.gen.info")
            rec.active_event_gen_info = None
            if event_data:
                event_data_res_id = self.env["spp.event.data"].search([("id", "=", event_data)], limit=1).res_id
                rec.active_event_gen_info = (
                    self.env["spp.event.gen.info"].search([("id", "=", event_data_res_id)], limit=1).id
                )
