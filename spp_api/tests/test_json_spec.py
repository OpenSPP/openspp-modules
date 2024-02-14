# Copyright 2018-2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018 Rafis Bikbov <https://it-projects.info/team/bikbov>
# Copyright 2021 Denis Mudarisov <https://github.com/trojikman>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from bravado_core.spec import Spec
from swagger_spec_validator import SwaggerValidationError

from odoo.tests import tagged
from odoo.tests.common import HttpCase
from odoo.tools import config, mute_logger


@tagged("post_install", "-at_install")
class TestJsonSpec(HttpCase):
    def test_json_base(self):
        db = self.env.cr.dbname
        resp = self.url_open(
            "http://localhost:%d/api/demo/v1/swagger.json?token=demo_token&db=%s" % (config["http_port"], db),
            timeout=30,
        )
        self.assertEqual(resp.status_code, 200, "Cannot get json spec")
        # TODO add checking  actual content of the json

    @mute_logger("py.warnings")
    def test_OAS_scheme_for_demo_data_is_valid(self):
        db = self.env.cr.dbname
        resp = self.url_open(
            "http://localhost:%d/api/demo/v1/swagger.json?token=demo_token&db=%s" % (config["http_port"], db),
            timeout=30,
        )
        spec_dict = resp.json()
        try:
            Spec.from_dict(spec_dict, config={"validate_swagger_spec": True})
        except SwaggerValidationError as e:
            self.fail("A JSON Schema for Swagger 2.0 is not valid:\n %s" % e)

    def test_03_api_swagger_view(self):
        db = self.env.cr.dbname
        url = self.env["ir.config_parameter"].get_param("web.base.url", f"http://localhost:{config['http_port']}")
        resp = self.url_open(f"{url}/api/swagger-doc/demo/v1?token=demo_token&db={db}")
        self.assertEqual(resp.status_code, 200)
        resp = self.url_open(f"{url}/api/swagger-doc/demo1/v1?token=demo_token&db={db}")
        self.assertEqual(resp.status_code, 404)
        resp = self.url_open(f"{url}/api/swagger-doc/demo/v1?token=demo_token_1&db={db}")
        self.assertEqual(resp.status_code, 403)
