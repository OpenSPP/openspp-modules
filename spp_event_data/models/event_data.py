# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging
from datetime import date

from odoo import _, api, fields, models

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
    collection_date = fields.Date(default=date.today(), required=True)
    expiry_date = fields.Date()
    state = fields.Selection(
        [("active", "Active"), ("inactive", "Inactive")],
        "State",
        default="active",
    )

    @api.depends("model")
    def _compute_event_type(self):
        for rec in self:
            rec.event_type = ""
            if rec.model:
                model_name = self.env["ir.model"].search([("model", "=", rec.model)])
                if model_name:
                    rec.event_type = model_name.name

    @api.depends("model", "res_id")
    def _compute_name(self):
        for rec in self:
            rec.name = ""
            if rec.model:
                model_name = self.env["ir.model"].search([("model", "=", rec.model)])
                if model_name:
                    rec.name = model_name.name

                if rec.create_date:
                    rec.name += " - [%s]" % rec.create_date

    @api.model
    def create(self, vals):
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

        event = super(OpenSPPEventData, self).create(vals)
        return event

    def end_active_event(self):
        for rec in self:
            rec.state = "inactive"

    def open_form(self):
        for rec in self:
            res_model = rec.model
            view_id = self.env[res_model].get_view_id()
            return {
                "name": _("%s" % rec.name),
                "view_mode": "form",
                "res_model": res_model,
                "res_id": rec.res_id,
                "view_id": view_id,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": self.env.context,
                "flags": {"mode": "readonly"},
            }
