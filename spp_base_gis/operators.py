class Operator:
    """
    The Operator class facilitates the creation and manipulation of spatial geometries and queries within a PostgreSQL
    database using the PostGIS extension. It offers methods for constructing geometries (points, lines, polygons),
    setting and transforming spatial reference identifiers (SRIDs), and generating spatial queries based on specified
    operations and geometries.

    Attributes:
        field (Field): An object representing the field associated with spatial data, containing SRID information.
        POSTGIS_SPATIAL_RELATION (dict): Maps spatial operation names to their corresponding PostGIS function names.

    Methods:
        __init__(self, field): Initializes a new instance of the Operator class with the specified field.
        st_makepoint(self, longitude, latitude): Returns a string for a PostGIS call to create a point from
                                                  longitude and latitude.
        st_makeline(self, points): Returns a string for a PostGIS call to create a line geometry from an array of
                                   points.
        st_makepolygon(self, points): Returns a string for a PostGIS call to create a polygon geometry from a list
                                      of points.
        st_setsrid(self, geom, srid): Returns a string for a PostGIS call to set the SRID for a geometry object.
        st_transform(self, geom, srid): Returns a string for a PostGIS call to transform a geometry object to a
                                        different spatial reference system.
        create_point(self, coordinate, srid): Creates a point geometry with given coordinates and SRID.
        create_line(self, coordinates, srid): Creates a line geometry from coordinates and assigns the specified SRID.
        create_polygon(self, coordinates, srid): Creates a polygon geometry from coordinates and assigns the specified
                                                 SRID.
        clean_and_validate(self, **kwargs): Validates provided keyword arguments for spatial operations, coordinates,
                                             distance, and layer types.
        get_postgis_query(self, operation, coordinates, distance=None, layer_type="point"): Generates and returns a
                                      PostGIS spatial query based on specified operation, coordinates, distance, and
                                      layer type.
    """

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

        :param coordinate: The `coordinate` parameter is a list containing a pair of coordinates in the
        form of (x, y). The function `create_point` takes the first pair of coordinates from the
        `coordinate` list and creates a point using those coordinates
        :param srid: The SRID (Spatial Reference System Identifier) is a unique value that identifies a
        specific spatial reference system. It is commonly used in GIS (Geographic Information Systems)
        to define the coordinate system and spatial properties of geographic data. Examples of SRID
        values include 4326 for WGS 84 and
        :return: a point with the specified coordinates and spatial reference identifier (SRID).
        """
        point = self.st_makepoint(coordinate[0][0], coordinate[0][1])
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
        The function creates a polygon from a list of coordinates and assigns a spatial reference system
        identifier (SRID) to it.

        :param coordinates: Coordinates is a list of tuples representing the vertices of the polygon.
        Each tuple contains the latitude and longitude values of a point on the polygon's boundary
        :param srid: SRID stands for Spatial Reference System Identifier. It is a unique identifier that
        defines the spatial reference system used by the geometry data. It specifies the coordinate
        system and projection information for spatial data
        :return: The function `create_polygon` returns a polygon geometry with the specified coordinates
        and spatial reference identifier (SRID). The polygon is created by connecting the given
        coordinates in the order they are provided, and if the first and last coordinates are not the
        same, the function adds the first coordinate to the end of the list to close the polygon. The
        resulting polygon geometry is then assigned the specified SRID before being
        """
        first_coord = coordinates[0]
        last_coord = coordinates[-1]

        # Check if the first and last coordinates are not the same
        # if not, add the first coordinate to the end of the list
        # to close the polygon
        if first_coord != last_coord:
            coordinates.append(first_coord)

        points = [self.st_makepoint(*coord) for coord in coordinates]
        polygon = self.st_makepolygon(points)
        return self.st_setsrid(polygon, srid)

    def clean_and_validate(self, **kwargs):
        """
        The function `clean_and_validate` in Python validates keyword arguments for spatial operations,
        coordinates, distance, and layer types, with specific checks for each parameter.
        """

        if not kwargs:
            raise ValueError("No keyword arguments provided.")

        operation = kwargs.get("operation")
        coordinates = kwargs.get("coordinates", [])
        distance = kwargs.get("distance")
        layer_type = kwargs.get("layer_type")

        # validating operation
        if operation and operation not in self.POSTGIS_SPATIAL_RELATION:
            raise ValueError(f"Invalid operation: {operation}")

        # validating coordinates
        if coordinates and not isinstance(coordinates, list | tuple):
            raise TypeError(f"Invalid coordinates: {coordinates}")
        for coordinate in coordinates:
            if not isinstance(coordinate, list | tuple):
                raise TypeError(f"Invalid coordinate: {coordinate}")
            if not all(isinstance(coord, int | float) for coord in coordinate):
                raise TypeError(f"Invalid coordinate: {', '.join(str(c) for c in coordinate)}")
            if len(coordinate) != 2:
                raise ValueError(f"Invalid coordinate: {', '.join(str(c) for c in coordinate)}")
            if not -180 <= coordinate[0] <= 180 or not -90 <= coordinate[1] <= 90:
                raise ValueError(f"Invalid coordinate: {', '.join(str(c) for c in coordinate)}")

        # validating layer_type
        if layer_type and layer_type not in ["point", "line", "polygon"]:
            raise ValueError(f"Invalid layer type: {layer_type}")
        if len(coordinates) == 1 and layer_type != "point" or len(coordinates) > 1 and layer_type == "point":
            raise ValueError(f"Invalid coordinates for {layer_type}: {coordinates}")

        # validating distance
        if distance and not isinstance(distance, int | float):
            raise TypeError(f"Invalid distance: {distance}")

        if coordinates and layer_type == "polygon":
            first_coord = coordinates[0]
            last_coord = coordinates[-1]

            # Check if the first and last coordinates are not the same
            # if not, add the first coordinate to the end of the list
            # to close the polygon
            if first_coord != last_coord:
                coordinates.append(first_coord)

            if len(coordinates) < 4:
                raise ValueError(f"Invalid coordinates for polygon: {coordinates}")

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
