# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.phone_validation.tools import phone_validation


class OpenSPPRegistrant(models.Model):
    _inherit = "res.partner"

    # Custom Fields
    service_point_ids = fields.Many2many("spp.service.point", string="Service Points")


class OpenSPPServicePoint(models.Model):
    _name = "spp.service.point"
    _description = "Service Point"
    _order = "id desc"

    def _get_default_country_id(self):
        return self.env.company.country_id

    name = fields.Char("Agent", required=True)
    area_id = fields.Many2one("spp.area", "Area")
    service_type_ids = fields.Many2many("spp.service.type", string="Service Types")
    phone_no = fields.Char("Phone Number")
    phone_sanitized = fields.Char(compute="_compute_phone_sanitized")
    shop_address = fields.Text("Address")
    is_contract_active = fields.Boolean("Active Contract")
    is_disabled = fields.Boolean("Disabled")
    disabled_date = fields.Date("Date Disabled")
    disabled_reason = fields.Char("Disable Reason")
    country_id = fields.Many2one(
        "res.country", "Country", default=_get_default_country_id
    )

    @api.depends("phone_no", "country_id")
    def _compute_phone_sanitized(self):
        for rec in self:
            rec.phone_sanitized = ""
            if rec.phone_no:
                country_fname = "country_id"
                number = rec["phone_no"]
                sanitized = str(
                    phone_validation.phone_sanitize_numbers_w_record(
                        [number],
                        rec,
                        record_country_fname=country_fname,
                        force_format="E164",
                    )[number]["sanitized"]
                )
                rec.phone_sanitized = sanitized

    @api.onchange("phone_no", "country_id")
    def _onchange_phone_validation(self):
        if self.phone_no:
            self.phone_no = self._phone_format(self.phone_no)

    def _phone_format(self, number, country=None):
        country = country or self.country_id or self.env.company.country_id
        if not country:
            return number
        return phone_validation.phone_format(
            number,
            country.code if country else None,
            country.phone_code if country else None,
            force_format="INTERNATIONAL",
            raise_exception=False,
        )

    def disable_service_point(self):
        for rec in self:
            if not rec.is_disabled:
                rec.update(
                    {
                        "is_disabled": True,
                        "disabled_date": fields.Date.today(),
                    }
                )
            else:
                raise UserError(_("Service point is already disabled."))

    def enable_service_point(self):
        for rec in self:
            if rec.is_disabled:
                rec.update(
                    {
                        "is_disabled": False,
                        "disabled_date": None,
                        "disabled_reason": None,
                    }
                )
            else:
                raise UserError(_("Service point is already enabled."))

    def open_area_form(self):
        for rec in self:
            if rec.area_id:
                return rec.area_id.open_area_form()


class OpenSPPServiceType(models.Model):
    _name = "spp.service.type"
    _description = "Service Type"

    name = fields.Char("Service Type")
