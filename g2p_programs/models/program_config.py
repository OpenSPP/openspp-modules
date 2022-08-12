# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProgramConfig(models.TransientModel):
    _name = "g2p.program.settings"
    _inherit = "res.config.settings"
    _description = "Program Settings"

    # Field Definitions
    default_eligibility_managers = fields.Many2many(
        "g2p.eligibility.manager",
        string="Eligibility Managers",
        default_model="g2p.program",
    )
    deduplication_managers = fields.Many2many(
        "g2p.deduplication.manager",
        string="Deduplication Managers",
        default_model="g2p.program",
    )
    notification_managers = fields.Many2many(
        "g2p.program.notification.manager",
        string="Notification Managers",
        default_model="g2p.program",
    )
    program_managers = fields.Many2many(
        "g2p.program.manager", string="Program Managers", default_model="g2p.program"
    )
    cycle_managers = fields.Many2many(
        "g2p.cycle.manager", string="Cycle Managers", default_model="g2p.program"
    )
    entitlement_managers = fields.Many2many(
        "g2p.program.entitlement.manager",
        string="Entitlement Managers",
        default_model="g2p.program",
    )
