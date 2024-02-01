from odoo import models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # fields_view_get replaced as _get_view with a different return value
    # need to fix this.

    # @api.model
    # def _get_view(
    #     self, view_id=None, view_type="form", **options
    # ):
    #     arch, view = super()._get_view(
    #         view_id, view_type, **options
    #     )

    #     page_name = view["name"]
    #     if not page_name == "res.config.settings.view.form":
    #         return arch, view

    #     doc = arch

    #     query = "//div[div[field[@widget='upgrade_boolean']]]"
    #     for item in doc.xpath(query):
    #         item.attrib["class"] = "d-none"

    #     arch = etree.tostring(doc)

    #     return arch, view
