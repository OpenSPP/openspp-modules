from odoo import api, models, fields


class Registrant(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "spp.unique.id"]

    name = fields.Char(
        compute="_compute_name",
        inverse="_inverse_name",
        store=True,
    )

    @api.onchange("is_group", "family_name", "given_name", "addl_name")
    def name_change(self):
        pass

    @api.depends(
        "is_registrant",
        "is_group",
        "family_name",
        "given_name",
        "addl_name",
    )
    def _compute_name(self):
        for rec in self:
            if not rec.is_registrant or rec.is_group:
                continue
            name = []
            if rec.family_name:
                name.append(rec.family_name)
            if rec.given_name:
                name.append(rec.given_name)
            if rec.addl_name:
                name.append(self.addl_name)
            rec.name = ", ".join(name).upper()

    def _inverse_name(self):
        for rec in self:
            if not rec.is_registrant or rec.is_group:
                continue
            name = list(map(lambda i: i.capitalize(), self.name.split(", ")))
            if len(name) == 1:
                rec.given_name = name[0]
            elif len(name) == 2:
                rec.family_name = name[0]
                rec.given_name = name[1]
            else:
                rec.family_name = name[0]
                rec.given_name = name[1]
                rec.addl_name = name[2]

    def _get_registrant_id_prefix(self):
        if not self.is_registrant:
            return ""
        if self.is_group:
            return "GRP"
        return "IND"

    def _get_match_registrant_id_pattern(self):
        if not self.is_registrant:
            return ""
        if self.is_group:
            return r"^GRP_[0-9A-Z]{8}$"
        return r"^IND_[0-9A-Z]{8}$"
