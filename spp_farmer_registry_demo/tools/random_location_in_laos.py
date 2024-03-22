import json
import random

from shapely.geometry import Point, shape
from shapely.prepared import prep

from odoo.tools.misc import file_open

# Load Laos country border data in GeoJSON format
with file_open("spp_farmer_registry_demo/tools/laos_features.json", "r") as f:
    laos_geojson = json.load(f)

# Create a shape object from the GeoJSON data
laos_shape = shape(laos_geojson["features"][0]["geometry"])

# Prepare the shape for faster spatial operations
prepared_laos_shape = prep(laos_shape)


def random_location_in_laos():
    min_lat, max_lat = 13.9095, 22.5085
    min_lon, max_lon = 100.0843, 107.6346

    while True:
        # Generate random latitude and longitude within the bounding box
        latitude = random.uniform(min_lat, max_lat)
        longitude = random.uniform(min_lon, max_lon)
        random_point = Point(longitude, latitude)

        # Check if the generated point is within the Laos boundary
        if prepared_laos_shape.contains(random_point):
            return (latitude, longitude)
