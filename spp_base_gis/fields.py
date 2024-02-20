import logging

from odoo import api, fields
from odoo.tools import sql

_logger = logging.getLogger(__name__)

try:
    import geojson
    from pyproj import Transformer
    from shapely import wkb
    from shapely.geometry import LineString, Point, Polygon, shape
    from shapely.ops import transform
except ImportError:
    _logger.warning("Geospatial libraries not available.")


def transform_geometry(geometry, from_srid, to_srid):
    transformer = Transformer.from_crs(f"EPSG:{from_srid}", f"EPSG:{to_srid}", always_xy=True)
    return transform(transformer.transform, geometry)  # Using Shapely's transform


class GeoField(fields.Field):
    """
    Base class for geospatial fields, handling common attributes and methods.
    """

    _type = "geo"
    geo_type = None  # To be defined in subclasses
    srid = 4326  # Default SRID, can be overridden in subclasses
    column_type = ("geometry", "geometry")

    def __init__(self, string="GeoField", **kwargs):
        super().__init__(string=string, **kwargs)
        self.index = kwargs.get("index", True)  # Enable GiST index by default

    def convert_to_column(self, value, record, values=None, validate=True):
        if validate:
            self.validate_value(value)
        return wkb.dumps(shape(value), hex=True) if value else None

    def convert_to_cache(self, value, record, validate=True):
        return shape(wkb.loads(value, hex=True)) if value else None

    def validate_value(self, value):
        # Placeholder for validation logic, e.g., checking geometry validity
        pass

    @api.model
    def create_geo_column(self, model, column_name):
        table_name = model._table
        geo_type = self.geo_type.upper()
        srid = self.srid
        index = self.index
        column_type = f"geometry({geo_type}, {srid})"

        sql.create_column(table_name, column_name, column_type)
        if index:
            sql.create_index(table_name, column_name, index_type="GIST")

        _logger.info(f"Geospatial column {column_name} of type {column_type} created in {table_name}.")

    def transform_geometry_srid(self, value, from_srid=4326, to_srid=3857):
        if value is None:
            return None
        geom = shape(value)  # Assuming value is in GeoJSON-like dict format
        transformed_geom = transform_geometry(geom, from_srid, to_srid)
        return geojson.dumps(transformed_geom)  # Convert back to GeoJSON string


class GeoPointField(GeoField):
    geo_type = "POINT"

    def convert_to_column(self, value, record, values=None, validate=True):
        # Ensure value is a Shapely Point or convertible to it
        if isinstance(value, dict):
            value = Point(value.get("x"), value.get("y"))
        elif not isinstance(value, Point):
            raise ValueError("Value must be a dict with 'x' and 'y' keys or a Shapely Point")
        return super().convert_to_column(value, record, values, validate)

    def convert_to_cache(self, value, record, validate=True):
        # Convert WKB to Shapely Point
        point = super().convert_to_cache(value, record, validate)
        return {"x": point.x, "y": point.y} if point else None


class GeoLineStringField(GeoField):
    geo_type = "LINESTRING"

    def convert_to_column(self, value, record, values=None, validate=True):
        # Ensure value is a list of point tuples or a Shapely LineString
        if isinstance(value, list):
            value = LineString(value)
        elif not isinstance(value, LineString):
            raise ValueError("Value must be a list of point tuples or a Shapely LineString")
        return super().convert_to_column(value, record, values, validate)

    def convert_to_cache(self, value, record, validate=True):
        # Convert WKB to list of point tuples
        linestring = super().convert_to_cache(value, record, validate)
        return [(point.x, point.y) for point in linestring.coords] if linestring else None


class GeoPolygonField(GeoField):
    geo_type = "POLYGON"

    def convert_to_column(self, value, record, values=None, validate=True):
        # Ensure value is a list of lists of point tuples or a Shapely Polygon
        if isinstance(value, list):
            # Assuming value is a list of exterior coordinates, possibly followed by interiors
            value = Polygon(value[0], value[1:] if len(value) > 1 else [])
        elif not isinstance(value, Polygon):
            raise ValueError("Value must be a list of lists of point tuples or a Shapely Polygon")
        return super().convert_to_column(value, record, values, validate)

    def convert_to_cache(self, value, record, validate=True):
        # Convert WKB to list of lists of point tuples
        polygon = super().convert_to_cache(value, record, validate)
        exterior = [(point.x, point.y) for point in polygon.exterior.coords]
        interiors = [[(point.x, point.y) for point in interior.coords] for interior in polygon.interiors]
        return [exterior] + interiors if polygon else None
