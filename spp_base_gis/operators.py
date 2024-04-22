class Operator:
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

    def create_point(self, longitude, latitude, srid):
        """
        The function creates a point with specified longitude, latitude, and spatial reference
        identifier (SRID) in a PostgreSQL database.

        :param longitude: Longitude is the angular distance of a point east or west of the prime
        meridian. It is measured in degrees, ranging from -180 degrees (west) to +180 degrees (east)
        :param latitude: The latitude parameter represents the north-south position of a point on the
        Earth's surface, measured in degrees from the equator. It ranges from -90 degrees (South Pole)
        to +90 degrees (North Pole), with 0 degrees at the equator
        :param srid: The SRID (Spatial Reference System Identifier) is a unique value that identifies
        the coordinate system and spatial reference information used by the geometry data. It is
        typically a number that corresponds to a specific coordinate system, such as EPSG codes
        :return: The function `create_point` returns a SQL query string that creates a point geometry
        with the specified longitude, latitude, and SRID (Spatial Reference Identifier) using PostGIS
        functions.
        """
        return f"ST_SetSRID(ST_MakePoint({longitude}, {latitude}), {srid})"

    def st_transform(self, geom, srid):
        return f"ST_Transform({geom}, {srid})"

    def validate(self, **kwargs):
        """
        The function `validate` checks the validity of keyword arguments related to spatial operations.
        """
        if not kwargs:
            raise ValueError("No keyword arguments provided.")
        operation = kwargs.get("operation")
        longitude = kwargs.get("longitude")
        latitude = kwargs.get("latitude")
        distance = kwargs.get("distance")

        if operation and operation not in self.POSTGIS_SPATIAL_RELATION:
            raise ValueError(f"Invalid operation: {operation}")
        if longitude and not isinstance(longitude, int | float):
            raise TypeError(f"Invalid longitude: {longitude}")
        if latitude and not isinstance(latitude, int | float):
            raise TypeError(f"Invalid latitude: {latitude}")
        if distance and not isinstance(distance, int | float):
            raise TypeError(f"Invalid distance: {distance}")

    def get_postgis_query(self, operation, longitude, latitude, distance=None):
        """
        The function `get_postgis_query` generates a PostGIS spatial query based on the specified
        operation, longitude, latitude, and optional distance.

        :param operation: The `operation` parameter in the `get_postgis_query` method represents the
        spatial operation to be performed in the PostGIS query. It could be one of the following spatial
        operations: 'intersects', 'contains', 'within', 'touches', 'overlaps', 'crosses', 'equals
        :param longitude: Longitude is a numerical value that represents the east-west position of a
        point on the Earth's surface. It is measured in degrees and ranges from -180 degrees (west) to
        +180 degrees (east)
        :param latitude: Latitude is a geographic coordinate that specifies the north-south position of
        a point on the Earth's surface. It is measured in degrees ranging from -90 (South Pole) to 90
        (North Pole)
        :param distance: The `distance` parameter in the `get_postgis_query` method is used to specify
        the distance within which the spatial operation should be performed. If a value is provided for
        `distance`, the method will create a buffer around the specified point within that distance and
        perform the spatial operation accordingly. If no
        :return: The `get_postgis_query` method returns a PostGIS spatial query based on the provided
        operation, longitude, latitude, and optional distance. If a distance is provided, it calculates
        the spatial relation using a buffered area around the point within the specified distance. If no
        distance is provided, it calculates the spatial relation directly between the point and the
        field name.
        """
        self.validate(operation=operation, longitude=longitude, latitude=latitude, distance=distance)

        point = self.create_point(longitude, latitude, self.field.srid)

        if distance:
            left = point
            right = self.field.name

            # Need to transform srid to 3857 for distance calculation
            if self.field.srid == 4326:
                left = self.st_transform(point, 3857)
                right = self.st_transform(self.field.name, 3857)

            return f"{self.POSTGIS_SPATIAL_RELATION[operation]}(ST_Buffer({left}, {distance}), {right})"
        else:
            return f"{self.POSTGIS_SPATIAL_RELATION[operation]}({point}, {self.field.name})"
