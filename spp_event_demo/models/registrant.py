# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class OpenSPPRegistrant(models.Model):
    _inherit = "res.partner"

    active_house_visit = fields.Many2one("spp.event.data", compute="_compute_active_house_visit")
    active_phone_survey = fields.Many2one("spp.event.data", compute="_compute_active_phone_survey")

    active_school_enrolment_record = fields.Many2one(
        "spp.event.data", compute="_compute_active_school_enrolment_record"
    )

    @api.depends("event_data_ids")
    def _compute_active_house_visit(self):
        """
        This computes the active house visit of the registrant
        """
        for rec in self:
            rec.active_house_visit = rec._get_active_event_id("spp.event.house.visit")

    @api.depends("event_data_ids")
    def _compute_active_phone_survey(self):
        """
        This computes the active phone survey of the registrant
        """
        for rec in self:
            rec.active_phone_survey = rec._get_active_event_id("spp.event.phone.survey")

    @api.depends("event_data_ids")
    def _compute_active_school_enrolment_record(self):
        """
        This computes the active school enrolment record of the registrant
        """
        for rec in self:
            rec.active_school_enrolment_record = rec._get_active_event_id("spp.event.schoolenrolment.record")
