# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class OpenSPPMailingRegistrants(models.Model):
    _name = "spp.mailing.registrants"
    _description = "Registrant Mailing"

    registrant_id = fields.Many2one("res.partner", string="Registrants")
    program_id = fields.Many2one("g2p.program", string="Program")
    cycle_id = fields.Many2one("g2p.cycle", string="Cycle")
    mailing_individual_id = fields.Many2one("mailing.mailing", string="Mass SMS Mail Individual")
    mailing_group_id = fields.Many2one("mailing.mailing", string="Mass SMS Mail Group")
    mailing_program_id = fields.Many2one("mailing.mailing", string="Mass SMS Mail Program")
    mailing_cycle_id = fields.Many2one("mailing.mailing", string="Mass SMS Mail Cycle")
