# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Rafis Bikbov <https://it-projects.info/team/bikbov>
# Copyright 2021 Denis Mudarisov <https://github.com/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import json
import logging

import werkzeug

from odoo import http
from odoo.http import request
from odoo.tools import date_utils

from odoo.addons.web.controllers.main import ensure_db

from ..config import BASE_API

_logger = logging.getLogger(__name__)


class OAS(http.Controller):
    @http.route(
        ["/doc/api-docs/index.html"],
        methods=["GET"],
        type="http",
        auth="public",
    )
    def index(self, **params):
        self._get_api_urls()
        primary_name = params.get("urls.primaryName")
        swagger_settings = {
            "urls": self._get_api_urls(),
            "urls.primaryName": primary_name,
        }
        values = {"swagger_settings": swagger_settings}
        return request.render(" spp_api.openapi", values)

    def _get_api_urls(self):
        """
        This method lookup into the dictionary of registered REST service
        for the current database to built the list of available REST API
        :return:
        """

        namespaces = (
            http.request.env["spp_api.namespace"].sudo().search([["active", "=", True]])
        )
        api_urls = []
        for namespace in namespaces:
            api_urls.append(
                {
                    "name": "{}: {}".format(namespace.name, namespace.version_name),
                    "url": namespace.spec_url,
                }
            )

        # services_registry = _rest_services_databases.get(request.env.cr.dbname, {})
        # api_urls = []
        # for rest_root_path, spec in list(services_registry.items()):
        #     collection_path = rest_root_path[1:-1]  # remove '/'
        #     collection_name = spec["collection_name"]
        #     for service in self._get_service_in_collection(collection_name):
        #         api_urls.append(
        #             {
        #                 "name": "{}: {}".format(collection_path, service._usage),
        #                 "url": "/api-docs/%s/%s.json"
        #                 % (collection_path, service._usage),
        #             }
        #         )
        # api_urls = sorted(api_urls, key=lambda k: k["name"])
        return api_urls

    @http.route(
        "/" + BASE_API + "/<namespace_name>/<version>/swagger.json",
        type="http",
        auth="none",
        csrf=False,
    )
    def oas_json_spec_download(self, namespace_name, version, **kwargs):
        ensure_db()
        namespace = (
            http.request.env["spp_api.namespace"]
            .sudo()
            .search([("name", "=", namespace_name), ("version_name", "=", version)])
        )
        if not namespace:
            raise werkzeug.exceptions.NotFound()
        if namespace.token != kwargs.get("token"):
            raise werkzeug.exceptions.Forbidden()

        response_params = {"headers": [("Content-Type", "application/json")]}
        if "download" in kwargs:
            response_params = {
                "headers": [
                    ("Content-Type", "application/octet-stream; charset=binary"),
                    ("Content-Disposition", http.content_disposition("swagger.json")),
                ],
                "direct_passthrough": True,
            }

        return werkzeug.wrappers.Response(
            json.dumps(namespace.get_oas(version), default=date_utils.json_default),
            status=200,
            **response_params
        )
