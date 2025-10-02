from odoo import fields, models


class RegistryConfig(models.TransientModel):
    _inherit = "res.config.settings"

    number_of_groups = fields.Integer(
        string="Number of Groups",
        config_parameter="spp_demo_common.number_of_groups",
    )
    members_range_from = fields.Integer(
        string="Members per Group (From)",
        config_parameter="spp_demo_common.members_range_from",
    )
    members_range_to = fields.Integer(
        string="Members per Group (To)",
        config_parameter="spp_demo_common.members_range_to",
    )
    batch_size = fields.Integer(
        string="Batch Size",
        config_parameter="spp_demo_common.batch_size",
    )
    queue_job_minimum_size = fields.Integer(
        string="Queue Job Minimum Size",
        config_parameter="spp_demo_common.queue_job_minimum_size",
    )
