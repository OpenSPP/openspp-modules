import json
import uuid
from datetime import datetime, timezone

import werkzeug.wrappers

from odoo.http import Controller, request, route
from odoo.osv.expression import AND
from odoo.tools import date_utils

from ..tools import constants, verify_and_decode_signature


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


class SppDciApiServer(Controller):
    @route(
        constants.OAUTH2_ENDPOINT,
        auth="none",
        methods=["POST"],
        type="http",
        csrf=False,
    )
    def auth_get_access_token(self, **kw):
        client_id = kw.get("client_id", "")
        client_secret = kw.get("client_secret", "")
        grant_type = kw.get("grant_type", "")

        if not all([client_id, client_secret, grant_type]):
            error = {
                "error": "Bad Request",
                "error_description": "client_id, client_secret, and grant_type is required.",
            }
            return response_wrapper(400, error)

        client = (
            request.env["spp.dci.api.client.credential"]
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
        constants.SYNC_SEARCH_ENDPOINT,
        auth="none",
        methods=["POST"],
        type="http",
        csrf=False,
    )
    def retrieve_registry(self, **kw):
        auth_header = get_auth_header(request.httprequest.headers, raise_exception=True)

        access_token = (
            auth_header.replace("Bearer ", "").replace("\\n", "").encode("utf-8")
        )

        # TODO: payload of access token is not used for now
        verified, payload = verify_and_decode_signature(access_token)

        if not verified:
            return error_wrapper(401, "Invalid Access Token.")

        header = kw.get("header", "")
        header_error = self.check_content(
            header,
            "header",
            ["message_id", "message_ts", "action", "sender_id", "total_count"],
        )
        if header_error:
            return error_wrapper(header_error.get("code"), header_error.get("message"))

        message = kw.get("message", "")
        message_error = self.check_content(
            message, "message", ["transaction_id", "search_request"]
        )
        if message_error:
            return error_wrapper(
                message_error.get("code"), message_error.get("message")
            )

        message_id = header["message_id"]
        transaction_id = message.get("transaction_id")
        search_requests = message["search_request"]

        today_isoformat = datetime.now(timezone.utc).isoformat()
        correlation_id = str(uuid.uuid4())

        # Process search requests and modify search_responses
        search_responses = []
        self.process_search_requests(search_requests, today_isoformat, search_responses)

        header = {
            "message_id": message_id,
            "message_ts": today_isoformat,
            "action": "search",
            "status": "succ",
        }
        message = {
            "transaction_id": transaction_id,
            "correlation_id": correlation_id,
            "search_response": search_responses,
        }

        data = {
            "header": header,
            "message": message,
        }
        return response_wrapper(200, data)

    def check_content(self, content, label, required_parameters):
        if not content:
            return {"code": 400, "message": f"{label} is required."}

        for param in required_parameters:
            if param not in content:
                parameter_str = ", ".join(required_parameters)
                return {
                    "code": 400,
                    "message": f"{label} should have these parameters: {parameter_str}",
                }

        return None

    def process_queries(self, query_type, queries, domain):
        for query in queries:
            if query_type == constants.PREDICATE:
                query_error = self.check_content(query, "query", ["expression1"])
                if query_error:
                    return error_wrapper(
                        query_error.get("code"), query_error.get("message")
                    )

                expression = query.get("expression1")
                expression_error = self.check_content(
                    expression,
                    "expression1",
                    ["attribute_name", "operator", "attribute_value"],
                )
                if expression_error:
                    return error_wrapper(
                        expression_error.get("code"),
                        expression_error.get("message"),
                    )

                attribute_name = expression.get("attribute_name")
                if attribute_name not in constants.FIELD_MAPPING:
                    return error_wrapper(
                        400,
                        f"These are the only supported attribute name: {', '.join(constants.FIELD_MAPPING.keys())}",
                    )

                operator = expression.get("operator")
                if operator not in constants.OPERATION_MAPPING:
                    return error_wrapper(
                        400,
                        f"These are the only supported operator: {', '.join(constants.OPERATION_MAPPING.keys())}",
                    )

                attribute_value = expression.get("attribute_value")

                domain = AND(
                    [
                        domain,
                        [
                            (
                                constants.FIELD_MAPPING[attribute_name],
                                constants.OPERATION_MAPPING[operator],
                                attribute_value,
                            )
                        ],
                    ]
                )

        return domain

    def process_search_requests(
        self, search_requests, today_isoformat, search_responses
    ):
        for req in search_requests:
            req_error = self.check_content(
                req, "search_request", ["reference_id", "timestamp", "search_criteria"]
            )
            if req_error:
                return error_wrapper(req_error.get("code"), req_error.get("message"))

            search_criteria = req.get("search_criteria")
            search_criteria_error = self.check_content(
                search_criteria, "search_criteria", ["reg_type", "query_type", "query"]
            )
            if search_criteria_error:
                return error_wrapper(
                    search_criteria_error.get("code"),
                    search_criteria_error.get("message"),
                )

            query_type = search_criteria.get("query_type")
            if query_type not in constants.ALLOWED_QUERY_TYPE:
                return error_wrapper(
                    400,
                    f"query_type only accepts these values: {', '.join(constants.ALLOWED_QUERY_TYPE)}",
                )

            reg_type = search_criteria.get("reg_type")

            if reg_type not in constants.REG_TYPE_CHOICES:
                return error_wrapper(
                    400,
                    f"These are the only supported reg type: {', '.join(constants.REG_TYPE_CHOICES)}",
                )

            reference_id = req.get("reference_id")
            queries = search_criteria.get("query")

            domain = [("is_registrant", "=", True)]

            if reg_type == constants.INDIVIDUAL:
                domain.append(("is_group", "=", False))
            else:
                domain.append(("is_group", "=", True))

            # Process Queries and modify domain
            self.process_queries(query_type, queries, domain)

            if domain:
                records = request.env["res.partner"].sudo().search(domain)
                if records:
                    search_responses.append(
                        {
                            "reference_id": reference_id,
                            "timestamp": today_isoformat,
                            "status": "succ",
                            "data": {
                                "reg_record_type": "person",
                                "reg_type": reg_type,
                                "reg_records": records.get_dci_individual_registry_data(),
                            },
                            "locale": "eng",
                        }
                    )
        return search_responses
