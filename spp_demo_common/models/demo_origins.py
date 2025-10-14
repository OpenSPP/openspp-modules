# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SPPDemoOrigins(models.Model):
    _name = "spp.demo.origins"
    _description = "SPP Demo Origins"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    lang_id = fields.Many2one("res.lang", string="Language")
    lang_active = fields.Boolean(string="Active", related="lang_id.active")
