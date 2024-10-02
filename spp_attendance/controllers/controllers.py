import json
from datetime import datetime

import werkzeug.wrappers

from odoo import _
from odoo.http import Controller, request, route
from odoo.tools import date_utils

from odoo.addons.spp_oauth.tools import OpenSPPOAuthJWTException, verify_and_decode_signature


def response_wrapper(status, data):
    return werkzeug.wrappers.Response(
        status=status,
        content_type="application/json; charset=utf-8",
        response=json.dumps(data, default=date_utils.json_default) if data else None,
    )


def error_wrapper(code, message):
    error = {"error": {"code": code, "message": message}}
    return response_wrapper(code, error)


def get_auth_header(headers, raise_exception=False):
    auth_header = headers.get("Authorization") or headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        if raise_exception:
            error = {
                "error": "Unauthorized",
                "error_description": "Your token could not be authenticated.",
            }
            return response_wrapper(401, error)
    return auth_header


def verify_auth_header():
    auth_header = get_auth_header(request.httprequest.headers, raise_exception=True)

    access_token = auth_header.replace("Bearer ", "").replace("\\n", "").encode("utf-8")
    try:
        verify_and_decode_signature(access_token)
    except OpenSPPOAuthJWTException:
        return False

    return True


def check_required_fields(data, required_fields=None):
    if not required_fields:
        return []

    missing_required_fields = []
    for field in required_fields:
        if field not in data:
            missing_required_fields.append(field)
    return missing_required_fields


def check_date_time_exists(date, time, subscriber_id):
    return (
        request.env["spp.attendance.list"]
        .sudo()
        .search(
            [("attendance_date", "=", date), ("attendance_time", "=", time), ("subscriber_id", "=", subscriber_id.id)]
        )
    )


