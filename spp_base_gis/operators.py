class Operator:
    POSTGIS_SPATIAL_RELATION = {
        "intersects": "ST_Intersects",
        "within": "ST_Within",
        "contains": "ST_Contains",
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

    def get_postgis_query(self, operation, longitude, latitude, distance=None):
        """
        The function `get_postgis_query` generates a PostGIS spatial query based on the operation,
        longitude, latitude, and optional distance provided.

        :param operation: The `operation` parameter in the `get_postgis_query` method represents the
        spatial operation to be performed in the PostGIS query. It determines how the spatial
        relationship between geometries will be evaluated. Examples of spatial operations include
        `ST_Intersects`, `ST_Contains`, `ST_Distance`,
        :param longitude: The `longitude` parameter in the `get_postgis_query` method represents the
        longitude coordinate of a point on the Earth's surface. It is used to create a spatial point in
        PostGIS for performing spatial operations like distance calculations or spatial relations
        :param latitude: Latitude is a geographic coordinate that specifies the north-south position of
        a point on the Earth's surface. It is measured in degrees ranging from -90 (South Pole) to 90
        (North Pole)
        :param distance: The `distance` parameter in the `get_postgis_query` method is used to specify
        the distance for a spatial operation. If a distance is provided, the method will calculate the
        spatial relation based on the distance from a given point. If no distance is provided, the
        method will calculate the spatial relation
        :return: The `get_postgis_query` method returns a PostGIS spatial query based on the provided
        operation, longitude, latitude, and optional distance. If a distance is provided, it calculates
        the spatial relation using a buffered area around the point within the specified distance. If no
        distance is provided, it calculates the spatial relation between the point and the field
        directly.
        """
        point = self.create_point(longitude, latitude, self.field.srid)

        if distance:
            left = point
            right = self.field.name

            # Need to transform srid to 3857 for distance calculation
            if self.field.srid == 4326:
                left = "ST_Transform(%s, 3857)" % point
                right = "ST_Transform(%s, 3857)" % self.field.name

            return f"{self.POSTGIS_SPATIAL_RELATION[operation]}(ST_Buffer({left}, {distance}), {right})"
        else:
            return f"{self.POSTGIS_SPATIAL_RELATION[operation]}({point}, {self.field.name})"
