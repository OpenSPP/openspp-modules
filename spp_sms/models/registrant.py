# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class Mailing(models.Model):
    _inherit = "res.partner"

    mailing_sms_id = fields.Many2one("mailing.mailing", string="Mailing SMS ID")
