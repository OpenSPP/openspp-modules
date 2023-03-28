import json
from unittest.mock import patch

from odoo.exceptions import UserError

from .common import Common


class TestChangeRequests(Common):
    def setUp(self):
        super().setUp()
        self._test_change_request = self._create_change_request()

    def test_01_create(self):
        self.assertEqual(
            self._test_change_request.assign_to_id,
            self.env.user,
            "Creating user should be default assignee!",
        )

    def test_02_unlink_raise_error(self):
        with self.assertRaisesRegex(
            UserError, "Only draft change requests can be deleted by its creator."
        ):
            self._test_change_request.with_user(2).unlink()
        self._test_change_request.state = "pending"
        with self.assertRaisesRegex(
            UserError, "Only draft change requests can be deleted by its creator."
        ):
            self._test_change_request.unlink()

    def test_03_unlink(self):
        self._test_change_request.unlink()
        remaining_change_request = self.env["spp.change.request"].search(
            [("request_type", "=", "request_type")]
        )
        self.assertCountEqual(
            remaining_change_request.ids,
            [],
            "Draft change request should unlinkable by its creator!",
        )

    def test_04_compute_applicant_id_domain(self):
        self.assertEqual(
            self._test_change_request.applicant_id_domain,
            json.dumps([("id", "=", 0)]),
            "Without resgistrant, applicant selections should not be available!",
        )
        self._test_change_request.registrant_id = self._test_group
        self.assertEqual(
            self._test_change_request.applicant_id_domain,
            json.dumps(
                [
                    (
                        "id",
                        "in",
                        self._test_change_request.registrant_id.group_membership_ids.individual.ids,
                    )
                ]
            ),
            "With registrant, applicant selection should be available!",
        )

    def test_05_assign_to_user(self):
        admin = self.env.ref("base.user_admin")
        self._test_change_request.assign_to_user(admin)
        self.assertEqual(
            self._test_change_request.assign_to_id,
            admin,
            "Admin should be the one who assigned to this CR!",
        )
        self._test_change_request.state = "pending"
        with self.assertRaisesRegex(
            UserError, "^.*not have any validation sequence defined.$"
        ):
            self._test_change_request.assign_to_user(self.env.user)

    def test_06_onchange_scan_qr_code_details(self):
        self._test_change_request.qr_code_details = (
            '{"qrcode": "-T-E-S-T-Q-R-C-O-D-E-"}'
        )
        with self.assertRaisesRegex(
            UserError, "^.*no group found with the ID number from the QR Code scanned.$"
        ):
            self._test_change_request._onchange_scan_qr_code_details()
        self.env["g2p.reg.id"].create(
            {
                "partner_id": self._test_group.id,
                "id_type": self.env.ref("spp_idpass.id_type_idpass").id,
                "value": "-T-E-S-T-Q-R-C-O-D-E-",
            }
        )
        self._test_change_request._onchange_scan_qr_code_details()
        self.assertEqual(
            self._test_change_request.registrant_id,
            self._test_group,
            "Registrant on CR should be test group!",
        )

    @patch(
        "odoo.addons.phone_validation.tools.phone_validation.phone_parse",
        return_value="1",
    )
    def test_07_open_request_detail(self, phone_parse):
        with self.assertRaisesRegex(UserError, "Phone No. is required."):
            self._test_change_request.open_request_detail()
        self._test_change_request.applicant_phone = "+9647001234567"
        res = self._test_change_request.open_request_detail()
        self.assertListEqual(
            [res.get("type"), res.get("tag"), res.get("params", {}).get("type")],
            ["ir.actions.client", "display_notification", "danger"],
            "Request Type ID not existed, client should display error notification!",
        )
