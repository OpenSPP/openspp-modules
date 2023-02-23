from odoo import api, models


class CustomFilterMixin(models.AbstractModel):
    _name = "custom.filter.mixin"
    _description = "Custom Filter Mixin"

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """Customizing searchable attribute for fields in model.

        Usage:

        - Create / Inherit a model then set new model to inherit this model.

        - Add a field [even stored field] / Altering an old field [even stored field]

        - Add param `allow_filter=True` if you want to show field from UI filtering.

        :param list[str] allfields: list of fields to document, all if empty or not provided

        :param list[str] attributes: list of description attributes to return for each field,
            all if empty or not provided

        :rtype: dictionary

        :return: dict of field name and its attributes

        :example:

        class ResPartner(models.Model):
            _name = "res.partner"
            _inherit = ["res.partner", "custom.filter.mixin"]

            active = fields.Boolean(
                ...,
                allow_filter=True,
                ...
            )
            newfield = fields.Text(
                ...,
                allow_filter=True,
                ...
            )
        """
        res = super().fields_get(allfields, attributes)
        if self.user_has_groups("base.group_no_one"):
            return res
        for fname in res.keys():
            if fname == "id":
                allow_filter = getattr(self._fields[fname], "allow_filter", True)
            else:
                allow_filter = getattr(self._fields[fname], "allow_filter", False)
            if res[fname].get("searchable"):
                res[fname]["searchable"] = allow_filter and res[fname]["searchable"]
            if res[fname].get("exportable"):
                res[fname]["exportable"] = allow_filter and res[fname]["exportable"]

        return res

    def _valid_field_parameter(self, field, name):
        return name == "allow_filter" or super()._valid_field_parameter(field, name)
