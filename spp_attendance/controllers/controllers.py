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


def check_date_time_exists(date, time, subscriber_id, person_datetime_mapping=None):
    if person_datetime_mapping:
        return (subscriber_id, date, time) in person_datetime_mapping
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


def validate_request_header_and_body():
    if not verify_auth_header():
        return error_wrapper(401, "Unauthorized")

    req = request
    data = req.httprequest.data or "{}"
    try:
        data = json.loads(data)
    except json.decoder.JSONDecodeError:
        return error_wrapper(400, "data must be in JSON format.")

    return None


def validate_entity(model_name, model_id, model_label):
    if model_id:
        try:
            model_id = int(model_id)
        except ValueError:
            return error_wrapper(400, f"{model_label} must be an integer.")

        entity = request.env[model_name].sudo().search([("id", "=", model_id)], limit=1)
        if not entity:
            model_ids = request.env[model_name].sudo().search([])
            error_message = f"{model_label} does not exist."
            if model_ids:
                choices = ", ".join([f"{model.id} for {model.name}" for model in model_ids])
                error_message = f"{model_label} does not exist. Available {model_label}s: {choices}."
            return error_wrapper(400, error_message)
    return None


def validate_attendance_type(attendance_type):
    return validate_entity("spp.attendance.type", attendance_type, "Attendance Type")


def validate_attendance_location(attendance_location):
    return validate_entity("spp.attendance.location", attendance_location, "Attendance Location")


