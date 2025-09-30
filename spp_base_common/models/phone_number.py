import logging
import re

from odoo import _, api, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class G2PPhoneNumber(models.Model):
    _inherit = "g2p.phone.number"

    def write(self, vals):
        res = super().write(vals)
        if "phone_no" in vals or "country_id" in vals:
            self._onchange_phone_validation()
        return res

    @api.model_create_multi
    def create(self, vals):
        record = super().create(vals)
        record._onchange_phone_validation()
        return record

    @api.onchange("phone_no", "country_id")
    def _onchange_phone_validation(self):
        phone_validation = self.env["spp.phone.validation"].search([("state", "=", "active")])
        if not self.phone_no:
            return

        phone_no = self.phone_no
        error_msgs = []

        # Check for letters
        if re.search(r"[A-Za-z]", phone_no):
            error_msgs.append(_("Phone number must not contain letters."))

        # Check for invalid special characters (allow only digits, '-', and '+' at the start)
        # Acceptable pattern: optional leading '+', digits and '-' only
        if not re.match(r"^\+?[\d-]+$", phone_no):
            error_msgs.append(
                _(
                    "Phone number contains invalid special characters. "
                    "Only digits, '-', and an optional leading '+' are allowed."
                )
            )

        # Format validation
        if phone_validation:
            format_msgs = []
            validated_success_count = 0
            for validation in phone_validation:
                if validation.with_prefix:
                    pattern = r"^\+?" + re.escape(validation.prefix) + r"\d{" + str(validation.number_of_digits) + r"}$"
                else:
                    pattern = r"^\d{" + str(validation.number_of_digits) + r"}$"
                if re.match(pattern, phone_no):
                    validated_success_count += 1
                else:
                    format_msgs.append(validation.name)

            if validated_success_count == 0 and not error_msgs:
                error_msgs.append(_("Phone number must match one of the following formats: ") + ", ".join(format_msgs))

        if error_msgs:
            raise ValidationError("\n".join(error_msgs))
        return

    @api.depends("phone_no", "country_id")
    def _compute_phone_sanitized(self):
        for rec in self:
            rec.phone_sanitized = rec.phone_no
