# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SPPDemoDataGenerationLog(models.Model):
    _name = "spp.demo.data.generation.log"
    _description = "Demo Data Generation Log"
    _order = "create_date desc"

    demo_data_generator_id = fields.Many2one(
        "spp.demo.data.generator",
        string="Demo Data Generator",
        required=True,
        ondelete="cascade",
        index=True,
    )
    registrant_id = fields.Many2one(
        "res.partner",
        string="Registrant",
        ondelete="set null",
        help="The registrant for which the generation failed",
    )
    registrant_type = fields.Selection(
        [("group", "Group"), ("individual", "Individual")],
        string="Registrant Type",
        required=True,
    )
    operation_type = fields.Selection(
        [
            ("id_generation", "ID Generation"),
            ("phone_generation", "Phone Number Generation"),
            ("bank_account", "Bank Account"),
            ("gps_coordinates", "GPS Coordinates"),
            ("other", "Other"),
        ],
        string="Operation Type",
        required=True,
    )
    failure_reason = fields.Selection(
        [
            ("max_attempts_reached", "Maximum Attempts Reached"),
            ("regex_validation_failed", "Regex Validation Failed"),
            ("generation_error", "Generation Error"),
            ("data_validation_failed", "Data Validation Failed"),
            ("other", "Other"),
        ],
        string="Failure Reason",
        required=True,
    )
    error_message = fields.Text(string="Error Message")
    attempts = fields.Integer(string="Number of Attempts", default=0)
    validation_regex = fields.Char(string="Validation Regex")
    generated_value = fields.Char(string="Last Generated Value")
    exception_details = fields.Text(string="Exception Details")
    create_date = fields.Datetime(string="Date Created", readonly=True)
