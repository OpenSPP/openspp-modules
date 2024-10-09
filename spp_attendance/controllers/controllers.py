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


def validate_page_and_limit(page, limit):
    try:
        page = int(page)
        limit = int(limit)
    except ValueError:
        return "Page and limit must be integers."

    if page < 1 or limit < 1:
        return "Page and limit must be positive integers."

    return None


def validate_date(from_date, to_date):
    if not all([from_date, to_date]):
        return None

    try:
        from_date = datetime.strptime(from_date, "%Y-%m-%d")
        to_date = datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        return "FromDate and ToDate must be in the format YYYY-MM-DD."

    if from_date > to_date:
        return "FromDate must be less than or equal to ToDate."

    return None


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
            missing_required_fields = check_required_fields(
                time_card, ["DateTime", "AttendanceLocation", "AttendanceType"]
            )
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

            attendance_type_id = False
            attendance_type = time_card.get("AttendanceType")

            if attendance_type:
                attendance_type_id = (
                    req.env["spp.attendance.type"].sudo().search([("name", "=", attendance_type)], limit=1)
                )

                if not attendance_type_id:
                    attendance_type_ids = req.env["spp.attendance.type"].sudo().search([]).mapped("name")
                    if attendance_type_ids:
                        available_types = ", ".join(attendance_type_ids)
                        error_message = (
                            f"Attendance Type does not exist. Available Attendance Types: {available_types}. "
                            "Leave it blank if desired type is not existing."
                        )
                    else:
                        error_message = "Attendance Type does not exist. Leave it blank."
                    return error_wrapper(400, error_message)

            attendance_location = time_card.get("AttendanceLocation")
            attendance_description = time_card.get("AttendanceDescription", "")
            attendance_external_url = time_card.get("AttendanceExternalURL", "")
            req.env["spp.attendance.list"].sudo().create(
                {
                    "subscriber_id": subscriber_id.id,
                    "attendance_date": attendance_date,
                    "attendance_time": attendance_time,
                    "attendance_type_id": attendance_type_id.id if attendance_type_id else False,
                    "attendance_location": attendance_location,
                    "attendance_description": attendance_description,
                    "attendance_external_url": attendance_external_url,
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
        methods=["GET"],
        csrf=False,
    )
    def attendance_list_person(self, person_identifier, page=1, limit=30, **kwargs):
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

        if page_limit_error_message := validate_page_and_limit(page, limit):
            return error_wrapper(400, page_limit_error_message)

        page = int(page)
        limit = int(limit)
        offset = (page - 1) * limit

        from_date = kwargs.get("FromDate", None)
        to_date = kwargs.get("ToDate", None)
        attendance_type = kwargs.get("AttendanceType", None)
        attendance_type_id = None

        if from_date and to_date:
            if date_error_message := validate_date(from_date, to_date):
                return error_wrapper(400, date_error_message)
            else:
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
                to_date = datetime.strptime(to_date, "%Y-%m-%d")

        if attendance_type:
            attendance_type_id = req.env["spp.attendance.type"].sudo().search([("name", "=", attendance_type)], limit=1)
            if not attendance_type_id:
                return error_wrapper(400, "Attendance Type does not exist.")

        total_attendance, attendance_record = subscriber_id.get_attendance_list(
            from_date=from_date,
            to_date=to_date,
            attendance_type_id=attendance_type_id,
            offset=offset,
            limit=limit,
        )
        attendance_record["pagination"] = {
            "page": page,
            "limit": limit,
            "total_records": total_attendance,
            "total_pages": (total_attendance + limit - 1) // limit,
        }

        return response_wrapper(
            200,
            attendance_record,
        )

    @route(
        "/api/attendance/list",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False,
    )
    def attendance_list(self, page=1, limit=30, **kwargs):
        req = request
        if not verify_auth_header():
            return error_wrapper(401, "Unauthorized")

        data = req.httprequest.data or "{}"
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            return error_wrapper(400, "data must be in JSON format.")

        if page_limit_error_message := validate_page_and_limit(page, limit):
            return error_wrapper(400, page_limit_error_message)

        page = int(page)
        limit = int(limit)
        offset = (page - 1) * limit

        from_date = kwargs.get("FromDate", None)
        to_date = kwargs.get("ToDate", None)
        attendance_type = kwargs.get("AttendanceType", None)
        attendance_type_id = None

        if from_date and to_date:
            if date_error_message := validate_date(from_date, to_date):
                return error_wrapper(400, date_error_message)
            else:
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
                to_date = datetime.strptime(to_date, "%Y-%m-%d")

        if attendance_type:
            attendance_type_id = req.env["spp.attendance.type"].sudo().search([("name", "=", attendance_type)], limit=1)
            if not attendance_type_id:
                return error_wrapper(400, "Attendance Type does not exist.")

        subscriber_model = request.env["spp.attendance.subscriber"].sudo()
        subscriber_ids = subscriber_model.search([], offset=offset, limit=limit, order="id")
        total_records = subscriber_model.search_count([])

        records = []
        for subscriber_id in subscriber_ids:
            total_attendance, attendance_record = subscriber_id.get_attendance_list(
                from_date=from_date,
                to_date=to_date,
                attendance_type_id=attendance_type_id,
            )
            records.append(attendance_record)

        response_data = {
            "records": records,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_records": total_records,
                "total_pages": (total_records + limit - 1) // limit,
            },
        }

        return response_wrapper(
            200,
            response_data,
        )

    @route(
        "/api/present/subscriber",
        type="http",
        auth="none",
        methods=["GET"],
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
