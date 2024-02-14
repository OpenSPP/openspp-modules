from odoo import fields, models


class SppProgram(models.Model):
    _inherit = "g2p.program"

    program_id = fields.Char(
        string="Program ID",
        default=lambda self: self.env["ir.sequence"].next_by_code("program.id.sequence"),
        readonly=True,
        copy=False,
        index=True,
    )

    _sql_constraints = [("program_id_uniq", "UNIQUE(program_id)", "program_id should be unique!")]
