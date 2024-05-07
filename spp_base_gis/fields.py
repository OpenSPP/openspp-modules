import json
import logging

from odoo import _, api, fields
from odoo.exceptions import ValidationError
from odoo.tools import sql

_logger = logging.getLogger(__name__)

try:
    import geojson
    from pyproj import Transformer
    from shapely.geometry import LineString, Point, Polygon, shape
    from shapely.geometry.base import BaseGeometry
    from shapely.ops import transform
    from shapely.wkb import loads as wkbloads
    from shapely.wkt import loads as wktloads
except ImportError:
    _logger.warning("Geospatial libraries not available.")

geo_types = {}


def transform_geometry(geometry, from_srid, to_srid):
    transformer = Transformer.from_crs(f"EPSG:{from_srid}", f"EPSG:{to_srid}", always_xy=True)
    return transform(transformer.transform, geometry)  # Using Shapely's transform


def value_to_shape(value, use_wkb=False):
    """Transforms input into a Shapely object"""
    if not value:
        return wktloads("GEOMETRYCOLLECTION EMPTY")
    if isinstance(value, str):
        if "{" in value:
            geo_dict = geojson.loads(value)
            return shape(geo_dict)
        elif use_wkb:
            return wkbloads(value, hex=True)
        else:
            return wktloads(value)
    elif hasattr(value, "wkt"):
        if isinstance(value, BaseGeometry):
            return value
        else:
            return wktloads(value.wkt)
    else:
        raise TypeError(_("Write/create/search geo type must be wkt/geojson " "string or must respond to wkt"))


class GeoField(fields.Field):
    """
    Base class for geospatial fields, handling common attributes and methods.
    """

    _type = "geo"
    geo_type = None  # To be defined in subclasses
    geo_class = None  # To be defined in subclasses
    srid = 4326  # Default SRID, can be overridden in subclasses
    column_type = ("geometry", "geometry")
    dim = 2

    def __init__(self, string="GeoField", **kwargs):
        self.index = kwargs.get("index", True)  # Enable GiST index by default
        if isinstance(self, GeoField) and self.geo_type and self.geo_class:
            geo_types.update({self.geo_type: self.geo_class})
        super().__init__(string=string, **kwargs)

    def validate_value(self, value):
        try:
            result = json.loads(value)
            if isinstance(result, dict):
                shapely_geometry = shape(result)
                if not result.get("coordinates") or not result.get("type"):
                    raise ValidationError(_("type and coordinates should be in the geojson"))
                elif result["type"] not in geo_types:
                    raise ValidationError(_("%(geo_type)s is not a valid type.") % {"geo_type": result["type"]})
                elif not isinstance(shapely_geometry, geo_types[result["type"]]):
                    raise ValidationError(_("Value must ba a Shapely %(type)s") % {"type": result["type"]})
            else:
                raise ValidationError("Value should be a geojson")
        except json.JSONDecodeError as e:
            raise ValidationError(e) from e

    @api.model
    def create_geo_column(self, model, column_name):
        table_name = model._table
        cr = model._cr
        geo_type = self.geo_type.upper()
        srid = self.srid
        index = self.index
        dim = self.dim
        column_type = f"geometry({geo_type}, {srid})"

        cr.execute(
            "SELECT AddGeometryColumn( %s, %s, %s, %s, %s)",
            (table_name, column_name, srid, geo_type, dim),
        )

        if index:
            index_name = f"{table_name}_{column_name}_gist_index"
            sql.create_index(model._cr, index_name, table_name, [column_name], method="GIST")

        _logger.info(f"Geospatial column {column_name} of type {column_type} created in {table_name}.")

    @classmethod
    def transform_geometry_srid(cls, value, from_srid=4326, to_srid=3857, output="json"):
        if value is None:
            return None
        geom = shape(value)  # Assuming value is in GeoJSON-like dict format
        transformed_geom = transform_geometry(geom, from_srid, to_srid)
        if output == "geom":
            return transformed_geom
        return geojson.dumps(transformed_geom)  # Convert back to GeoJSON string

    def convert_to_column(self, value, record, values=None, validate=True):
        if not value:
            return None
        if validate:
            self.validate_value(value)
        shape_to_write = value_to_shape(value)
        if shape_to_write.is_empty:
            return None
        else:
            return f"SRID={self.srid};{shape_to_write.wkt}"

    def convert_to_cache(self, value, record, validate=True):
        val = value
        if isinstance(val, bytes | str):
            try:
                int(val, 16)
            except Exception:
                value = value_to_shape(value, use_wkb=False)
        if isinstance(value, BaseGeometry):
            val = value.wkb_hex
        return val

    def convert_to_record(self, value, record):
        if not value:
            return False
        return value_to_shape(value, use_wkb=True)

    def convert_to_read(self, value, record, use_display_name=True):
        if not isinstance(value, BaseGeometry):
            shape = wkbloads(value, hex=True) if value else False
        else:
            shape = value
        if not shape or shape.is_empty:
            return False
        return geojson.dumps(shape)

    def check_geometry_columns(self, cursor, table_name, column_name, expected_values):
        query = """
            SELECT srid, type, coord_dimension
            FROM geometry_columns
            WHERE f_table_name = %s AND f_geometry_column = %s
        """
        cursor.execute(query, (table_name, column_name))
        return cursor.fetchone() == expected_values

    def update_geometry_columns(self, cursor, table_name, column_name, expected_values):
        if not self.check_geometry_columns(cursor, table_name, column_name, expected_values):
            raise ValidationError(
                f"Geometry column validation failed for table '{table_name}', column '{column_name}'."
            )

    def update_db_column(self, model, column_info):
        cursor = model._cr
        table_name = model._table
        column_name = self.name

        if not column_info:
            self.create_geo_column(model, column_name)
            return

        if column_info["udt_name"] == self.column_type[0]:
            return

        expected_geo_values = (self.srid, self.geo_type.upper(), self.dim)
        self.update_geometry_columns(cursor, table_name, column_name, expected_geo_values)

        # if column_info["udt_name"] in self.column_cast_from:
        #     sql.convert_column(cursor, table_name, column_name, self.column_type[1])
        # else:
        #     new_column_name = sql.find_unique_column_name(cursor, table_name, self.name)
        #     if column_info["is_nullable"] == "NO":
        #         sql.drop_not_null(cursor, table_name, column_name)
        #     sql.rename_column(cursor, table_name, column_name, new_column_name)
        #     sql.create_column(cursor, table_name, column_name, self.column_type[1], self.string)


class GeoPointField(GeoField):
    type = "geo_point"
    geo_class = Point
    geo_type = Point.__name__


class GeoLineStringField(GeoField):
    type = "geo_line"
    geo_class = LineString
    geo_type = LineString.__name__


class GeoPolygonField(GeoField):
    type = "geo_polygon"
    geo_class = Polygon
    geo_type = Polygon.__name__


# class GeoMultiPolygonField(GeoField):
#     type = "geo_multi_polygon"
#     geo_class = MultiPolygon
#     geo_type = MultiPolygon.__name__


fields.GeoPointField = GeoPointField
fields.GeoLineStringField = GeoLineStringField
fields.GeoPolygonField = GeoPolygonField
# fields.GeoMultiPolygonField = GeoMultiPolygonField
