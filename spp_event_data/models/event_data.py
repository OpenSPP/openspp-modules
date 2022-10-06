# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class OpenSPPEventData(models.Model):
    _name = "spp.event.data"
    _description = "Event Data"
    _order = "id desc"

    name = fields.Char(compute="_compute_name", store=True)
    model = fields.Char("Related Document Model", index=True)
    res_id = fields.Many2oneReference("Related data", index=True, model_field="model")
    registrar = fields.Many2one("res.partner")
    collection_date = fields.Date()
    expiry_date = fields.Date()

    @api.depends("model")
    def _compute_name(self):
        for rec in self:
            rec.name = ""
            if rec.model:
                model_name = self.env["ir.model"].search([("model", "=", rec.model)])
                if model_name:
                    rec.name = model_name.name

                model = self.env[rec.model].search([("id", "=", rec.res_id)])
                if model and model.summary:
                    rec.name += " - [%s]" % model.summary

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
