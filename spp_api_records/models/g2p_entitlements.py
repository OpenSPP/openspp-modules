from odoo import api, fields, models


class G2pEntitlements(models.Model):
    _inherit = "g2p.entitlement"

    partner_type = fields.Char(compute="_compute_partner_type")
    type = fields.Char(compute="_compute_type")
    cycle_number = fields.Char(related="cycle_id.name", string="Cycle Number")
    program_id = fields.Many2one(related="cycle_id.program_id")

    @api.depends("partner_id")
    def _compute_partner_type(self):
        for rec in self:
            partner_type = ""
            if rec.partner_id:
                partner_type = "individual"
                if rec.partner_id.is_group:
                    partner_type = "group"

            rec.partner_type = partner_type

    @api.depends("is_cash_entitlement")
    def _compute_type(self):
        for rec in self:
            entitlement_type = "inkind"
            if rec.is_cash_entitlement:
                entitlement_type = "cash"

            rec.type = entitlement_type


class G2pEntitlementsInKind(models.Model):
    _inherit = "g2p.entitlement.inkind"

    partner_type = fields.Char(compute="_compute_partner_type")
    type = fields.Char(compute="_compute_type")
    cycle_number = fields.Char(related="cycle_id.name", string="Cycle Number")

    @api.depends("partner_id")
    def _compute_partner_type(self):
        for rec in self:
            partner_type = ""
            if rec.partner_id:
                partner_type = "individual"
                if rec.partner_id.is_group:
                    partner_type = "group"

            rec.partner_type = partner_type

    def _compute_type(self):
        for rec in self:
            entitlement_type = "inkind"

            rec.type = entitlement_type
