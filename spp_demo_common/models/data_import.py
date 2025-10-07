import base64
import json
import logging
import datetime

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SPPDataImporter(models.Model):
    _name = "spp.data.importer"
    _description = "SPP Data Importer"

    name = fields.Char(string="Name", required=True)
    import_file = fields.Binary(string="Import File", required=True)
    import_filename = fields.Char(string="Import Filename", required=True)

    module_ids = fields.Many2many(
        "ir.module.module",
        string="Modules",
        help="Select the modules to include in the export.",
        compute="_compute_module_ids",
    )
    module_list = fields.Text(string="Module List", readonly=True)

    model_ids = fields.Many2many(
        "ir.model",
        string="Models",
        help="Select the models to include in the export.",
        compute="_compute_model_ids",
    )
    model_list = fields.Text(string="Model List", readonly=True)

    raw_ids = fields.One2many("spp.data.importer.raw", "importer_id", string="Raw Data", readonly=True)
    summary_ids = fields.One2many("spp.data.importer.summary", "importer_id", string="Summary", readonly=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("imported", "Imported"),
            ("validated", "Validated"),
            ("in_progress", "In Progress"),
            ("partial", "Partial"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
            ("error", "Error"),
        ],
        string="State",
        default="draft",
        required=True,
    )
    locked = fields.Boolean(string="Locked", default=False)
    locked_reason = fields.Text(string="Locked Reason")
    remarks = fields.Text(string="Remarks")

    def start_import(self):
        self.ensure_one()
        self.state = "in_progress"
        self.locked = True
        self.locked_reason = "Import in progress..."
        self.raw_ids = False
        try:
            file_data = base64.b64decode(self.import_file)
            json_data = json.loads(file_data)
            raw_vals = []
            summary_data = []
            for data in json_data[1:]:
                model_name = data.get("model")
                summary_data.append(
                    {
                        "name": data.get("model", ""),
                        "importer_id": self.id,
                        "model_name": data.get("model", ""),
                        "record_count": data.get("record_count", 0),
                    }
                )

                for record in data.get("data", []):
                    model_data = record
                    name = record.get("name", f"ID: {record.get('id', '')}")

                    raw_vals.append(
                        {
                            "name": name,
                            "model_name": model_name,
                            "importer_id": self.id,
                            "json_data": json.dumps(model_data),
                        }
                    )
            self.summary_ids = [(0, 0, vals) for vals in summary_data]
            self.raw_ids = [(0, 0, vals) for vals in raw_vals]
            self.state = "imported"
            self.locked = False
            self.locked_reason = "Import completed successfully."

        except Exception as e:
            raise ValidationError(f"Failed to parse import file: {e}") from e

    def validate_import(self):
        """
        Validates import and processes related fields in JSON data.
        Replaces old IDs from source DB with references to raw records.
        Maps: old_id -> raw_record_id for later creation.
        """
        self.ensure_one()
        if self.state not in ["imported", "error"]:
            raise ValidationError("Import must be in 'Imported' or 'Error' state to validate.")

        self.locked = True
        self.locked_reason = "Import being validated."

        # Build mapping: (model_name, old_record_id) -> raw_record
        raw_mapping = {}

        for raw in self.raw_ids:
            raw.json_data = raw.json_data.replace("'", '"')  # Ensure proper JSON format
            if isinstance(raw.json_data, str):
                json_data = json.loads(raw.json_data)
            else:
                json_data = raw.json_data
            try:
                old_id = json_data.get("id") or raw.record_id
                key = (raw.model_name, old_id)
                raw_mapping[key] = raw
                raw.state = "draft"
                raw.remarks = False
            except Exception as e:
                raw.state = "error"
                raw.remarks = f"Failed to build mapping: {str(e)}"
                _logger.error(f"Error mapping raw record {raw.id}: {str(e)}")

        # Process each raw record and update json_data
        for raw in self.raw_ids:
            if raw.state == "error":
                continue

            if isinstance(raw.json_data, str):
                json_data = json.loads(raw.json_data)
            else:
                json_data = raw.json_data
            try:
                model = self.env[raw.model_name]

                # Process and update related fields
                updated_json_data = self._process_related_fields(model, json_data, raw_mapping)

                # Remove the old 'id' field as Odoo will generate new one
                updated_json_data.pop("id", None)

                # Update the raw record with processed data
                raw.json_data = json.dumps(updated_json_data)
                raw.state = "validated"
                raw.remarks = False

            except Exception as e:
                raw.state = "error"
                raw.remarks = f"Validation failed: {str(e)}"
                _logger.error(f"Error validating raw record {raw.id}: {str(e)}")

        # Check if all records validated successfully
        failed_count = self.raw_ids.filtered(lambda r: r.state == "error")
        if failed_count:
            self.state = "error"
            self.remarks = f"Validation failed for {len(failed_count)} records."
            self.locked = False
        else:
            self.state = "validated"
            self.remarks = "Import validated successfully."
            self.locked = False

    def _process_related_fields(self, model, json_data, raw_mapping):
        """
        Process all fields in json_data and convert old IDs to raw record references.

        :param model: Odoo model object
        :param json_data: Dictionary of field values from source DB
        :param raw_mapping: Mapping of (model_name, old_id) to raw records
        :return: Updated json_data dictionary
        """
        updated_data = json_data.copy()

        for field_name, field_value in json_data.items():
            # Skip empty values, id field, and non-existent fields
            if field_value is False or field_value is None or field_name == "id":
                continue

            if field_name not in model._fields:
                continue

            field = model._fields[field_name]
            field_type = field.type

            # Handle many2one fields
            if field_type == "many2one":
                updated_data[field_name] = self._process_many2one_field(field, field_value, raw_mapping)

            # Handle one2many fields
            elif field_type == "one2many":
                updated_data[field_name] = self._process_x2many_field(field, field_value, raw_mapping)

            # Handle many2many fields
            elif field_type == "many2many":
                updated_data[field_name] = self._process_x2many_field(field, field_value, raw_mapping)

        return updated_data

    def _process_many2one_field(self, field, field_value, raw_mapping):
        """
        Process many2one field: converts old ID to raw record reference.
        Format: "raw:{raw_record_id}"

        :param field: Odoo field object
        :param field_value: Old record ID from source database
        :param raw_mapping: Mapping of (model_name, old_id) to raw records
        :return: String reference to raw record or False
        """
        comodel_name = field.comodel_name

        # If already processed, return as-is
        if isinstance(field_value, str) and field_value.startswith("raw:"):
            return field_value

        # If it's a list/tuple (shouldn't be for many2one), take first element
        if isinstance(field_value, list | tuple):
            field_value = field_value[0] if field_value else False

        if not field_value:
            return False

        # Look up the raw record by old ID
        key = (comodel_name, field_value)
        raw_record = raw_mapping.get(key)

        if raw_record:
            # Return reference to raw record for later creation
            return f"raw:{raw_record.id}"

        # No raw record found - might be a system record or not exported
        _logger.warning(
            f"No raw record found for {comodel_name} with old ID {field_value}. " f"Field will be set to False."
        )
        return False

    def _process_x2many_field(self, field, field_value, raw_mapping):
        """
        Process one2many/many2many: converts old IDs to Odoo create commands.
        Format: [(0, 0, {processed_fields}), ...]

        :param field: Odoo field object
        :param field_value: List of old record IDs or list of dicts
        :param raw_mapping: Mapping of (model_name, old_id) to raw records
        :return: List of Odoo command tuples
        """
        comodel_name = field.comodel_name

        # If already processed (list of command tuples), return as-is
        if isinstance(field_value, list) and field_value:
            if isinstance(field_value[0], list | tuple):
                return field_value

        # Ensure field_value is a list
        if not isinstance(field_value, list):
            field_value = [field_value] if field_value else []

        commands = []

        for item in field_value:
            if not item:
                continue

            # Extract old_id (could be just ID or dict with 'id' key)
            if isinstance(item, dict):
                old_id = item.get("id")
            else:
                old_id = item

            if not old_id:
                continue

            # Look up the raw record by old ID
            key = (comodel_name, old_id)
            raw_record = raw_mapping.get(key)

            if raw_record:
                try:
                    # Parse the raw record's json_data
                    related_json_data = json.loads(raw_record.json_data)

                    # Recursively process related fields in this data
                    processed_data = self._process_related_fields(
                        self.env[comodel_name], related_json_data, raw_mapping
                    )

                    # Remove old ID
                    processed_data.pop("id", None)

                    # Add create command (0, 0, {fields})
                    commands.append((0, 0, processed_data))

                except Exception as e:
                    _logger.error(f"Error processing x2many for {comodel_name} " f"old_id {old_id}: {str(e)}")
                    continue
            else:
                _logger.warning(f"No raw record found for {comodel_name} with old ID {old_id}")

        return commands if commands else False

    def create_records(self):
        """
        Creates actual Odoo records from validated raw data.
        Processes records in dependency order and maps old IDs to new IDs.
        """
        self.ensure_one()

        if self.state != "validated":
            raise ValidationError("Import must be validated before creating records.")

        self.locked = True
        self.locked_reason = "Creating records..."

        # Maps "raw:{raw_id}" to actual created Odoo record ID
        created_mapping = {}

        # Sort raw records by dependencies (topological sort)
        sorted_raws = self._topological_sort_raws()

        for raw in sorted_raws:
            if raw.state != "validated":
                continue

            try:
                json_data = json.loads(raw.json_data)
                model = self.env[raw.model_name]

                # Replace "raw:{id}" references with actual new record IDs
                final_data = self._resolve_raw_references(json_data, created_mapping)
                
                # Convert date fields if necessary
                for field_name, field in model._fields.items():
                    if field.type == "date" and field_name in final_data:
                        val = final_data[field_name]
                        if isinstance(val, str):
                            try:
                                # Accept ISO or standard date
                                if "T" in val:
                                    val = datetime.datetime.strptime(val, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
                                else:
                                    val = datetime.datetime.strptime(val, "%Y-%m-%d").strftime("%Y-%m-%d")
                                final_data[field_name] = val
                            except Exception:
                                final_data[field_name] = False
                        else:
                            final_data[field_name] = False
                    elif field.type == "datetime" and field_name in final_data:
                        val = final_data[field_name]
                        if isinstance(val, str):
                            try:
                                # Accept ISO or standard datetime
                                if "T" in val:
                                    val = datetime.datetime.strptime(val, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                                else:
                                    val = datetime.datetime.strptime(val, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                                final_data[field_name] = val
                            except Exception:
                                final_data[field_name] = False
                        else:
                            final_data[field_name] = False
                            
                # Create the record
                new_record = model.create(final_data)

                # Store mapping: raw reference -> new Odoo ID
                created_mapping[f"raw:{raw.id}"] = new_record.id

                # Update raw record with new DB ID
                raw.write(
                    {
                        "state": "created",
                        "db_id": new_record.id,  # Store the actual new Odoo ID
                        "error_message": False,
                    }
                )

                _logger.info(
                    f"Created {raw.model_name} record ID {new_record.id} "
                    f"from raw {raw.id} (old ID: {raw.record_id})"
                )

            except Exception as e:
                raw.write({"state": "error", "error_message": f"Creation failed: {str(e)}"})
                _logger.error(f"Error creating record from raw {raw.id}: {str(e)}")

        # Update import state
        failed_count = len(self.raw_ids.filtered(lambda r: r.state == "error"))
        success_count = len(self.raw_ids.filtered(lambda r: r.state == "created"))

        if failed_count > 0:
            self.state = "partial"
            self.locked_reason = f"Import completed: {success_count} created, {failed_count} failed."
        else:
            self.state = "completed"
            self.locked_reason = f"Import completed successfully: {success_count} records created."

    def _resolve_raw_references(self, data, created_mapping):
        """
        Recursively resolve "raw:{id}" references to actual new record IDs.

        :param data: Dictionary, list, or value that may contain raw references
        :param created_mapping: Mapping of "raw:{id}" to actual new Odoo IDs
        :return: Data with resolved references
        """
        if isinstance(data, dict):
            resolved = {}
            for k, v in data.items():
                resolved[k] = self._resolve_raw_references(v, created_mapping)
            return resolved

        elif isinstance(data, list):
            resolved = []
            for item in data:
                # Handle command tuples (0, 0, {dict})
                if isinstance(item, list | tuple) and len(item) == 3:
                    cmd, _, vals = item
                    resolved_vals = self._resolve_raw_references(vals, created_mapping)
                    resolved.append((cmd, 0, resolved_vals))
                else:
                    resolved.append(self._resolve_raw_references(item, created_mapping))
            return resolved

        elif isinstance(data, str) and data.startswith("raw:"):
            # Resolve the reference
            new_id = created_mapping.get(data)
            if new_id is None:
                _logger.warning(f"Unresolved raw reference: {data}")
                return False
            return new_id

        else:
            return data

    def _topological_sort_raws(self):
        """
        Sort raw records in dependency order using topological sort.
        Records with fewer dependencies are processed first.
        """
        # Build dependency graph
        dependencies = {}  # raw_id -> set of raw_ids it depends on

        for raw in self.raw_ids:
            if raw.state != "validated":
                continue

            deps = set()
            try:
                json_data = json.loads(raw.json_data)
                deps = self._extract_raw_dependencies(json_data)
            except Exception as e:
                _logger.error(f"Error extracting dependencies for raw {raw.id}: {e}")

            dependencies[raw.id] = deps

        # Perform topological sort
        sorted_ids = []
        visited = set()

        def visit(raw_id):
            if raw_id in visited:
                return
            visited.add(raw_id)

            # Visit dependencies first
            for dep_id in dependencies.get(raw_id, set()):
                if dep_id in dependencies:  # Only if it's in our set
                    visit(dep_id)

            sorted_ids.append(raw_id)

        for raw_id in dependencies.keys():
            visit(raw_id)

        # Return raw records in sorted order
        id_to_raw = {r.id: r for r in self.raw_ids}
        return [id_to_raw[rid] for rid in sorted_ids if rid in id_to_raw]

    def _extract_raw_dependencies(self, data):
        """
        Extract all "raw:{id}" references from data structure.

        :param data: Dictionary, list, or value
        :return: Set of raw record IDs this data depends on
        """
        dependencies = set()

        if isinstance(data, dict):
            for value in data.values():
                dependencies.update(self._extract_raw_dependencies(value))

        elif isinstance(data, list):
            for item in data:
                dependencies.update(self._extract_raw_dependencies(item))

        elif isinstance(data, str) and data.startswith("raw:"):
            # Extract the raw record ID
            raw_id = int(data.split(":")[1])
            dependencies.add(raw_id)

        return dependencies

    @api.depends("module_list")
    def _compute_module_ids(self):
        for rec in self:
            rec.module_ids = False
            if rec.module_list:
                module_names = [name.strip() for name in rec.module_list.split(",") if name.strip()]
                modules = self.env["ir.module.module"].search([("name", "in", module_names)])
                rec.module_ids = modules

    @api.depends("model_list")
    def _compute_model_ids(self):
        for rec in self:
            rec.model_ids = False
            if rec.model_list:
                model_names = [name.strip() for name in rec.model_list.split(",") if name.strip()]
                models = self.env["ir.model"].search([("model", "in", model_names)])
                rec.model_ids = models

    @api.onchange("import_file")
    def _onchange_import_file(self):
        self.module_list = ""
        self.model_list = ""
        self.summary_ids = False
        if self.import_file:
            try:
                file_data = base64.b64decode(self.import_file)
                json_data = json.loads(file_data)
                modules = json_data[0].get("modules", [])
                if isinstance(modules, list):
                    self.module_list = ", ".join(modules)
                else:
                    self.module_list = modules or ""
                models = []
                for data in json_data[1:]:
                    models.append(data.get("model", ""))
                self.model_list = ", ".join(models)
            except Exception as e:
                raise ValidationError(f"Failed to parse import file: {e}") from e

    def refresh_page(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
