import json
from urllib.parse import urlencode, urljoin

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.osv.expression import AND


class G2pCycle(models.Model):
    _inherit = "g2p.cycle"

    attendance_type = fields.Char(
        string="Attendance Type",
        help=_("Type of attendance to be taken for this program. Should be existing in the system of the API Server."),
    )
    required_number_of_attendance = fields.Integer(
        string="Required Number of Attendance (Days)",
        default=10,
    )
    from_date = fields.Date()
    to_date = fields.Date()

    def action_filter_beneficiaries_by_compliance_criteria(self):
        super().action_filter_beneficiaries_by_compliance_criteria()
        registrant_satisfied = (
            self.env["res.partner"]
            .sudo()
            .search(self._get_compliance_criteria_domain() + AND([[("personal_identifier", "!=", False)]]))
        )

        attendance_auth_url = self.env["ir.config_parameter"].sudo().get_param("spp_attendance.attendance_auth_url")
        attendance_client_id = self.env["ir.config_parameter"].sudo().get_param("spp_attendance.attendance_client_id")
        attendance_client_secret = (
            self.env["ir.config_parameter"].sudo().get_param("spp_attendance.attendance_client_secret")
        )
        # access_token_mapping = self.env['ir.config_parameter'].sudo().get_param('spp_attendance.access_token_mapping')
        data = json.dumps({"client_id": attendance_client_id, "client_secret": attendance_client_secret})
        response = requests.post(attendance_auth_url, data=data)
        if response.status_code != 200:
            raise UserError(f"Connection to Attendance Server Failed. Reason: {response.text}")

        # access_token = response.json().get(access_token_mapping, None)
        access_token = response.json().get("access_token", None)
        if not access_token:
            raise UserError("Access Token not found in response.")

        attendance_compliance_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("spp_cycle_attendance_compliance.attendance_compliance_url")
        )

        header = {"Authorization": f"Bearer {access_token}"}
        data = json.dumps({"person_ids": registrant_satisfied.mapped("personal_identifier")})

        params = {"limit": max(len(registrant_satisfied), 30)}
        if self.from_date:
            params["from_date"] = self.from_date
        if self.to_date:
            params["to_date"] = self.to_date
        if self.attendance_type:
            params["attendance_type"] = self.attendance_type

        full_attendance_compliance_url = urljoin(attendance_compliance_url, "?" + urlencode(params))
        response = requests.get(full_attendance_compliance_url, headers=header, data=data)

        if response.status_code != 200:
            raise UserError(f"Connection to Attendance Compliance Server Failed. Reason: {response.text}")

        verified_person_id = []
        records = response.json().get("records", [])
        for record in records:
            person_id = record.get("person_id", None)
            number_of_attendance = record.get("number_of_days_present", 0)
            if number_of_attendance >= self.required_number_of_attendance:
                verified_person_id.append(person_id)
        registrant_satisfied = registrant_satisfied.filtered(lambda r: r.personal_identifier in verified_person_id)
        membership_to_paused = self.cycle_membership_ids.filtered(lambda cm: cm.partner_id not in registrant_satisfied)
        membership_to_paused.state = "non_compliant"
        membership_to_enrolled = self.cycle_membership_ids - membership_to_paused
        membership_to_enrolled.state = "enrolled"
