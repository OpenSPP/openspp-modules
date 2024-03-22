# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class OpenSPPEventData(models.Model):
    _name = "spp.event.data"
    _description = "Event Data"
    _order = "id desc"

    name = fields.Char(compute="_compute_name", store=True)
    model = fields.Char("Related Document Model", index=True)
    event_type = fields.Char(compute="_compute_event_type", store=True)
    res_id = fields.Many2oneReference("Related data", index=True, model_field="model")
    registrar = fields.Char()
    partner_id = fields.Many2one("res.partner", domain=[("is_registrant", "=", True)])
    collection_date = fields.Date(default=fields.Date.today(), required=True)
    expiry_date = fields.Date()
    state = fields.Selection(
        [("active", "Active"), ("inactive", "Inactive")],
        default="active",
    )

    @api.depends("model")
    def _compute_event_type(self):
        """
        This computes the event_type of the event data
        """
        for rec in self:
            rec.event_type = ""
            if rec.model:
                model_name = self.env["ir.model"].search([("model", "=", rec.model)])
                if model_name:
                    rec.event_type = model_name.name

    @api.depends("model", "res_id")
    def _compute_name(self):
        """
        This computes the name of the event data
        """
        for rec in self:
            rec.name = ""
            if rec.model:
                model_name = self.env["ir.model"].search([("model", "=", rec.model)])
                if model_name:
                    rec.name = model_name.name

                if rec.create_date:
                    rec.name += " - [%s]" % rec.create_date.strftime("%Y-%m-%d %H:%M")

    @api.model
    def create(self, vals):
        """
        This overrides the create function to end the previous active event before
        creating
        """
        if vals["model"]:
            model = vals["model"]
            partner = vals["partner_id"]
            active_event = self.env["spp.event.data"].search(
                [
                    ("model", "=", model),
                    ("state", "=", "active"),
                    ("partner_id", "=", partner),
                ]
            )
            if active_event:
                active_event.end_active_event()

        event = super().create(vals)
        return event

    def end_active_event(self):
        for rec in self:
            rec.state = "inactive"

    def open_form(self):
        for rec in self:
            context = {
                "create": False,
                "edit": False,
            }
            res_model = rec.model
            view_id = self.env[res_model].get_view_id()
            return {
                "name": rec.name,
                "view_mode": "form",
                "res_model": res_model,
                "res_id": rec.res_id,
                "view_id": view_id,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": context,
                "flags": {"mode": "readonly"},
            }
