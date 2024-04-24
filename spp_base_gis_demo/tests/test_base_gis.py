from shapely.geometry import Point, Polygon, mapping, shape

from odoo.exceptions import UserError

from .common import Common


class BaseGISTest(Common):
    def test_gis_locational_query_intersects(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1, latitude=self.latitude_1
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2, latitude=self.latitude_2
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3, latitude=self.latitude_3
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 1)
        self.assertEqual(feature_collection_1["features"][0]["properties"]["name"], self.test_record_1.name)

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 1)
        self.assertEqual(feature_collection_2["features"][0]["properties"]["name"], self.test_record_2.name)

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 0)

    def test_gis_locational_query_intersects_with_distance(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1, latitude=self.latitude_1, distance=1000
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2, latitude=self.latitude_2, distance=1000
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3, latitude=self.latitude_3, distance=1000
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 1)
        self.assertEqual(feature_collection_1["features"][0]["properties"]["name"], self.test_record_1.name)

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 1)
        self.assertEqual(feature_collection_2["features"][0]["properties"]["name"], self.test_record_2.name)

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 0)

    def test_gis_locational_query_within(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1, latitude=self.latitude_1, spatial_relation="within"
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2, latitude=self.latitude_2, spatial_relation="within"
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3, latitude=self.latitude_3, spatial_relation="within"
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 1)
        self.assertEqual(feature_collection_1["features"][0]["properties"]["name"], self.test_record_1.name)

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 1)
        self.assertEqual(feature_collection_2["features"][0]["properties"]["name"], self.test_record_2.name)

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 0)

    def test_gis_locational_query_within_with_distance(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1, latitude=self.latitude_1, spatial_relation="within", distance=1000
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2, latitude=self.latitude_2, spatial_relation="within", distance=1000
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3, latitude=self.latitude_3, spatial_relation="within", distance=1000
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 0)

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 1)
        self.assertEqual(feature_collection_2["features"][0]["properties"]["name"], self.test_record_2.name)

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 0)

    def test_gis_locational_query_contains(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1, latitude=self.latitude_1, spatial_relation="contains"
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2, latitude=self.latitude_2, spatial_relation="contains"
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3, latitude=self.latitude_3, spatial_relation="contains"
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 0)

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 0)

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 0)

    def test_gis_locational_query_contains_with_distance(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1, latitude=self.latitude_1, spatial_relation="contains", distance=10000
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2, latitude=self.latitude_2, spatial_relation="contains", distance=10000
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3, latitude=self.latitude_3, spatial_relation="contains", distance=1000
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 1)
        self.assertEqual(feature_collection_1["features"][0]["properties"]["name"], self.test_record_1.name)

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 1)
        self.assertEqual(feature_collection_2["features"][0]["properties"]["name"], self.test_record_2.name)

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 0)

    def test_gis_locational_query_covers(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1, latitude=self.latitude_1, spatial_relation="covers"
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2, latitude=self.latitude_2, spatial_relation="covers"
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3, latitude=self.latitude_3, spatial_relation="covers"
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 0)

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 0)

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 0)

    def test_gis_locational_query_covers_with_distance(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1, latitude=self.latitude_1, spatial_relation="covers", distance=10000
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2, latitude=self.latitude_2, spatial_relation="covers", distance=10000
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3, latitude=self.latitude_3, spatial_relation="covers", distance=1000
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 1)
        self.assertEqual(feature_collection_1["features"][0]["properties"]["name"], self.test_record_1.name)

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 1)
        self.assertEqual(feature_collection_2["features"][0]["properties"]["name"], self.test_record_2.name)

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 0)

    def test_gis_locational_query_equals(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1, latitude=self.latitude_1, spatial_relation="equals"
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2, latitude=self.latitude_2, spatial_relation="equals"
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3, latitude=self.latitude_3, spatial_relation="equals"
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 0)

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 0)

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 0)

    def test_gis_locational_query_equals_with_distance(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1, latitude=self.latitude_1, spatial_relation="equals", distance=10000
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2, latitude=self.latitude_2, spatial_relation="equals", distance=10000
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3, latitude=self.latitude_3, spatial_relation="equals", distance=1000
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 0)

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 0)

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 0)

    def test_gis_locational_query_coveredby(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1, latitude=self.latitude_1, spatial_relation="coveredby"
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2, latitude=self.latitude_2, spatial_relation="coveredby"
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3, latitude=self.latitude_3, spatial_relation="coveredby"
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 1)
        self.assertEqual(feature_collection_1["features"][0]["properties"]["name"], self.test_record_1.name)

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 1)
        self.assertEqual(feature_collection_2["features"][0]["properties"]["name"], self.test_record_2.name)

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 0)

    def test_gis_locational_query_coveredby_with_distance(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1, latitude=self.latitude_1, spatial_relation="coveredby", distance=1000
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2, latitude=self.latitude_2, spatial_relation="coveredby", distance=1000
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3, latitude=self.latitude_3, spatial_relation="coveredby", distance=1000
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 0)

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 1)
        self.assertEqual(feature_collection_2["features"][0]["properties"]["name"], self.test_record_2.name)

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 0)

    def test_gis_locational_query_disjoint(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1, latitude=self.latitude_1, spatial_relation="disjoint"
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2, latitude=self.latitude_2, spatial_relation="disjoint"
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3, latitude=self.latitude_3, spatial_relation="disjoint"
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 1)
        self.assertEqual(feature_collection_1["features"][0]["properties"]["name"], self.test_record_2.name)
        self.assertEqual(
            feature_collection_1["features"][0]["geometry"]["coordinates"],
            mapping(shape(self.geojson_polygon_2))["coordinates"],
        )
        self.assertEqual(feature_collection_1["features"][0]["geometry"]["type"], self.geojson_polygon_2["type"])
        self.assertEqual(feature_collection_1["features"][0]["type"], "Feature")

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 1)
        self.assertEqual(feature_collection_2["features"][0]["properties"]["name"], self.test_record_1.name)
        self.assertEqual(
            feature_collection_2["features"][0]["geometry"]["coordinates"],
            mapping(shape(self.geojson_polygon_1))["coordinates"],
        )
        self.assertEqual(feature_collection_2["features"][0]["geometry"]["type"], self.geojson_polygon_1["type"])
        self.assertEqual(feature_collection_2["features"][0]["type"], "Feature")

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 2)
        self.assertEqual(feature_collection_3["features"][0]["properties"]["name"], self.test_record_1.name)
        self.assertEqual(
            feature_collection_3["features"][0]["geometry"]["coordinates"],
            mapping(shape(self.geojson_polygon_1))["coordinates"],
        )
        self.assertEqual(feature_collection_3["features"][0]["geometry"]["type"], self.geojson_polygon_1["type"])
        self.assertEqual(feature_collection_3["features"][0]["type"], "Feature")
        self.assertEqual(feature_collection_3["features"][1]["properties"]["name"], self.test_record_2.name)
        self.assertEqual(
            feature_collection_3["features"][1]["geometry"]["coordinates"],
            mapping(shape(self.geojson_polygon_2))["coordinates"],
        )
        self.assertEqual(feature_collection_3["features"][1]["geometry"]["type"], self.geojson_polygon_2["type"])

    def test_gis_locational_query_disjoint_with_distance(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1,
            latitude=self.latitude_1,
            spatial_relation="disjoint",
            distance=1000,
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2,
            latitude=self.latitude_2,
            spatial_relation="disjoint",
            distance=1000,
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3,
            latitude=self.latitude_3,
            spatial_relation="disjoint",
            distance=1000,
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 1)
        self.assertEqual(feature_collection_1["features"][0]["properties"]["name"], self.test_record_2.name)
        self.assertEqual(
            feature_collection_1["features"][0]["geometry"]["coordinates"],
            mapping(shape(self.geojson_polygon_2))["coordinates"],
        )
        self.assertEqual(feature_collection_1["features"][0]["geometry"]["type"], self.geojson_polygon_2["type"])
        self.assertEqual(feature_collection_1["features"][0]["type"], "Feature")

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 1)
        self.assertEqual(feature_collection_2["features"][0]["properties"]["name"], self.test_record_1.name)
        self.assertEqual(
            feature_collection_2["features"][0]["geometry"]["coordinates"],
            mapping(shape(self.geojson_polygon_1))["coordinates"],
        )
        self.assertEqual(feature_collection_2["features"][0]["geometry"]["type"], self.geojson_polygon_1["type"])
        self.assertEqual(feature_collection_2["features"][0]["type"], "Feature")

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 2)
        self.assertEqual(feature_collection_3["features"][0]["properties"]["name"], self.test_record_1.name)
        self.assertEqual(
            feature_collection_3["features"][0]["geometry"]["coordinates"],
            mapping(shape(self.geojson_polygon_1))["coordinates"],
        )
        self.assertEqual(feature_collection_3["features"][0]["geometry"]["type"], self.geojson_polygon_1["type"])
        self.assertEqual(feature_collection_3["features"][0]["type"], "Feature")
        self.assertEqual(feature_collection_3["features"][1]["properties"]["name"], self.test_record_2.name)
        self.assertEqual(
            feature_collection_3["features"][1]["geometry"]["coordinates"],
            mapping(shape(self.geojson_polygon_2))["coordinates"],
        )
        self.assertEqual(feature_collection_3["features"][1]["geometry"]["type"], self.geojson_polygon_2["type"])

    def test_gis_locational_query_crosses(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1, latitude=self.latitude_1, spatial_relation="crosses"
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2, latitude=self.latitude_2, spatial_relation="crosses"
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3, latitude=self.latitude_3, spatial_relation="crosses"
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 0)

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 0)

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 0)

    def test_gis_locational_query_crosses_with_distance(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1,
            latitude=self.latitude_1,
            spatial_relation="crosses",
            distance=100000,
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2,
            latitude=self.latitude_2,
            spatial_relation="crosses",
            distance=100000,
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3,
            latitude=self.latitude_3,
            spatial_relation="crosses",
            distance=100000,
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 0)

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 0)

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 0)

    def test_gis_locational_query_touches(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1, latitude=self.latitude_1, spatial_relation="touches"
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2, latitude=self.latitude_2, spatial_relation="touches"
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3, latitude=self.latitude_3, spatial_relation="touches"
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 0)

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 0)

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 0)

    def test_gis_locational_query_touches_with_distance(self):
        feature_collection_1 = self.test_model.gis_locational_query(
            longitude=self.longitude_1,
            latitude=self.latitude_1,
            spatial_relation="touches",
            distance=1000,
        )
        feature_collection_2 = self.test_model.gis_locational_query(
            longitude=self.longitude_2,
            latitude=self.latitude_2,
            spatial_relation="touches",
            distance=1000,
        )
        feature_collection_3 = self.test_model.gis_locational_query(
            longitude=self.longitude_3,
            latitude=self.latitude_3,
            spatial_relation="touches",
            distance=1000,
        )

        self.assertEqual(feature_collection_1["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_1["features"]), 0)

        self.assertEqual(feature_collection_2["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_2["features"]), 0)

        self.assertEqual(feature_collection_3["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_3["features"]), 0)

    def test_gis_locational_query_errors(self):
        spatial_relation = "error"
        with self.assertRaisesRegex(UserError, f"Invalid spatial relation {spatial_relation}"):
            self.test_model.gis_locational_query(
                longitude=self.longitude_1, latitude=self.latitude_1, spatial_relation=spatial_relation
            )

        layer_type = "triangle"
        with self.assertRaisesRegex(UserError, f"Invalid layer type {layer_type}"):
            self.test_model.gis_locational_query(
                longitude=self.longitude_1, latitude=self.latitude_1, layer_type=layer_type
            )

        distance = -1
        with self.assertRaisesRegex(UserError, "Distance must be a positive number"):
            self.test_model.gis_locational_query(
                longitude=self.longitude_1, latitude=self.latitude_1, distance=distance
            )

        distance = "distance"
        with self.assertRaisesRegex(UserError, "Distance must be a number"):
            self.test_model.gis_locational_query(
                longitude=self.longitude_1, latitude=self.latitude_1, distance=distance
            )

        longitude, latitude = "zero", "one"
        with self.assertRaisesRegex(UserError, f"Invalid coordinates: latitude={latitude}, longitude={longitude}"):
            self.test_model.gis_locational_query(longitude=longitude, latitude=latitude)

        longitude, latitude = 80, 181
        with self.assertRaisesRegex(UserError, f"Invalid coordinates: latitude={latitude}, longitude={longitude}"):
            self.test_model.gis_locational_query(longitude=longitude, latitude=latitude)

        longitude, latitude = 80, -181
        with self.assertRaisesRegex(UserError, f"Invalid coordinates: latitude={latitude}, longitude={longitude}"):
            self.test_model.gis_locational_query(longitude=longitude, latitude=latitude)

        longitude, latitude = 91, 100
        with self.assertRaisesRegex(UserError, f"Invalid coordinates: latitude={latitude}, longitude={longitude}"):
            self.test_model.gis_locational_query(longitude=longitude, latitude=latitude)

        longitude, latitude = -91, 100
        with self.assertRaisesRegex(UserError, f"Invalid coordinates: latitude={latitude}, longitude={longitude}"):
            self.test_model.gis_locational_query(longitude=longitude, latitude=latitude)

    def test_get_gis_view(self):
        with self.assertRaisesRegex(
            UserError,
            "No GIS view defined for the model spp.base.gis.test.model. Please create a view or modify view mode",
        ):
            self.test_model._get_gis_view()

    def test_get_fields_of_type(self):
        fields_str = self.test_model.get_fields_of_type("geo_polygon")
        fields_list = self.test_model.get_fields_of_type(["geo_polygon"])

        self.assertIsInstance(fields_str, list)
        self.assertIsInstance(fields_list, list)
        self.assertEqual(len(fields_str), 1)
        self.assertEqual(len(fields_list), 1)
        self.assertEqual(fields_str[0].name, "geo_polygon_field")
        self.assertEqual(fields_list[0].name, "geo_polygon_field")
        self.assertEqual(fields_str[0].type, "geo_polygon")
        self.assertEqual(fields_list[0].type, "geo_polygon")
        self.assertEqual(type(fields_list[0]), type(fields_str[0]))
        self.assertEqual(fields_list[0], fields_str[0])

    def test_shape_to_geojson(self):
        point = Point(1, 1)

        geojson = self.test_model.shape_to_geojson(point)

        self.assertIsInstance(geojson, dict)
        self.assertEqual(geojson["type"], "Point")
        self.assertEqual(geojson["coordinates"], (1.0, 1.0))

    def test_convert_feature_to_featurecollection(self):
        feature = {
            "type": "Feature",
            "properties": {"name": "Test"},
            "geometry": {"type": "Point", "coordinates": [1, 1]},
        }

        feature_collection_dict = self.test_model.convert_feature_to_featurecollection(feature)
        feature_collection_list = self.test_model.convert_feature_to_featurecollection([feature])

        self.assertIsInstance(feature_collection_dict, dict)
        self.assertIsInstance(feature_collection_list, dict)
        self.assertEqual(feature_collection_list, feature_collection_dict)
        self.assertEqual(feature_collection_dict["type"], "FeatureCollection")
        self.assertEqual(len(feature_collection_dict["features"]), 1)
        self.assertEqual(feature_collection_dict["features"][0], feature)

    def test_get_field_type_from_layer_type(self):
        self.assertEqual(self.test_model.get_field_type_from_layer_type("polygon"), "geo_polygon")
        self.assertEqual(self.test_model.get_field_type_from_layer_type("point"), "geo_point")
        self.assertEqual(self.test_model.get_field_type_from_layer_type("line"), "geo_line")

        with self.assertRaisesRegex(UserError, "Invalid layer type error"):
            self.test_model.get_field_type_from_layer_type("error")

    def test_get_feature(self):
        feature = self.test_record_1.get_feature("geo_polygon_field")

        self.assertIsInstance(feature, list)
        self.assertEqual(len(feature), 1)
        self.assertIsInstance(feature[0], dict)
        self.assertEqual(feature[0]["type"], "Feature")
        self.assertIsInstance(feature[0]["geometry"], dict)
        self.assertEqual(feature[0]["geometry"]["type"], "Polygon")
        self.assertIsInstance(feature[0]["geometry"]["coordinates"], tuple)
        self.assertEqual(len(feature[0]["geometry"]["coordinates"]), 1)
        self.assertEqual(type(shape(feature[0]["geometry"])), Polygon)
