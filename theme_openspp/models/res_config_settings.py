from odoo import api, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Commented (for now) since fields_view_get is now obsolete and replaced with _get_view with
    # different return values
    # @api.model
    # def _get_view(self, view_id=None, view_type="form", **options):
    #     arch, view = super()._get_view(view_id, view_type, **options)

    #     page_name = view["name"]

    #     if not page_name == "res.config.settings.view.form":
    #         return arch, view

    #     doc = arch

    #     query = "//div[div[field[@widget='upgrade_boolean']]]"
    #     for item in doc.xpath(query):
    #         item.attrib["class"] = "d-none"

    #     arch = doc
    #     return arch, view
