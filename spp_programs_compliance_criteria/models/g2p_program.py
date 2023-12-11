from odoo import fields, models


class G2pProgram(models.Model):
    _inherit = "g2p.program"

    compliance_managers = fields.One2many(
        comodel_name="spp.compliance.manager",
        inverse_name="program_id",
        auto_join=True,
    )
