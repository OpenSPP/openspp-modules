# Part of OpenSPP. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class OpenSPPPhoneSurvey(models.Model):
    _name = "spp.event.phone.survey"
    _inherit = "spp.event.mixin"
    _description = "Phone Survey"

    summary = fields.Char()
    description = fields.Text()
