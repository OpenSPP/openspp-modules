import random


def random_location_in_kenya():
    # Conservative boundaries for Kenya
    min_lat, max_lat = -1.900, 2.6766
    min_lon, max_lon = 36.2509, 40.651

    # Generate random latitude and longitude within these boundaries
    latitude = random.uniform(min_lat, max_lat)
    longitude = random.uniform(min_lon, max_lon)

    return latitude, longitude


# Example usage
# latitude, longitude = random_location_in_kenya()
# print(latitude, longitude)
