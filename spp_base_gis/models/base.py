import logging

from odoo import _, api, models
from odoo.exceptions import MissingError, UserError

from .. import fields as geo_fields

_logger = logging.getLogger(__name__)


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """Add geo_type definition for geo fields"""
        res = super().fields_get(allfields=allfields, attributes=attributes)
        for f_name in res:
            field = self._fields.get(f_name)
            if field and field.type.startswith("geo_"):
                geo_type = {
                    "type": field.type,
                    "dim": int(field.dim),
                    "srid": field.srid,
                    "geo_type": field.geo_type,
                }
                res[f_name]["geo_type"] = geo_type
        return res

    @api.model
    def _get_gis_view(self):
        gis_view = (
            self.env["ir.ui.view"]
            .sudo()
            .search(
                [("model", "=", self._name), ("type", "=", "gis")],
                limit=1,
            )
        )
        if not gis_view:
            raise UserError(
                _("No GIS view defined for the model %s. Please create a view or modify view mode") % self._name,
            )
        return gis_view

    @api.model
    def set_gis_field_name(self, in_tuple):
        if not in_tuple:
            return in_tuple
        field_obj = self.env["ir.model.fields"]
        name = field_obj.browse(in_tuple[0]).name
        return (in_tuple[0], name, in_tuple[1], field_obj.browse(in_tuple[0]).field_description)

    @api.model
    def get_gis_layers(self, view_id=None, view_type="gis", **options):
        view_obj = self.env["ir.ui.view"]

        if not view_id:
            view = self._get_gis_view()
        else:
            view = view_obj.browse(view_id)
        gis_layers = {
            "backgrounds": view.raster_layer_ids.read(),
            "default_zoom": view.default_zoom,
        }

        layer_dict_list = view.data_layer_ids.read()
        res_model = view.data_layer_ids._name

        for layer_dict in layer_dict_list:
            layer_dict["attribute_field_id"] = self.set_gis_field_name(layer_dict.get("attribute_field_id", False))
            layer_dict["geo_field_id"] = self.set_gis_field_name(layer_dict.get("geo_field_id", False))
            layer_dict["resModel"] = res_model
            layer_dict["model"] = layer_dict["model_name"]

        gis_layers["actives"] = layer_dict_list
        return gis_layers

    @api.model
    def get_edit_info_for_gis_column(self, column):
        raster_obj = self.env["spp.gis.raster.layer"]

        field = self._fields.get(column)
        if not field or not isinstance(field, geo_fields.GeoField):
            raise ValueError(_("%s column does not exists or is not a geo field") % column)
        view = self._get_gis_view()
        raster = raster_obj.search([("view_id", "=", view.id)], limit=1)
        if not raster:
            raise MissingError(_("No raster layer for view %s") % (view.name,))
        return {
            "edit_raster": raster.read()[0],
            "srid": field.srid,
            "default_zoom": view.default_zoom,
            "default_center": view.default_center,
        }
