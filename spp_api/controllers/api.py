# Copyright 2018, XOE Solutions
# Copyright 2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Rafis Bikbov <https://it-projects.info/team/bikbov>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
# pylint: disable=redefined-builtin
import json
import logging

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

        data = path._post_treatment_values(kw)

        records = self.get_records(path.model, kw)
        obj = records.create(data)
        return successful_response(201, obj.id)

    # ReadMulti (optional: filters, offset, limit, order, include_fields, exclude_fields):
    @pinguin.route(
        _api_endpoint_model, methods=["GET"], type="http", auth="none", csrf=False
    )
    def read_multi__GET(self, namespace, version, model, **kw):
        path = kw.get("path")
        del kw["path"]
        path.search_treatment_kwargs(kw)

        records = self.get_records(path.model, kw)
        response_data = {
            "results": records.search_read(**kw),
            "total": records.search_count(kw.get("domain", [])),
            "offset": kw.get("offset", 0),
            "limit": kw.get("limit", 0),
            "version": version,
        }
        return successful_response(200, response_data)

    # ReadOne (optional: include_fields, exclude_fields)
    @pinguin.route(
        _api_endpoint_model_id, methods=["GET"], type="http", auth="none", csrf=False
    )
    def read_one__GET(self, namespace, version, model, id, **kw):
        path = kw.get("path")
        del kw["path"]
        path.read_treatment_kwargs(kw)
        # read_domain = path.eval_domain(path.filter_domain)

        # records = self.get_records(path.model, kw)
        # read_domain += [('id', '=', id)]
        # obj = records.search(read_domain, limit=1)
        # if not obj:
        #     raise werkzeug.exceptions.HTTPException(
        #         response=error_response(*CODE__obj_not_found)
        #     )
        obj = self.get_record(path.model, id, path, kw)
        result = obj.read(**kw)
        response_data = result and result[0] or {}
        _logger.info("response_data: %s", response_data)
        return json.dumps(response_data)

    # UpdateOne
    @pinguin.route(
        _api_endpoint_model_id, methods=["PUT"], type="http", auth="none", csrf=False
    )
    def update_one__PUT(self, namespace, version, model, id, **kw):
        path = kw.get("path")
        del kw["path"]
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
        return successful_response(200, obj.id)

    # UnlinkOne
    @pinguin.route(
        _api_endpoint_model_id, methods=["DELETE"], type="http", auth="none", csrf=False
    )
    def unlink_one__DELETE(self, namespace, version, model, id, **kw):
        path = kw.get("path")
        del kw["path"]
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
        obj.unlink()
        return successful_response(pinguin.CODE__ok_no_content, obj.id)

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

        obj = self.get_record(path.model, id, path, method_params)
        kwargs = path.custom_treatment_values(method_params)
        data = getattr(obj, path.function)(**kwargs)
        obj.flush()  # to recompute fields
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

        records = self.get_records(path.model, method_params)
        ids = ids and ids.split(",") or []
        ids = [int(i) for i in ids]
        kwargs = path.custom_treatment_values(method_params)

        # limit to the authorized domain and ids
        domain = path.eval_domain(path.filter_domain)
        domain += [("id", "in", ids)]

        records = records.search(domain)

        data = getattr(records, path.function)(**kwargs)
        records.flush()  # to recompute fields
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
