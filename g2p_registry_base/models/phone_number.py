# Part of Newlogic G2P. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models
from odoo.addons.phone_validation.tools import phone_validation

_logger = logging.getLogger(__name__)


class G2PPhoneNumber(models.Model):
    _name = "g2p.phone.number"
    _description = "Phone Number"
    _order = "id desc"
    _rec_name = "phone_no"

    partner_id = fields.Many2one(
        "res.partner",
        "Registrant",
        required=True,
        domain=[("is_registrant", "=", True)],
    )
    phone_no = fields.Char("Phone Number", required=True)
    phone_sanitized = fields.Char("Phone Sanitized", compute="_compute_phone_sanitized")
    date_collected = fields.Date("Date Collected", default=fields.Date.today)
    disabled = fields.Datetime("Date Disabled")
    disabled_by = fields.Many2one("res.users", "Disabled by")
    country_id = fields.Many2one("res.country", "Country")

    @api.depends("phone_no", "country_id")
    def _compute_phone_sanitized(self):
        self.ensure_one()
        self.phone_sanitized = ""
        if self.phone_no:
            country_fname = "country_id"
            number = self["phone_no"]
            sanitized = str(
                phone_validation.phone_sanitize_numbers_w_record(
                    [number],
                    self,
                    record_country_fname=country_fname,
                    force_format="E164",
                )[number]["sanitized"]
            )
            _logger.debug(f"sanitized {sanitized}")
            self.phone_sanitized = sanitized

    @api.onchange("phone_no", "country_id")
    def _onchange_phone_validation(self):
        if self.phone_no:
            self.phone_no = self._phone_format(self.phone_no)
            _logger.debug(f"phone_no: {self.phone_no}")

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

    def disable_phone(self):
        for rec in self:
            if not rec.disabled:
                rec.update(
                    {
                        "disabled": fields.Datetime.now(),
                        "disabled_by": self.env.user,
                    }
                )

    def enable_phone(self):
        for rec in self:
            if rec.disabled:
                rec.update(
                    {
                        "disabled": None,
                        "disabled_by": None,
                    }
                )
