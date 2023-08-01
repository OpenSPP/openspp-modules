# Copyright 2018, XOE Solutions
# Copyright 2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Rafis Bikbov <https://it-projects.info/team/bikbov>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: disable=redefined-builtin
import json
import logging
import uuid

import werkzeug

from odoo import http
from odoo.http import request

from odoo.addons.spp_base_api.lib.pinguin import error_response

from . import pinguin
from .pinguin import CODE__obj_not_found, successful_response

_logger = logging.getLogger(__name__)

#################################################################
# Odoo REST API                                                 #
#  Version 1                                                    #
# --------------------------------------------------------------#
# The current api version is considered stable, although        #
# the exposed models and methods change as they are configured  #
# on the database level. Only if significant changes in the api #
# generation logic should be implemented in the future          #
# a version bump should be considered.                          #
#################################################################

API_ENDPOINT = "/api"


class ApiV1Controller(http.Controller):
    """Implements the REST API V1 endpoint.
    .. methods:

        CRUD Methods:
        - `POST     .../<model>`               -> `CreateOne`
        - `PUT      .../<model>/<id>`          -> `UpdateOne`
        - `GET      .../<model>`               -> `ReadMulti`
        - `GET      .../<model>/<id>`          -> `ReadOne`
        - `DELETE   .../<model>/<id>`          -> `UnlinkOne`

        Auxiliary Methods:
        - `PATCH    .../<model>/<id>/<method>`               -> `Call Method on Singleton Record`
        - `PATCH    .../<model>/<method>`                    -> `Call Method on RecordSet`
        - `GET      .../report/pdf/<report_external_id>`     -> `Get Report as PDF`
        - `GET      .../report/html/<report_external_id>`    -> `Get Report as HTML`
    """

    _api_endpoint = API_ENDPOINT + "/<namespace>"
    _api_endpoint = _api_endpoint + "/<version>"
    # CreateOne # ReadMulti
    _api_endpoint_model = _api_endpoint + "/<model>"
    # ReadOne # UpdateOne # UnlinkOne
    _api_endpoint_model_id = _api_endpoint + "/<model>/<int:id>"
    # Call Method on Singleton Record
    _api_endpoint_model_id_method = (
        _api_endpoint + "/<model>/<int:id>/call/<method_name>"
    )
    # Call Method on RecordSet
    _api_endpoint_model_method = _api_endpoint + "/<model>/call/<method_name>"
    _api_endpoint_model_method_ids = _api_endpoint + "/<model>/call/<method_name>/<ids>"
    # Get Reports
    _api_report_docids = (
        _api_endpoint
        + "/report/<any(pdf, html):converter>/<report_external_id>/<docids>"
    )

    def get_records(self, model, kwargs):
        user = request.env.user
        records = request.env[model].with_user(user)
        # Used *in* of check kwargs to force remove
        # context when value {} is sending
        if "context" in kwargs:
            records = records.with_context(**kwargs.get("context"))
            del kwargs["context"]

        return records

    def get_record(self, model, id, path, kwargs):
        records = self.get_records(model, kwargs)
        read_domain = path.eval_domain(path.filter_domain)
        read_domain += [("id", "=", id)]
        obj = records.search(read_domain, limit=1)
        if not obj:
            raise werkzeug.exceptions.HTTPException(
                response=error_response(*CODE__obj_not_found)
            )
        return obj

    # #################
    # # CRUD Methods ##
    # #################

    # CreateOne`
    @pinguin.route(
        _api_endpoint_model, methods=["POST"], type="http", auth="none", csrf=False
    )
    def create_one__POST(self, namespace, version, model, **kw):
        path = kw.get("path")
        del kw["path"]

        request_id = kw.get("request_id")
        if "request_id" in kw:
            del kw["request_id"]

        data = path.post_treatment_values(kw)

        records = self.get_records(path.model, kw)
        obj = records.create(data)

        # Request Log
        self.create_api_log(
            path,
            "request",
            request_data=json.dumps(data, default=str),
            request_id=request_id,
        )

        # Response Log
        self.create_api_log(path, "response", response_data=str(obj.id))

        return successful_response(201, obj.id)

    # ReadMulti (optional: filters, offset, limit, order, include_fields, exclude_fields):
    @pinguin.route(
        _api_endpoint_model, methods=["GET"], type="http", auth="none", csrf=False
    )
    def read_multi__GET(self, namespace, version, model, **kw):
        path = kw.get("path")
        del kw["path"]

        kw_copy = kw.copy()

        request_id = kw.get("request_id", None)
        if "request_id" in kw:
            del kw["request_id"]

        kw = path.search_treatment_kwargs(kw)
        records = self.get_records(path.model, kw)
        records = records.search_read(**kw)

        response_data = {
            "results": records,
            "total": len(records),
            "offset": kw.get("offset", 0),
            "limit": kw.get("limit", 0),
            "version": version,
        }

        # Request Log
        self.create_api_log(
            path,
            "request",
            request_parameter=json.dumps(kw_copy, default=str),
            request_id=request_id,
        )

        # Response Log
        self.create_api_log(
            path, "response", response_data=json.dumps(response_data, default=str)
        )

        return successful_response(200, response_data)

    # ReadOne (optional: include_fields, exclude_fields)
    @pinguin.route(
        _api_endpoint_model_id, methods=["GET"], type="http", auth="none", csrf=False
    )
    def read_one__GET(self, namespace, version, model, id, **kw):
        path = kw.get("path")
        del kw["path"]

        kw_copy = kw.copy()

        request_id = kw.get("request_id", None)
        if "request_id" in kw:
            del kw["request_id"]

        path.read_treatment_kwargs(kw)

        obj = self.get_record(path.model, id, path, kw)
        result = obj.search_read(fields=kw["fields"])

        response_data = result and result[0] or {}
        _logger.info("response_data: %s", response_data)

        # Request Log
        self.create_api_log(
            path,
            "request",
            request_parameter=json.dumps(kw_copy, default=str),
            request_id=request_id,
        )

        # Response Log
        self.create_api_log(
            path, "response", response_data=json.dumps(response_data, default=str)
        )

        return successful_response(200, response_data)

    # UpdateOne
    @pinguin.route(
        _api_endpoint_model_id, methods=["PUT"], type="http", auth="none", csrf=False
    )
    def update_one__PUT(self, namespace, version, model, id, **kw):
        path = kw.get("path")
        del kw["path"]

        request_id = kw.get("request_id")
        if "request_id" in kw:
            del kw["request_id"]

        data = path.post_treatment_values(kw)
        # read_domain = path.eval_domain(path.filter_domain)
        #
        # records = self.get_records(path.model, kw)
        # read_domain += [('id', '=', id)]
        # obj = records.search(read_domain, limit=1)
        # if not obj:
        #     raise werkzeug.exceptions.HTTPException(
        #         response=error_response(*CODE__obj_not_found)
        #     )
        obj = self.get_record(path.model, id, path, kw)
        obj.write(data)

        # Request Log
        self.create_api_log(
            path,
            "request",
            request_data=json.dumps(data, default=str),
            request_id=request_id,
        )

        # Response Log
        self.create_api_log(path, "response", response_data=str(obj.id))

        return successful_response(200, obj.id)

    # UnlinkOne
    @pinguin.route(
        _api_endpoint_model_id, methods=["DELETE"], type="http", auth="none", csrf=False
    )
    def unlink_one__DELETE(self, namespace, version, model, id, **kw):
        path = kw.get("path")
        del kw["path"]

        request_id = kw.get("request_id")
        if "request_id" in kw:
            del kw["request_id"]

        obj = self.get_record(path.model, id, path, kw)
        name = obj.name
        obj.unlink()

        response = f"{name} is successfully deleted"

        # Request Log
        self.create_api_log(path, "request", request_id=request_id)

        # Response Log
        self.create_api_log(path, "response", response_data=response)

        return successful_response(pinguin.CODE__ok_no_content, response)

    # ######################
    # # Auxiliary Methods ##
    # ######################

    # Call Method on Singleton Record (optional: method parameters)
    @pinguin.route(
        _api_endpoint_model_id_method,
        methods=["PATCH"],
        type="http",
        auth="none",
        csrf=False,
    )
    def call_method_one__PATCH(
        self, namespace, version, model, id, method_name, **method_params
    ):
        path = method_params.get("path")
        del method_params["path"]

        request_id = method_params.get("request_id")
        if "request_id" in method_params:
            del method_params["request_id"]

        obj = self.get_record(path.model, id, path, method_params)
        kwargs = path.custom_treatment_values(method_params)
        data = getattr(obj, path.function)(**kwargs)

        obj.flush()  # to recompute fields

        # Request Log
        self.create_api_log(path, "request", request_id=request_id)

        # Response Log
        self.create_api_log(path, "response", response_data=data)

        return successful_response(200, data=data)

    # Call Method on RecordSet (optional: method parameters)
    @pinguin.route(
        [_api_endpoint_model_method, _api_endpoint_model_method_ids],
        methods=["PATCH"],
        type="http",
        auth="none",
        csrf=False,
    )
    def call_method_multi__PATCH(
        self, namespace, version, model, method_name, ids=None, **method_params
    ):
        path = method_params.get("path")
        del method_params["path"]

        method_params_copy = method_params.copy()

        request_id = method_params.get("request_id")
        if "request_id" in method_params:
            del method_params["request_id"]

        records = self.get_records(path.model, method_params)
        ids = ids and ids.split(",") or []
        ids = [int(i) for i in ids]
        kwargs = path.custom_treatment_values(method_params)

        # limit to the authorized domain and ids
        domain = path.get_domain(method_params)
        if ids:
            domain += [("id", "in", ids)]

        records = records.search(domain)

        data = getattr(records, path.function)(**kwargs)
        records.flush()  # to recompute fields

        # Request Log
        self.create_api_log(
            path,
            "request",
            request_parameter=json.dumps(method_params_copy, default=str),
            request_id=request_id,
        )

        # Response Log
        self.create_api_log(path, "response", response_data=data)

        return successful_response(200, data=data)

    # Get Report
    @pinguin.route(
        _api_report_docids, methods=["GET"], type="http", auth="none", csrf=False
    )
    def report__GET(self, converter, namespace, report_external_id, docids):
        return pinguin.wrap__resource__get_report(
            namespace=namespace,
            report_external_id=report_external_id,
            docids=docids,
            converter=converter,
            success_code=pinguin.CODE__success,
        )

    def create_api_log(self, path, http_type, **kwargs):
        reply_id = ""
        request_id = kwargs.get("request_id", False)

        if http_type == "response":
            # To make sure reply_id is unique
            while True:
                reply_id = str(uuid.uuid4())
                if (
                    not request.env["spp_api.log"]
                    .search([("reply_id", "=", reply_id)])
                    .exists()
                ):
                    break
        elif http_type == "request":
            # Check if request_id is in parameter/data and if it is already taken.
            if not request_id:
                raise werkzeug.exceptions.HTTPException(
                    response=error_response(
                        400, "Bad Request", "request_id is required."
                    )
                )
            if (
                request.env["spp_api.log"]
                .search([("request_id", "=", request_id)])
                .exists()
            ):
                raise werkzeug.exceptions.HTTPException(
                    response=error_response(
                        400, "Bad Request", "request_id is already taken."
                    )
                )

        vals = {
            "method": path.method,
            "http_type": http_type,
            "model": path.model,
            "request": http.request.httprequest.full_path,
            "request_id": request_id,
            "request_parameter": kwargs.get("request_parameter", False),
            "request_data": kwargs.get("request_data", False),
            "reply_id": reply_id,
            "response_data": kwargs.get("response_data", False),
        }

        request.env["spp_api.log"].create(vals)