class SppGisApiController(Controller):
    @route(
        "/auth/token",
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
                "error_description": ("client_id and client_secret are required."),
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
        "/attendances",
        type="http",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    def create_attendance_list(self, **kwargs):
        if error := validate_request_header_and_body():
            return error

        req = request
        data = req.httprequest.data or "{}"
        data = json.loads(data)

        if missing_required_fields := check_required_fields(data, ["records", "submitted_by", "submitted_datetime"]):
            return error_wrapper(400, f"Missing required fields: {', '.join(missing_required_fields)}")

        current_date = datetime.now().strftime("%Y-%m-%d")
        submitted_datetime = data.get("submitted_datetime", current_date)
        submitted_by = data.get("submitted_by")
        submission_source = data.get("submission_source", "")

        attendance_list_data = []
        person_id_list = []

        person_datetime_mapping = []

        for person_data in data["records"]:
            if missing_required_fields := check_required_fields(person_data, ["time_card", "person_id"]):
                return error_wrapper(400, f"Missing required fields: {', '.join(missing_required_fields)}")

            person_id = person_data.get("person_id")
            subscriber_id = (
                req.env["spp.attendance.subscriber"].sudo().search([("person_identifier", "=", person_id)], limit=1)
            )
            if not subscriber_id:
                return error_wrapper(400, "person_id does not exist.")

            time_cards = person_data.get("time_card")
            for time_card in time_cards:
                missing_required_fields = check_required_fields(time_card, ["date_time"])
                if missing_required_fields:
                    return error_wrapper(
                        400, f"Missing required fields for time_card: {', '.join(missing_required_fields)}"
                    )

                attendance_datetime = time_card.get("date_time")
                attendance_datetime = datetime.strptime(attendance_datetime, "%Y-%m-%d %H:%M:%S")

                attendance_date = str(attendance_datetime.date())
                attendance_time = str(attendance_datetime.time())

                if check_date_time_exists(
                    attendance_date, attendance_time, subscriber_id, person_datetime_mapping=person_datetime_mapping
                ):
                    return error_wrapper(
                        400,
                        _(
                            "Attendance list already exists "
                            + "for the date %(date)s and time %(time)s for %(person_identifier)s."
                        )
                        % {"date": attendance_date, "time": attendance_time, "person_identifier": person_id},
                    )
                person_datetime_mapping.append((subscriber_id, attendance_date, attendance_time))

                attendance_type = time_card.get("attendance_type", False) or False
                if result := validate_attendance_type(attendance_type):
                    return result
                attendance_type = int(attendance_type)

                attendance_location = time_card.get("attendance_location", False) or False
                if result := validate_attendance_location(attendance_location):
                    return result
                attendance_location = int(attendance_location)

                attendance_description = time_card.get("attendance_description", "")
                attendance_external_url = time_card.get("attendance_external_url", "")
                attendance_list_data.append(
                    {
                        "subscriber_id": subscriber_id.id,
                        "attendance_date": attendance_date,
                        "attendance_time": attendance_time,
                        "attendance_type_id": attendance_type,
                        "attendance_location_id": attendance_location,
                        "attendance_description": attendance_description,
                        "attendance_external_url": attendance_external_url,
                        "submitted_by": submitted_by,
                        "submitted_datetime": submitted_datetime,
                        "submission_source": submission_source,
                    }
                )
                if person_id not in person_id_list:
                    person_id_list.append(person_id)

        req.env["spp.attendance.list"].sudo().create(attendance_list_data)

        return response_wrapper(200, {"message": "Attendance list created successfully.", "person_ids": person_id_list})

    @route(
        "/attendance/<string:person_identifier>",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False,
    )
    def attendance_list_person(self, person_identifier, page=1, limit=30, **kwargs):
        if error := validate_request_header_and_body():
            return error

        req = request
        data = req.httprequest.data or "{}"
        data = json.loads(data)

        subscriber_id = (
            req.env["spp.attendance.subscriber"].sudo().search([("person_identifier", "=", person_identifier)], limit=1)
        )

        if not subscriber_id:
            return error_wrapper(400, f"PersonID {person_identifier} does not exist.")

        if page_limit_error_message := validate_page_and_limit(page, limit):
            return error_wrapper(400, page_limit_error_message)

        page = int(page)
        limit = int(limit)
        offset = (page - 1) * limit

        from_date = kwargs.get("from_date", None)
        to_date = kwargs.get("to_date", None)

        if from_date and to_date:
            if date_error_message := validate_date(from_date, to_date):
                return error_wrapper(400, date_error_message)
            else:
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
                to_date = datetime.strptime(to_date, "%Y-%m-%d")

        attendance_type = kwargs.get("attendance_type", False) or False
        if result := validate_attendance_type(attendance_type):
            return result
        attendance_type = int(attendance_type)

        attendance_location = kwargs.get("attendance_location", False) or False
        if result := validate_attendance_location(attendance_location):
            return result
        attendance_location = int(attendance_location)

        total_attendance, attendance_record = subscriber_id.get_attendance_list(
            from_date=from_date,
            to_date=to_date,
            attendance_type_id=attendance_type,
            attendance_location_id=attendance_location,
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
        "/attendances",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False,
    )
    def attendance_list(self, page=1, limit=30, **kwargs):
        if error := validate_request_header_and_body():
            return error

        req = request
        data = req.httprequest.data or "{}"
        data = json.loads(data)

        if page_limit_error_message := validate_page_and_limit(page, limit):
            return error_wrapper(400, page_limit_error_message)

        page = int(page)
        limit = int(limit)
        offset = (page - 1) * limit

        from_date = kwargs.get("from_date", None)
        to_date = kwargs.get("to_date", None)

        if from_date and to_date:
            if date_error_message := validate_date(from_date, to_date):
                return error_wrapper(400, date_error_message)
            else:
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
                to_date = datetime.strptime(to_date, "%Y-%m-%d")

        attendance_type = kwargs.get("attendance_type", False) or False
        if result := validate_attendance_type(attendance_type):
            return result
        attendance_type = int(attendance_type)

        attendance_location = kwargs.get("attendance_location", False) or False
        if result := validate_attendance_location(attendance_location):
            return result
        attendance_location = int(attendance_location)

        domain = []

        person_identifier_list = data.get("person_ids", [])
        if person_identifier_list:
            domain.append(("person_identifier", "in", person_identifier_list))

        subscriber_model = request.env["spp.attendance.subscriber"].sudo()
        subscriber_ids = subscriber_model.search(domain, offset=offset, limit=limit, order="id")
        total_records = subscriber_model.search_count(domain)

        records = []
        for subscriber_id in subscriber_ids:
            total_attendance, attendance_record = subscriber_id.get_attendance_list(
                from_date=from_date,
                to_date=to_date,
                attendance_type_id=attendance_type,
                attendance_location_id=attendance_location,
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
        "/attendance/types",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False,
    )
    def get_attendance_types(self):
        if error := validate_request_header_and_body():
            return error

        req = request
        data = req.httprequest.data or "{}"
        data = json.loads(data)

        attendance_type_ids = req.env["spp.attendance.type"].sudo().search([])

        return response_wrapper(
            200,
            {
                "records": [
                    {
                        "id": attendance_type.id,
                        "name": attendance_type.name,
                        "description": attendance_type.description,
                    }
                    for attendance_type in attendance_type_ids
                ],
            },
        )

    @route(
        "/attendance/locations",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False,
    )
    def get_attendance_locations(self):
        if error := validate_request_header_and_body():
            return error

        req = request
        data = req.httprequest.data or "{}"
        data = json.loads(data)

        attendance_location_ids = req.env["spp.attendance.location"].sudo().search([])

        return response_wrapper(
            200,
            {
                "records": [
                    {
                        "id": attendance_location.id,
                        "name": attendance_location.name,
                        "description": attendance_location.description,
                    }
                    for attendance_location in attendance_location_ids
                ],
            },
        )
