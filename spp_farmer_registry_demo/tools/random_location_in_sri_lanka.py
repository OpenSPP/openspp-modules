import json
import random

from shapely.geometry import Point, shape
from shapely.prepared import prep

from odoo.tools.misc import file_open

# Load Sri Lanka country border data in GeoJSON format
with file_open("spp_farmer_registry_demo/tools/geoBoundaries-LKA-ADM0_simplified.geojson", "r") as f:
    sri_lanka_geojson = json.load(f)

# Create a shape object from the GeoJSON data
sri_lanka_shape = shape(sri_lanka_geojson["features"][0]["geometry"])

# Prepare the shape for faster spatial operations
prepared_sri_lanka_shape = prep(sri_lanka_shape)


def random_location_in_sri_lanka():
    min_lat, max_lat = 5.9194, 9.8351
    min_lon, max_lon = 79.6521, 81.8790

    while True:
        # Generate random latitude and longitude within the bounding box
        latitude = random.uniform(min_lat, max_lat)
        longitude = random.uniform(min_lon, max_lon)
        random_point = Point(longitude, latitude)

        # Check if the generated point is within the Sri Lanka boundary
        if prepared_sri_lanka_shape.contains(random_point):
            return (latitude, longitude)
