import json

from odoo import _, fields, models


class OpenSPPAreaImport(models.Model):
    _inherit = "spp.area.import"

    def get_column_indexes(self, columns, area_level):
        column_indexes = super().get_column_indexes(columns, area_level)

        if "latitude" in columns and "longitude" in columns:
            column_indexes["latitude_index"] = columns.index("latitude")
            column_indexes["longitude_index"] = columns.index("longitude")

        return column_indexes

    def get_area_vals(self, column_indexes, row, sheet, area_level):
        vals = super().get_area_vals(column_indexes, row, sheet, area_level)

        if "latitude_index" in column_indexes and "longitude_index" in column_indexes:
            vals["latitude"] = sheet.cell(row, column_indexes["latitude_index"]).value
            vals["longitude"] = sheet.cell(row, column_indexes["longitude_index"]).value

        return vals


class OpenSPPAreaImportActivities(models.Model):
    _inherit = "spp.area.import.raw"

    latitude = fields.Float(digits=(13, 10))
    longitude = fields.Float(digits=(13, 10))

    def check_errors(self):
        errors = super().check_errors()
        if self.latitude and (self.latitude < -90 or self.latitude > 90):
            errors.append(_("Latitude must be between -90 and 90"))
        if self.longitude and (self.longitude < -180 or self.longitude > 180):
            errors.append(_("Longitude must be between -180 and 180"))
        if self.latitude and not self.longitude:
            errors.append(_("Longitude is required if Latitude is provided"))
        if self.longitude and not self.latitude:
            errors.append(_("Latitude is required if Longitude is provided"))
        return errors

    def get_area_vals(self):
        area_vals = super().get_area_vals()

        if self.latitude and self.longitude:
            point_geojson = {"type": "Point", "coordinates": [self.longitude, self.latitude]}
            area_vals["coordinates"] = json.dumps(point_geojson)

        return area_vals
