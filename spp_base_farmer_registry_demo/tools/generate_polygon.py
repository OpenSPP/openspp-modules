import math
import random


def acres_to_square_degrees(acres, latitude):
    # Earth's radius in kilometers
    earth_radius = 6371.0

    # Convert acres to square kilometers
    area_km2 = acres * 0.00404686

    # Calculate the area in square degrees using an approximation
    # Assumes the Earth is a perfect sphere
    area_deg2 = area_km2 / (math.pi / 180) ** 2 / earth_radius**2

    # Adjust for the latitude (degrees of longitude get smaller further from the equator)
    area_deg2 /= math.cos(math.radians(latitude))

    return area_deg2


def generate_polygon(lat, lon, acres):
    # Convert the area from acres to approximate square degrees
    area_deg2 = acres_to_square_degrees(acres, lat)

    # Assuming a hexagon, calculate the radius needed for the given area
    # Area of a hexagon: (3 * sqrt(3) / 2) * side^2
    side_length = math.sqrt((2 * area_deg2) / (3 * math.sqrt(3)))

    # Generate points for the hexagon
    points = []
    num_points = random.randint(3, 7)
    for i in range(num_points):
        angle_deg = 360 * i / num_points
        angle_rad = math.radians(angle_deg)
        dx = side_length * math.cos(angle_rad)
        dy = side_length * math.sin(angle_rad)

        # Adjust dx for the latitude (degrees of longitude get smaller further from the equator)
        dx /= math.cos(math.radians(lat))

        points.append((lon + dx, lat + dy))

    # Repeat the first point at the end to close the polygon
    points.append(points[0])

    return points

    # polygon_wkt = "MULTIPOLYGON((({})))".format(", ".join(["{} {}".format(lon, lat) for lon, lat in points]))


# Example usage
# print(generate_polygon(latitude, longitude, random.randrange(50, 500)))  #
