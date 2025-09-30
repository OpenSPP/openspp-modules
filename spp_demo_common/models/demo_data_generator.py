# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SPPDemoDataGenerator(models.Model):
    _name = "spp.demo.data.generator"
    _description = "SPP Demo Data Generator"

    def _default_number_of_groups(self):
        default_settings = self.env["ir.config_parameter"].sudo()
        return int(default_settings.get_param("spp_demo_common.number_of_groups", 10))

    def _default_members_range_from(self):
        default_settings = self.env["ir.config_parameter"].sudo()
        return int(default_settings.get_param("spp_demo_common.members_range_from", 1))

    def _default_members_range_to(self):
        default_settings = self.env["ir.config_parameter"].sudo()
        return int(default_settings.get_param("spp_demo_common.members_range_to", 10))

    def _default_batch_size(self):
        default_settings = self.env["ir.config_parameter"].sudo()
        return int(default_settings.get_param("spp_demo_common.batch_size", 100))

    def _default_locale_origin(self):
        company_lang = self.env.user.company_id.partner_id.lang
        if company_lang:
            lang = self.env["res.lang"].search([("code", "=", company_lang)], limit=1)
            if lang:
                return lang
        return self.env.ref("base.lang_en")
    
    def _default_queue_job_minimum_size(self):
        default_settings = self.env["ir.config_parameter"].sudo()
        return int(default_settings.get_param("spp_demo_common.queue_job_minimum_size", 500))

    name = fields.Char(string="Name", required=True)
    remember_settings = fields.Boolean(string="Remember Settings", default=False)
    number_of_groups = fields.Integer(string="Number of Groups", default=_default_number_of_groups, required=True)
    members_range_from = fields.Integer(
        string="Members per Group (From)", default=_default_members_range_from, required=True
    )
    members_range_to = fields.Integer(string="Members per Group (To)", default=_default_members_range_to, required=True)
    locale_origin = fields.Many2one("res.lang", string="Locale Origin", required=True, default=_default_locale_origin)
    batch_size = fields.Integer(string="Batch Size", default=_default_batch_size, required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("in_progress", "In Progress"), ("completed", "Completed"), ("cancelled", "Cancelled")],
        string="State",
        default="draft",
        required=True,
    )
    locked = fields.Boolean(string="Locked", default=False)
    locked_reason = fields.Text(string="Locked Reason")

    queue_job_minimum_size = fields.Integer(
        string="Queue Job Minimum Size",
        default=_default_queue_job_minimum_size,
    )

    def generate_demo_data(self):
        self.ensure_one()

    def refresh_page(self):
        self.ensure_one()
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

