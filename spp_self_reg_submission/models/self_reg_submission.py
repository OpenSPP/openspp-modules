from odoo import fields, models


class SelfRegSubmission(models.Model):
    _name = "spp.self_reg.submission"
    _description = "Self Registration Submission"

    domain = fields.Char()
    identifier = fields.Char()
    timestamp = fields.Datetime()
    form_data = fields.Binary()
    meta_data = fields.Binary()
    complete = fields.Boolean()
