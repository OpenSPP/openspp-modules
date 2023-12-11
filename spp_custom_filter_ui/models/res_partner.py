from odoo import fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "custom.filter.mixin"]

    active = fields.Boolean(allow_filter=True)
    name = fields.Char(allow_filter=True)
    address = fields.Text(allow_filter=True)
    phone = fields.Char(allow_filter=True)
    kind = fields.Many2one(comodel_name="g2p.group.kind", allow_filter=True)
    category_id = fields.Many2many(
        comodel_name="res.partner.category", allow_filter=True
    )
    registration_date = fields.Date(allow_filter=True)
    disabled = fields.Boolean(allow_filter=True)
    company_id = fields.Many2one(comodel_name="res.company", allow_filter=True)
    is_partial_group = fields.Boolean(allow_filter=True)
    email = fields.Char(allow_filter=True)
    create_date = fields.Datetime(allow_filter=True)
    create_uid = fields.Many2one(comodel_name="res.users", allow_filter=True)
    write_date = fields.Datetime(allow_filter=True)
    write_uid = fields.Many2one(comodel_name="res.users", allow_filter=True)
    disabled_by = fields.Many2one(comodel_name="res.users", allow_filter=True)
    disabled_reason = fields.Text(allow_filter=True)
    is_registrant = fields.Boolean(allow_filter=True)
    is_group = fields.Boolean(allow_filter=True)
    addl_name = fields.Char(allow_filter=True)
    birth_place = fields.Char(allow_filter=True)
    birthdate = fields.Date(allow_filter=True)
    birthdate_not_exact = fields.Boolean(allow_filter=True)
    family_name = fields.Char(allow_filter=True)
    # gender = fields.Selection(allow_filter=True)
    given_name = fields.Char(allow_filter=True)
    group_membership_ids = fields.One2many(allow_filter=True)
    id_pdf = fields.Binary(allow_filter=True)
    id_pdf_filename = fields.Char(allow_filter=True)
    individual_membership_ids = fields.One2many(allow_filter=True)
    kind_as_str = fields.Char(allow_filter=True)
    phone_number_ids = fields.One2many(allow_filter=True)
    program_membership_ids = fields.One2many(allow_filter=True)
    reg_ids = fields.One2many(allow_filter=True)
    related_1_ids = fields.One2many(allow_filter=True)
    related_2_ids = fields.One2many(allow_filter=True)
