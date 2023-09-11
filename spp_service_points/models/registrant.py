# Part of OpenSPP. See LICENSE file for full copyright and licensing details.
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import email_normalize

from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)


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

    res_partner_company_id = fields.Many2one(
        "res.partner",
        "Company",
        domain=[("is_company", "=", True)],
    )

    user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="service_point_ids_user_ids_rel",
        column1="user_id",
        column2="service_point_id",
        string="Service Points",
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

    def create_user(self):
        if not self.res_partner_company_id:
            raise UserError(_("Service point does not have company."))
        if not self.res_partner_company_id.child_ids:
            raise UserError(_("Company does not have contacts."))

        for child_id in self.res_partner_company_id.child_ids:

            # if individual already have an account then continue
            if child_id.user_ids:
                continue

            if child_id.email:
                try:
                    self._create_user(child_id)
                except SignupError as e:
                    _logger.error(e)
                    raise UserError(
                        _(f"Error on individual {child_id.name}: {e}")
                    ) from e
            else:
                raise UserError(_(f"{child_id.name} does not have email."))

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Create SP User"),
                "message": _(
                    "Successfully created users for the contacts of the company"
                ),
                "sticky": True,
                "type": "success",
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }

    def _create_user(self, child_id):
        return (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            ._create_user_from_template(
                {
                    "email": email_normalize(child_id.email),
                    "login": email_normalize(child_id.email),
                    "partner_id": child_id.id,
                    "groups_id": [
                        (4, self.env.ref("base.group_user").id),
                        (4, self.env.ref("spp_service_points.service_point_users").id),
                    ],
                    "service_point_ids": [(4, self.id)],
                }
            )
        )

    def get_user_id_list(self):
        user_id_list = []

        # get all user_ids of individual
        if self.res_partner_company_id and self.res_partner_company_id.child_ids:
            for child_id in self.res_partner_company_id.child_ids:
                user_id_list.extend(child_id.user_ids.ids)

        # to ensure no duplicate id
        user_id_list = list(set(user_id_list))

        return user_id_list

    def write(self, vals):
        res = super().write(vals)

        if "res_partner_company_id" in vals:
            self.user_ids = [(6, 0, self.get_user_id_list())]

        return res

    @api.model
    def create(self, vals):
        res = super().create(vals)

        if "res_partner_company_id" in vals:
            res.user_ids = [(6, 0, res.get_user_id_list())]

        return res


class OpenSPPServiceType(models.Model):
    _name = "spp.service.type"
    _description = "Service Type"

    name = fields.Char("Service Type")
