from odoo import http
from odoo.http import request


class MainController(http.Controller):
    @http.route("/get_maptiler_api_key", type="json", auth="user")
    def get_maptiler_api_key(self):
        map_tiler_api_key = request.env["ir.config_parameter"].sudo().get_param("spp_base_gis.map_tiler_api_key")
        web_base_url = request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        return {"mapTilerKey": map_tiler_api_key, "webBaseUrl": web_base_url}
