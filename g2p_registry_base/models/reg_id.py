# Part of Newlogic G2P. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class G2PRegistryID(models.Model):
    _name = "g2p.reg.id"
    _description = "Registrant ID"
    _order = "id desc"

    partner_id = fields.Many2one(
        "res.partner",
        "Registrant",
        required=True,
        domain=[("is_registrant", "=", True)],
    )
    id_type = fields.Many2one("g2p.id.type", "ID Type", required=True)
    value = fields.Char("Value", size=100)

    expiry_date = fields.Date("Expiry Date")

    def name_get(self):
        res = super(G2PRegistryID, self).name_get()
        for rec in self:
            name = ""
            if rec.partner_id:
                name = rec.partner_id.name
            res.append((rec.id, name))
        return res

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        if name:
            args = [("partner_id", operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)


class G2PIDType(models.Model):
    _name = "g2p.id.type"
    _description = "ID Type"
    _order = "id desc"

    name = fields.Char("Name")

    def unlink(self):
        for rec in self:
            external_identifier = self.env["ir.model.data"].search(
                [("res_id", "=", rec.id), ("model", "=", "g2p.id.type")]
            )
            if external_identifier.name == "id_type_idpass":
                raise ValidationError(_("Can't delete default ID Type"))
            else:
                return super(G2PIDType, self).unlink()

    def write(self, vals):
        external_identifier = self.env["ir.model.data"].search(
            [("res_id", "=", self.id), ("model", "=", "g2p.id.type")]
        )
        if external_identifier.name == "id_type_idpass":
            raise ValidationError(_("Can't edit default ID Type"))
        else:
            return super(G2PIDType, self).write(vals)
