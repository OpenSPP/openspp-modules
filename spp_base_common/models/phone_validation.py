from odoo import api, fields, models


class SPPPhoneValidation(models.Model):
    _name = "spp.phone.validation"
    _description = "SPP Phone Validation"

    name = fields.Char(string="Sample Format", compute="_compute_name")
    number_of_digits = fields.Integer(string="Number of Digits", required=True)
    with_prefix = fields.Boolean(string="With Prefix")
    prefix = fields.Char(string="Prefix")
    state = fields.Selection(
        [("active", "Active"), ("inactive", "Inactive")],
        string="State",
        default="active",
    )
    active = fields.Boolean(string="Active", default=True)

    @api.depends("number_of_digits", "with_prefix", "prefix")
    def _compute_name(self):
        for record in self:
            if record.with_prefix and record.prefix:
                record.name = f"{record.prefix}{'X'*record.number_of_digits}"
            else:
                record.name = "X" * record.number_of_digits

    def activate_phone_validation(self):
        for record in self:
            record.state = "active"

    def deactivate_phone_validation(self):
        for record in self:
            record.state = "inactive"
