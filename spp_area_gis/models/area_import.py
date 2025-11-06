# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import base64
import json
import logging
import time

from odoo import _, fields, models

_logger = logging.getLogger(__name__)
_area_import_raw_model = "spp.area.import.raw"
_res_lang_model = "res.lang"


class OpenSPPAreaImport(models.Model):
    _inherit = "spp.area.import"

    def _import_data_from_json(self, json_file_id):
        """
        Override to extract latitude and longitude from JSON data.
        Handles GIS data: LATITUDE and LONGITUDE columns.
        """
        self.ensure_one()
        import_start = time.time()

        json_file_record = self.env["spp.area.import.json"].browse(json_file_id)
        _logger.info(
            f"Area Import (GIS): Processing {json_file_record.json_file_name} "
            f"(batch {json_file_record.batch_number})"
        )

        # Decode and parse JSON
        json_bytes = base64.b64decode(json_file_record.json_file)
        json_string = json_bytes.decode("utf-8")
        rows = json.loads(json_string)

        _logger.info(f"Area Import (GIS): Loaded {len(rows)} rows from {json_file_record.json_file_name}")

        # Get active languages for mapping ISO codes
        active_languages = self.env[_res_lang_model].search([("active", "=", True)])
        lang_mapping = {lang.iso_code.upper(): lang.code for lang in active_languages}

        # Process each row
        for idx, row_data in enumerate(rows):
            row_start = time.time()

            area_level = row_data.get("_area_level", 0)

            # Extract current level fields (highest level in this row)
            admin_code_key = f"ADM{area_level}_PCODE"
            admin_code = row_data.get(admin_code_key)

            # Get default EN value directly
            default_name = row_data.get(f"ADM{area_level}_EN")

            # Find all translations for this level
            admin_level_prefix = f"ADM{area_level}_"
            translations = {"en_US": default_name}  # Start with EN as default

            for key, value in row_data.items():
                if key.startswith(admin_level_prefix) and key != admin_code_key:
                    lang_code = key.replace(admin_level_prefix, "")
                    if lang_code != "EN" and lang_code in lang_mapping:
                        # If empty or None, use default EN value
                        if not value or not str(value).strip():
                            translations[lang_mapping[lang_code]] = default_name
                        else:
                            translations[lang_mapping[lang_code]] = value

            # Extract parent level fields (one level lower)
            parent_name = None
            parent_code = None
            if area_level > 0:
                parent_level = area_level - 1
                parent_name_key = f"ADM{parent_level}_EN"  # Use EN for parent name
                parent_code_key = f"ADM{parent_level}_PCODE"
                parent_name = row_data.get(parent_name_key)
                parent_code = row_data.get(parent_code_key)

            # Extract GIS data (latitude and longitude)
            latitude = row_data.get("LATITUDE") or row_data.get("latitude")
            longitude = row_data.get("LONGITUDE") or row_data.get("longitude")

            # Create raw import record with default name
            raw_vals = {
                "area_import_id": self.id,
                "admin_name": default_name,
                "admin_code": admin_code,
                "parent_name": parent_name,
                "parent_code": parent_code,
                "level": area_level,
                "area_sqkm": row_data.get("AREA_SQKM"),
            }

            # Add GIS fields if present
            if latitude is not None:
                raw_vals["latitude"] = latitude
            if longitude is not None:
                raw_vals["longitude"] = longitude

            raw_record = self.env[_area_import_raw_model].create(raw_vals)

            # Update translations for all languages found
            for lang_code, translated_name in translations.items():
                if lang_code != "en_US":  # Skip default language (already set)
                    raw_record.with_context(lang=lang_code).write(
                        {
                            "admin_name": translated_name,
                        }
                    )

            row_time = time.time() - row_start
            if (idx + 1) % 10 == 0:  # Log every 10 rows
                _logger.info(
                    f"Area Import (GIS): Processed {idx + 1}/{len(rows)} rows from batch "
                    f"{json_file_record.batch_number} (last row: {row_time:.4f}s, "
                    f"translations: {len(translations)}, coordinates: {'present' if latitude and longitude else 'absent'})"
                )

        batch_time = time.time() - import_start
        _logger.info(
            f"Area Import (GIS): Completed batch {json_file_record.batch_number} - "
            f"{len(rows)} rows in {batch_time:.2f}s"
        )


class OpenSPPAreaImportActivities(models.Model):
    _inherit = "spp.area.import.raw"

    latitude = fields.Float(digits=(13, 10))
    longitude = fields.Float(digits=(13, 10))

    def check_errors(self):
        """Validate latitude and longitude values"""
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
        """
        Add GIS coordinates to area values when saving to spp.area.
        Converts latitude/longitude to GeoJSON Point format.
        """
        area_vals = super().get_area_vals()

        if self.latitude and self.longitude:
            point_geojson = {
                "type": "Point",
                "coordinates": [self.longitude, self.latitude],
            }
            area_vals["coordinates"] = json.dumps(point_geojson)

        return area_vals
