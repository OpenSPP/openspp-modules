# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ChangeRequestTargets(models.Model):
    _name = "spp.change.request.targets"
    _description = "Change Requests' Targets"

    name = fields.Char("Model Name", required=True)
    target = fields.Selection([("individual", "Individual"), ("group", "Group"), ("both", "Both")], default="group")
