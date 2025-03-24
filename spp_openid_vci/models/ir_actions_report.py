from odoo import models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _get_rendering_context(self, report, docids, data):
        data = super()._get_rendering_context(report, docids, data)
        web_base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url", default="")
        data["logo_url"] = f"{web_base_url}/spp_openid_vci/static/description/icon.png"
        return data