class SppGisApiController(Controller):
    @route(
        "/api/attendance/oauth2/client/token",
        type="http",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def auth_get_access_token(self, **kwargs):
        req = request
        data = req.httprequest.data or "{}"
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            return response_wrapper(
                400,
                {
                    "error": "Bad Request",
                    "error_description": "data must be in JSON format.",
                },
            )

        client_id = data.get("client_id", "")
        client_secret = data.get("client_secret", "")

        if not all([client_id, client_secret]):
            error = {
                "error": "Bad Request",
                "error_description": "client_id and client_secret are required.",
            }
            return response_wrapper(400, error)

        client = (
            req.env["spp.attendance.api.client.credential"]
            .sudo()
            .search(
                [("client_id", "=", client_id), ("client_secret", "=", client_secret)],
                limit=1,
            )
        )

        if not client:
            error = {
                "error": "Unauthorized",
                "error_description": "Invalid client id or secret.",
            }
            return response_wrapper(401, error)

        access_token = client.generate_access_token()

        data = {
            "access_token": access_token,
            "token_type": "Bearer",
        }
        return response_wrapper(200, data)

    @route(
        "/api/attendance/list/create",
        type="http",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def create_attendance_list(self, **kwargs):
        req = request
        if not verify_auth_header():
            return error_wrapper(401, "Unauthorized")

        data = req.httprequest.data or "{}"
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            return error_wrapper(400, "data must be in JSON format.")

        missing_required_fields = check_required_fields(data, ["TimeCard", "PersonID", "SubmittedBy"])

        if missing_required_fields:
            return error_wrapper(400, f"Missing required fields: {', '.join(missing_required_fields)}")

        person_identifier = data.get("PersonID")
        subscriber_id = (
            req.env["spp.attendance.subscriber"].sudo().search([("person_identifier", "=", person_identifier)], limit=1)
        )
        if not subscriber_id:
            return error_wrapper(400, "PersonID does not exist.")

        current_date = datetime.now().strftime("%Y-%m-%d")
        submitted_date = data.get("SubmittedDate", current_date)

        submitted_by = data.get("SubmittedBy")

        time_cards = data.get("TimeCard")
        for time_card in time_cards:
            missing_required_fields = check_required_fields(time_card, ["DateTime", "AttendanceType"])
            if missing_required_fields:
                return error_wrapper(400, f"Missing required fields for TimeCard: {', '.join(missing_required_fields)}")

            attendance_datetime = time_card.get("DateTime")
            attendance_datetime = datetime.strptime(attendance_datetime, "%Y-%m-%d %H:%M:%S")

            attendance_date = str(attendance_datetime.date())
            attendance_time = str(attendance_datetime.time())

            if check_date_time_exists(attendance_date, attendance_time, subscriber_id):
                return error_wrapper(
                    400,
                    _("Attendance list already exists for the date %(date)s and time %(time)s.")
                    % {"date": attendance_date, "time": attendance_time},
                )

            attendance_type = time_card.get("AttendanceType")
            req.env["spp.attendance.list"].sudo().create(
                {
                    "subscriber_id": subscriber_id.id,
                    "attendance_date": attendance_date,
                    "attendance_time": attendance_time,
                    "attendance_location": attendance_type,
                    "submitted_by": submitted_by,
                    "submitted_date": submitted_date,
                }
            )

        return response_wrapper(
            200, {"message": "Attendance list created successfully.", "PersonID": person_identifier}
        )

    @route(
        "/api/attendance/list/<string:person_identifier>",
        type="http",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def attendance_list_person(self, person_identifier, **kwargs):
        req = request
        if not verify_auth_header():
            return error_wrapper(401, "Unauthorized")

        data = req.httprequest.data or "{}"
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            return error_wrapper(400, "data must be in JSON format.")

        subscriber_id = (
            req.env["spp.attendance.subscriber"].sudo().search([("person_identifier", "=", person_identifier)], limit=1)
        )

        if not subscriber_id:
            return error_wrapper(400, "PersonID does not exist.")

        return response_wrapper(
            200,
            {
                "PersonID": person_identifier,
                "AttendanceList": [
                    {
                        "Date": attendance_list.attendance_date,
                        "Time": attendance_list.attendance_time,
                        "AttendanceType": attendance_list.attendance_location,
                        "SubmittedBy": attendance_list.submitted_by,
                        "SubmittedDate": attendance_list.submitted_date,
                    }
                    for attendance_list in subscriber_id.attendance_list_ids
                ],
            },
        )

    @route(
        "/api/attendance/list",
        type="http",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def attendance_list(self, **kwargs):
        req = request
        if not verify_auth_header():
            return error_wrapper(401, "Unauthorized")

        data = req.httprequest.data or "{}"
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            return error_wrapper(400, "data must be in JSON format.")

        subscriber_ids = req.env["spp.attendance.subscriber"].sudo().search([])

        return response_wrapper(
            200,
            [
                {
                    "PersonID": subscriber_id.person_identifier,
                    "AttendanceList": [
                        {
                            "Date": attendance_list.attendance_date,
                            "Time": attendance_list.attendance_time,
                            "AttendanceType": attendance_list.attendance_location,
                            "SubmittedBy": attendance_list.submitted_by,
                            "SubmittedDate": attendance_list.submitted_date,
                        }
                        for attendance_list in subscriber_id.attendance_list_ids
                    ],
                }
                for subscriber_id in subscriber_ids
            ],
        )

    @route(
        "/api/present/subscriber",
        type="http",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def present_subscriber(self, **kwargs):
        req = request
        if not verify_auth_header():
            return error_wrapper(401, "Unauthorized")

        data = req.httprequest.data or "{}"
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            return error_wrapper(400, "data must be in JSON format.")

        from_date = data.get("FromDate")
        to_date = data.get("ToDate")

        if not from_date or not to_date:
            return error_wrapper(400, "FromDate and ToDate are required.")

        try:
            from_date = datetime.strptime(from_date, "%Y-%m-%d")
            to_date = datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            return error_wrapper(400, "FromDate and ToDate must be in the format YYYY-MM-DD.")

        if from_date > to_date:
            return error_wrapper(400, "FromDate must be less than or equal to ToDate.")

        attendance_list_ids = (
            req.env["spp.attendance.list"]
            .sudo()
            .search([("attendance_date", ">=", from_date), ("attendance_date", "<=", to_date)])
        )

        subscriber_ids = attendance_list_ids.mapped("subscriber_id")

        return response_wrapper(
            200,
            {
                "PersonID": subscriber_ids.mapped("person_identifier"),
            },
        )
