from odoo import SUPERUSER_ID, api

from . import models


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    programs = env["g2p.program"].search([("program_id", "=", False)])
    for prog in programs:
        prog.program_id = env["ir.sequence"].next_by_code("program.id.sequence")
