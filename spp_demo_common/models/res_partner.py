from odoo import fields, models


class SPPResPartner(models.Model):
    _inherit = "res.partner"

    demo_data_generator_id = fields.Many2one("spp.demo.data.generator", string="Demo Data Generator", readonly=True)
