import json

from shapely import wkt
from shapely.geometry import mapping, shape
from shapely.geometry.base import BaseGeometry

from odoo.tools import SQL


class Operator:
    """
    The Operator class is designed to facilitate spatial operations and queries within a PostgreSQL database
    using the PostGIS extension. It provides a suite of methods for constructing geometries (such as points,
    lines, and polygons), setting and transforming spatial reference identifiers (SRIDs), and generating
    spatial queries based on specified operations and geometries. This class serves as a utility for
    interacting with spatial data, making it easier to perform common spatial operations and integrate
    spatial data processing into applications.

    Attributes:
        field (Field): An object representing the spatial field associated with the class. This field
                       contains information about the spatial reference identifier (SRID) and is used
                       in spatial operations to ensure geometries are correctly interpreted within the
                       spatial reference system.
        POSTGIS_SPATIAL_RELATION (dict): A dictionary mapping spatial operation names (as used within
                                         the application) to their corresponding PostGIS function names.
                                         This allows for a flexible interface to PostGIS functions by
                                         abstracting the actual function names behind more intuitive operation
                                         names.
        ALLOWED_LAYER_TYPE (dict): A dictionary defining the allowed types of spatial layers (e.g., Point,
                                   LineString, Polygon) that can be used within the class. This ensures
                                   that operations are only performed on supported geometry types, helping
                                   to maintain data integrity and prevent errors.

    Methods:
        __init__(self, field): Constructor method that initializes a new instance of the Operator class
                               with the specified spatial field.
        st_makepoint(self, longitude, latitude): Constructs a SQL string for a PostGIS call to create a
                                                  point geometry from longitude and latitude values.
        st_makeline(self, points): Constructs a SQL string for a PostGIS call to create a line geometry
                                   from an array of point geometries.
        st_makepolygon(self, points): Constructs a SQL string for a PostGIS call to create a polygon
                                      geometry from a list of point geometries defining the polygon's
                                      boundary.
        st_setsrid(self, geom, srid): Constructs a SQL string for a PostGIS call to set the SRID for a
                                      geometry object, ensuring it is interpreted within the correct
                                      spatial reference system.
        st_transform(self, geom, srid): Constructs a SQL string for a PostGIS call to transform a
                                        geometry object to a different spatial reference system.
        create_point(self, coordinate, srid): Creates a point geometry with the given coordinates and
                                              SRID.
        create_line(self, coordinates, srid): Creates a line geometry from a list of coordinates and
                                              assigns the specified SRID.
        create_polygon(self, coordinates, srid): Creates a polygon geometry from a list of coordinates
                                                 and assigns the specified SRID.
        clean_and_validate(self, **kwargs): Validates provided keyword arguments for spatial operations,
                                            ensuring that coordinates, distances, and layer types are
                                            correctly specified and supported.
        get_postgis_query(self, operation, coordinates, distance=None, layer_type="point"): Generates
                                      and returns a PostGIS spatial query based on the specified operation,
                                      coordinates, distance, and layer type.
        validate_coordinates_for_point(self, coordinates): Validates a set of coordinates for creating
                                                           a point geometry, ensuring they represent a
                                                           valid location on Earth's surface.
        validate_coordinates_for_line_or_polygon(self, coordinates, is_polygon=False): Validates a set
                                                           of coordinates for creating line or polygon
                                                           geometries, ensuring they form valid shapes.
    """

    OPERATION_TO_RELATION = {
        "gis_intersects": "intersects",
        "gis_contains": "contains",
        "gis_within": "within",
        "gis_touches": "touches",
        "gis_crosses": "crosses",
        "gis_equals": "equals",
        "gis_disjoint": "disjoint",
        "gis_covers": "covers",
        "gis_coveredby": "coveredby",
    }

    POSTGIS_SPATIAL_RELATION = {
        "intersects": "ST_Intersects",
        "within": "ST_Within",
        "contains": "ST_Contains",
        "covers": "ST_Covers",
        "equals": "ST_Equals",
        "coveredby": "ST_CoveredBy",
        "disjoint": "ST_Disjoint",
        "crosses": "ST_Crosses",
        "touches": "ST_Touches",
    }
    ALLOWED_LAYER_TYPE = {
        "Point": "point",
        "LineString": "line",
        "Polygon": "polygon",
    }

    def __init__(self, field):
        self.field = field

    def st_makepoint(self, longitude, latitude):
        """
        The `st_makepoint` function returns a formatted string representing a point with the given
        longitude and latitude coordinates.

        :param longitude: Longitude is a geographic coordinate that specifies the east-west position of
        a point on the Earth's surface. It is measured in degrees, with values ranging from -180 degrees
        (west) to +180 degrees (east)
        :param latitude: Latitude is a geographic coordinate that specifies the north-south position of
        a point on the Earth's surface. It is measured in degrees, with values ranging from -90 degrees
        (South Pole) to +90 degrees (North Pole)
        :return: The function `st_makepoint` returns a string formatted as "ST_MakePoint(longitude,
        latitude)" with the provided longitude and latitude values inserted into the string.
        """
        return f"ST_MakePoint({longitude}, {latitude})"

    def st_makeline(self, points):
        """
        The function `st_makeline` creates a line geometry using the given points in a PostgreSQL
        database.

        :param points: The `st_makeline` function you provided seems to be a SQL function that creates a
        LineString geometry from an array of points. The `points` parameter should be an array of
        coordinate pairs representing the points that make up the line
        :return: The function `st_makeline` is returning a string that represents a PostGIS function
        call to create a line geometry using an array of points. The array of points is joined together
        using commas and then inserted into the `ST_MakeLine` function call.
        """
        return f"ST_MakeLine(ARRAY[{', '.join(points)}])"

    def st_makepolygon(self, points):
        """
        The function `st_makepolygon` creates a polygon geometry using a list of points.

        :param points: The `points` parameter in the `st_makepolygon` function represents a list of
        coordinates that define the vertices of the polygon you want to create. Each point in the list
        should be a tuple containing the x and y coordinates of the vertex. For example, `[(0, 0), (
        :return: The function `st_makepolygon` is returning a string that represents a PostGIS function
        call to create a polygon using the provided points. The `st_makeline` function is also being
        called within the `st_makepolygon` function to create the boundary of the polygon.
        """
        return f"ST_MakePolygon({self.st_makeline(points)})"

    def st_setsrid(self, geom, srid):
        """
        The function `st_setsrid` sets the spatial reference identifier (SRID) of a geometry object in
        Python using the PostGIS function `ST_SetSRID`.

        :param geom: The `geom` parameter in the `st_setsrid` function is typically a geometry object
        that you want to update with a new SRID (Spatial Reference Identifier). This function is
        commonly used in spatial databases like PostGIS to set or update the SRID of a geometry object
        :param srid: The `srid` parameter in the `ST_SetSRID` function is used to specify the Spatial
        Reference Identifier (SRID) for the geometry object. The SRID is a unique identifier that
        defines the spatial reference system (coordinate system and projection) in which the geometry is
        defined. It helps
        :return: The function `st_setsrid` is returning a string that represents the SQL function
        `ST_SetSRID` with the provided `geom` and `srid` values. The returned string is in the format:
        `ST_SetSRID(geom, srid)`.
        """
        return f"ST_SetSRID({geom}, {srid})"

    def st_transform(self, geom, srid):
        """
        The `st_transform` function transforms a geometry object to a different spatial reference system
        using the specified SRID.

        :param geom: The `geom` parameter in the `st_transform` function is typically a geometry object
        representing a spatial feature, such as a point, line, or polygon. It could be in a specific
        spatial reference system (SRS) that you want to transform to a different SRS specified by the `s
        :param srid: The SRID (Spatial Reference System Identifier) is a unique identifier that is used
        to specify the coordinate system and spatial reference information for geographic data. It helps
        to define the spatial properties of the data, such as the projection, datum, and units of
        measurement
        :return: The function `st_transform` is returning a string that represents the PostGIS function
        `ST_Transform` with the provided `geom` and `srid` parameters.
        """
        return f"ST_Transform({geom}, {srid})"

    def create_point(self, coordinate, srid):
        """
        The function creates a point with the given coordinates and spatial reference identifier (SRID)
        in Python.

        :param coordinate: The `coordinate` parameter is a tuple containing the latitude and longitude
        values of a point. For example, `coordinate = (40.7128, -74.0060)` represents the coordinates of
        New York City
        :param srid: The SRID (Spatial Reference System Identifier) is a unique identifier that
        represents a specific spatial reference system. It defines the coordinate system and projection
        used in spatial data. When creating a point geometry, specifying the SRID helps ensure that the
        point is correctly located in geographic space
        :return: The function `create_point` returns a point with the specified coordinates and spatial
        reference identifier (SRID).
        """
        point = self.st_makepoint(coordinate[0], coordinate[1])
        return self.st_setsrid(point, srid)

    def create_line(self, coordinates, srid):
        """
        The function creates a line geometry from a list of coordinates and assigns a spatial reference
        system identifier (SRID) to it.

        :param coordinates: Coordinates is a list of tuples representing the points that make up the
        line. Each tuple should contain the latitude and longitude values of a point. For example,
        coordinates = [(lat1, lon1), (lat2, lon2), (lat3, lon3)]
        :param srid: The SRID (Spatial Reference System Identifier) is a unique identifier that defines
        the spatial reference system for the geometry data. It specifies the coordinate system and
        projection used to represent the spatial data
        :return: The function `create_line` takes in a list of coordinates and a spatial reference ID
        (srid), creates a line geometry using the coordinates, and sets the spatial reference ID for the
        line. The function returns the line geometry with the specified spatial reference ID.
        """
        points = [self.st_makepoint(*coord) for coord in coordinates]
        line = self.st_makeline(points)
        return self.st_setsrid(line, srid)

    def create_polygon(self, coordinates, srid):
        """
        The function creates a polygon geometry from a list of coordinates and assigns a spatial
        reference system identifier (SRID) to it.

        :param coordinates: Coordinates is a list of lists where each inner list represents a coordinate
        pair (x, y) of a point in the polygon. The first and last coordinates should be the same to
        close the polygon. The `srid` parameter is the Spatial Reference System Identifier, which
        defines the coordinate system and projection
        :param srid: The SRID (Spatial Reference System Identifier) is a unique value that identifies a
        specific coordinate system or projection in which geometric data is represented. It is typically
        a number that corresponds to a specific spatial reference system
        :return: The function `create_polygon` returns a polygon geometry with the specified coordinates
        and spatial reference identifier (SRID). The polygon is created by connecting the points in the
        `coordinates` list to form a closed shape. The function then sets the SRID for the polygon
        before returning it.
        """
        first_coord = coordinates[0][0]
        last_coord = coordinates[0][-1]

        # Check if the first and last coordinates are not the same
        # if not, add the first coordinate to the end of the list
        # to close the polygon
        if first_coord != last_coord:
            coordinates[0].append(first_coord)

        points = [self.st_makepoint(*coord) for coord in coordinates[0]]
        polygon = self.st_makepolygon(points)
        return self.st_setsrid(polygon, srid)

    def validate_coordinates_for_point(self, coordinates):
        """
        The function `validate_coordinates_for_point` checks if a set of coordinates represents a valid
        point on Earth's surface.

        :param coordinates: The `validate_coordinates_for_point` method is used to validate a set of
        coordinates for a point. The method checks if the coordinates have exactly 2 elements, and if
        each element is of type `int` or `float`. It also ensures that the first element (longitude) is
        between -180
        """
        if len(coordinates) != 2 or not all(isinstance(coord, int | float) for coord in coordinates):
            raise ValueError("Point coordinates should have 2 elements of type int or float.")
        if not -180 <= coordinates[0] <= 180 or not -90 <= coordinates[1] <= 90:
            raise ValueError("Longitude should be between -180 and 180, latitude should be between -90 and 90.")

    def validate_coordinates_for_line_or_polygon(self, coordinates, is_polygon=False):
        """
        The function `validate_coordinates_for_line_or_polygon` checks if the provided coordinates are
        valid for a line or polygon based on certain criteria.

        :param coordinates: The `coordinates` parameter is expected to be a list of tuples or lists,
        where each tuple or list contains two elements representing longitude and latitude values. The
        function validates these coordinates based on certain criteria depending on whether it is for a
        line or a polygon
        :param is_polygon: The `is_polygon` parameter is a boolean flag that indicates whether the
        coordinates provided are for a polygon (True) or a line (False). This parameter helps
        differentiate between validating coordinates for a line or a polygon based on the requirements
        specified in the function, defaults to False (optional)
        """
        if not all(isinstance(coord, tuple | list) and len(coord) == 2 for coord in coordinates):
            raise ValueError("Line/Polygon coordinates should be tuples/lists with 2 elements of type int or float.")
        if not all(isinstance(coord[0], int | float) and isinstance(coord[1], int | float) for coord in coordinates):
            raise ValueError("Line/Polygon longitude and latitude should be of type int or float.")
        if not all(-180 <= coord[0] <= 180 and -90 <= coord[1] <= 90 for coord in coordinates):
            raise ValueError("Longitude should be between -180 and 180, latitude should be between -90 and 90.")
        if not is_polygon and len(coordinates) < 2:
            raise ValueError("Line coordinates should have at least 2 points.")
        if is_polygon and (len(coordinates) < 4 or coordinates[0] != coordinates[-1]):
            raise ValueError(
                "Polygon coordinates should have at least 4 points and start and end points must be the same."
            )

    def clean_and_validate(self, **kwargs):
        """
        The function `clean_and_validate` in Python validates and cleans keyword arguments for spatial
        operations.
        """
        if not kwargs:
            raise ValueError("No keyword arguments provided.")

        operation = kwargs.get("operation")
        coordinates = kwargs.get("coordinates", [])
        distance = kwargs.get("distance")
        layer_type = kwargs.get("layer_type")

        if operation and operation not in self.POSTGIS_SPATIAL_RELATION:
            raise ValueError(f"Invalid operation: {operation}")

        if layer_type and layer_type not in self.ALLOWED_LAYER_TYPE.values():
            raise ValueError(f"Invalid layer type: {layer_type}")

        if not isinstance(coordinates, list | tuple):
            raise TypeError(f"Invalid coordinates: {coordinates}")

        if distance is not None and not isinstance(distance, int | float):
            raise TypeError(f"Invalid distance: {distance}")

        if layer_type == "point":
            self.validate_coordinates_for_point(coordinates)
        elif layer_type in ["line", "polygon"]:
            coord = coordinates if layer_type == "line" else coordinates[0]
            self.validate_coordinates_for_line_or_polygon(coord, is_polygon=(layer_type == "polygon"))

    def get_postgis_query(
        self,
        operation: str,
        coordinates: list[list[int | float] | tuple[int | float]] | tuple[list[int | float] | tuple[int | float]],
        distance=None,
        layer_type="point",
    ):
        """
        This Python function generates a PostGIS query based on the specified operation, coordinates,
        distance, and layer type.

        :param operation: The `operation` parameter in the `get_postgis_query` method is a string that
        specifies the spatial operation to be performed in the PostGIS query. It could be values like
        "intersects", "contains", "within", "touches", etc., which define the spatial relationship
        between geometries
        :type operation: str
        :param coordinates: Coordinates are the points or shapes on the map that you want to perform
        spatial operations on. The `coordinates` parameter in the `get_postgis_query` function is a list
        of lists or tuples containing integer or float values representing the coordinates of the points
        or shapes. The format of the coordinates depends on
        :type coordinates: list[list[int | float] | tuple[int | float]] | tuple[list[int | float] |
        tuple[int | float]]
        :param distance: The `distance` parameter in the `get_postgis_query` function is used to specify
        the distance for spatial operations involving a buffer. If a distance is provided, the function
        will create a buffer around the specified geometry based on that distance before performing the
        spatial operation
        :param layer_type: The `layer_type` parameter in the `get_postgis_query` method specifies the
        type of spatial layer being used in the PostGIS query. It can have one of the following values:,
        defaults to point (optional)
        :return: The `get_postgis_query` method returns a PostGIS spatial query based on the provided
        operation, coordinates, distance, and layer type. The returned query is constructed using the
        PostGIS spatial relation specified by the `operation` parameter, the geometry created based on
        the `coordinates` and `layer_type`, and the field name associated with the instance.
        """
        self.clean_and_validate(operation=operation, coordinates=coordinates, distance=distance, layer_type=layer_type)

        geom_functions = {
            "point": self.create_point,
            "line": self.create_line,
            "polygon": self.create_polygon,
        }

        geom = geom_functions[layer_type](coordinates, self.field.srid)

        if distance:
            left = geom
            right = self.field.name

            # Need to transform srid to 3857 for distance calculation
            if self.field.srid == 4326:
                left = self.st_transform(geom, 3857)
                right = self.st_transform(self.field.name, 3857)

            return f"{self.POSTGIS_SPATIAL_RELATION[operation]}(ST_Buffer({left}, {distance}), {right})"
        else:
            return f"{self.POSTGIS_SPATIAL_RELATION[operation]}({geom}, {self.field.name})"

    def validate_and_extract_value(self, value):
        """
        The function `validate_and_extract_value` checks if the input value is of the specified types
        and extracts a distance value if present in a list or tuple.

        :param value: The `validate_and_extract_value` method is designed to validate the input `value`
        and extract a distance value if it is provided as part of a list or tuple. The method checks if
        the `value` is of type string, dictionary, list, tuple, or a `BaseGeometry` object
        :return: The function `validate_and_extract_value` returns two values: `value` and `distance`.
        If the input `value` is a list or tuple with 2 elements, it unpacks the elements and returns
        them as `value` and `distance`. Otherwise, it returns the original `value` and `None` for
        `distance`.
        """
        if not isinstance(value, str | dict | list | tuple | BaseGeometry):
            raise ValueError(
                "Value should be a geojson, WKT, a list or tuple with 2 elements, " "or a shapely geometry."
            )

        distance = None
        if isinstance(value, list | tuple):
            if len(value) != 2 or not isinstance(value[1], int | float) or value[1] <= 0:
                raise ValueError(
                    "Value should be a list or tuple with 2 elements: a geojson/WKT/shapely geometry "
                    "and a positive distance."
                )
            value, distance = value  # Unpack the tuple/list

        return value, distance

    def parse_geometry(self, value):
        """
        The function `parse_geometry` attempts to parse a given value as GeoJSON, WKT, or a Shapely
        geometry and returns the corresponding representation.

        :param value: The `parse_geometry` method is designed to parse different types of geometry
        representations. The method first checks if the input `value` is a string, dictionary, or a
        Shapely geometry object, and then attempts to parse it accordingly
        :return: The `parse_geometry` method is designed to parse a given value into a GeoJSON format.
        Depending on the type of the input value, it will attempt to parse it as GeoJSON, WKT, or a
        Shapely geometry. Here is what is being returned based on the type of the input value:
        """
        if isinstance(value, str):
            try:
                return json.loads(value)  # Attempt to parse as GeoJSON
            except json.JSONDecodeError:
                try:
                    return mapping(wkt.loads(value))  # Attempt to parse as WKT
                except Exception as e:
                    raise ValueError("Invalid value: should be a geojson, WKT, or a shapely geometry.") from e
        elif isinstance(value, dict):
            return value  # Already in GeoJSON format
        elif isinstance(value, BaseGeometry):
            return mapping(value)  # Convert Shapely Geometry to GeoJSON
        else:
            raise ValueError("Invalid value type.")

    def validate_geojson(self, geojson):
        """
        The function `validate_geojson` checks if a given GeoJSON object has a valid type and structure.

        :param geojson: The `validate_geojson` method is used to validate a GeoJSON object. The method
        checks if the GeoJSON object has a valid type (Point, LineString, or Polygon) and then attempts
        to validate the structure of the GeoJSON using the `shape` function
        """
        if geojson.get("type") not in self.ALLOWED_LAYER_TYPE:
            raise ValueError("Invalid geojson type. Allowed types are Point, LineString, and Polygon.")
        try:
            shape(geojson)
        except Exception as e:
            raise ValueError("Invalid geojson.") from e

    def domain_query(self, operator, value):
        """
        The `domain_query` function validates and extracts a value, parses a geometry, validates the
        geometry, checks the operator, and then generates a PostGIS query based on the input parameters.

        :param operator: The `operator` parameter in the `domain_query` method is used to specify the
        type of operation to be performed on the given value. It is checked against a dictionary
        `OPERATION_TO_RELATION` to determine the corresponding operation to be executed
        :param value: The `value` parameter in the `domain_query` method is the input value that you
        want to query against a specific domain. This value will be validated, extracted, and parsed as
        a geometry object (geojson_val) before being used in the query operation. The `distance`
        variable is also
        :return: The code snippet is returning an SQL query generated based on the input parameters
        provided to the `domain_query` method. The SQL query is constructed using the
        `get_postgis_query` method from the class, passing in the operation, coordinates, distance, and
        layer type extracted from the input values.
        """

        val, distance = self.validate_and_extract_value(value)
        geojson_val = self.parse_geometry(val)
        self.validate_geojson(geojson_val)

        if operator not in self.OPERATION_TO_RELATION:
            raise ValueError("Invalid operator.")

        operation = self.OPERATION_TO_RELATION[operator]
        layer_type = self.ALLOWED_LAYER_TYPE[geojson_val["type"]]
        coordinates = geojson_val["coordinates"]

        return SQL(self.get_postgis_query(operation, coordinates, distance=distance, layer_type=layer_type))
