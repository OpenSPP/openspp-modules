# Copyright 2021 Denis Mudarisov <https://github.com/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import logging

from odoo.http import (
    Dispatcher,
)

try:
    import psutil
except ImportError:
    psutil = None


_logger = logging.getLogger(__name__)


class ApiJsonRequest(Dispatcher):
    routing_type = "apijson"

    def __init__(self, request):
        super().__init__(request)

    @classmethod
    def is_compatible_with(cls, request):
        return True

    def dispatch(self, endpoint, args):
        self.request.params = dict(**args, **self.request.get_http_params())

        if self.request.db:
            result = self.request.registry["ir.http"]._dispatch(endpoint)
        else:
            result = endpoint(**self.request.params)

        return self.request.make_json_response(result.json, status=result.status)
