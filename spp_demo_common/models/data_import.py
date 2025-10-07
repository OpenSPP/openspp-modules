import base64
import datetime
import json
import logging

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
    validated = fields.Boolean(string="Validated", readonly=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("imported", "Imported"),
            ("validated", "Validated"),
            ("in_progress", "In Progress"),
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
                raw.validated = True
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
            self.validated = True
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

        x2_many_vals = []

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
                    raw_id = raw_record.id
                    processed_raw = f"raw:{raw_id}"
                    x2_many_vals.append(processed_raw)

                except Exception as e:
                    _logger.error(f"Error processing x2many for {comodel_name} " f"old_id {old_id}: {str(e)}")
                    continue
            else:
                _logger.warning(f"No raw record found for {comodel_name} with old ID {old_id}")

        return x2_many_vals if x2_many_vals else False

    def create_records(self):
        """
        Creates actual Odoo records from validated raw data.
        Recursively creates many2one dependencies as needed.
        Skips one2many and many2many for first pass.
        """
        self.ensure_one()

        # if self.state != "validated":
        #     raise ValidationError("Import must be validated before creating records.")

        self.locked = True
        self.locked_reason = "Creating records..."

        # Maps "raw:{raw_id}" to actual created Odoo record ID
        created_mapping = {}

        # First pass: Create records (handling many2one recursively)
        for raw in self.raw_ids:
            if raw.state not in ["validated", "error"]:
                continue

            try:
                self._create_single_record(raw, created_mapping)
            except Exception as e:
                raw.write({"state": "error", "remarks": f"Processing failed: {str(e)}"})
                _logger.error(f"Error processing raw {raw.id}: {str(e)}")

        # Update import state
        failed_count = len(self.raw_ids.filtered(lambda r: r.state == "error"))
        success_count = len(self.raw_ids.filtered(lambda r: r.state in ["created", "saved"]))

        if failed_count > 0:
            self.state = "error"
            self.locked = False
            self.remarks = f"Creation completed with issues: {success_count} created, {failed_count} failed."
        elif success_count == len(self.raw_ids):
            self.state = "completed"
            self.locked = True
            self.locked_reason = f"Import completed successfully: {success_count} records created."
            self.remarks = f"Import completed successfully: {success_count} records created."

    def _create_single_record(self, raw, created_mapping, _creating=None):
        """
        Creates a single record, handling many2one dependencies recursively.

        :param raw: The raw record to create
        :param created_mapping: Dict mapping raw:{id} to created record IDs
        :param _creating: Set to track records being created (prevents circular dependencies)
        :return: Created record ID
        """
        _logger.info(f"Creating record for raw {raw.id} ({raw.model_name})")
        _logger.info(f"_creating: {_creating}, created_mapping keys: {list(created_mapping.keys())}")

        if _creating is None:
            _creating = set()

        raw_ref = f"raw:{raw.id}"

        # Check if already created
        if raw_ref in created_mapping:
            return created_mapping[raw_ref]

        # Check for circular dependency
        if raw.id in _creating:
            raise ValidationError(f"Circular dependency detected for raw {raw.id}")

        _creating.add(raw.id)

        try:
            json_data = json.loads(raw.json_data)
            model = self.env[raw.model_name]

            # Check if record already exists
            existing_id = self._check_existing_record(raw, json_data, model, created_mapping, raw_ref)
            if existing_id:
                return existing_id

            # Build creation data
            creation_data = self._build_creation_data(raw, json_data, model, created_mapping, _creating)

            # Create the record
            new_record = model.create(creation_data)
            created_mapping[raw_ref] = new_record.id

            raw.write(
                {
                    "state": "created",
                    "db_id": new_record.id,
                    "remarks": False,
                }
            )

            _logger.info(f"Created {raw.model_name} record ID {new_record.id} from raw {raw.id}")
            return new_record.id

        except Exception as e:
            error_msg = str(e)
            raw.write(
                {
                    "state": "error",
                    "remarks": f"Creation failed: {error_msg}",
                }
            )
            _logger.error(f"Error creating record from raw {raw.id}: {error_msg}")
            raise
        finally:
            _creating.discard(raw.id)

    def _check_existing_record(self, raw, json_data, model, created_mapping, raw_ref):
        """Check if record already exists based on common identifying fields."""
        possible_fields = ["name", "code", "value", "phone_no", "display_name", "email"]
        domain = []
        for field in possible_fields:
            if field in json_data and field in model._fields:
                # Check if field is a stored field
                if not model._fields[field].store:
                    continue
                domain.append((field, "=", json_data[field]))

        if domain:
            existing = model.search(domain, limit=1)
            if existing:
                raw.write(
                    {
                        "state": "saved",
                            "db_id": existing.id,
                            "remarks": "Record already exists, skipped creation.",
                        }
                    )
                    created_mapping[raw_ref] = existing.id
                    _logger.info(f"Skipped creation for raw {raw.id}, record already exists with ID {existing.id}")
                    return existing.id

        return None

    def _build_creation_data(self, raw, json_data, model, created_mapping, _creating):
        """Build the creation data dictionary from json_data."""
        creation_data = {}

        for field_name, value in json_data.items():
            if field_name not in model._fields:
                continue

            field = model._fields[field_name]

            # Skip one2many fields
            if field.type == "one2many":
                continue

            # Handle many2many fields
            if field.type == "many2many":
                creation_data[field_name] = self._create_process_many2many_field(
                    field_name, value, created_mapping, _creating
                )
                continue

            # Skip self-referencing many2one fields
            if field.type == "many2one" and field.comodel_name == raw.model_name:
                continue

            # Handle many2one with raw reference
            if field.type == "many2one" and isinstance(value, str) and value.startswith("raw:"):
                creation_data[field_name] = self._create_process_many2one_field(
                    field_name, value, created_mapping, _creating
                )
                continue

            # Handle date/datetime fields
            if field.type in ("date", "datetime"):
                creation_data[field_name] = self._create_process_datetime_field(field.type, value)
                continue

            creation_data[field_name] = value

        return creation_data

    def _create_process_many2many_field(self, field_name, value, created_mapping, _creating):
        """Process many2many field values."""
        if not isinstance(value, list):
            return False

        many2many_ids = []
        for item in value:
            if isinstance(item, str) and item.startswith("raw:"):
                ref_raw_id = int(item.split(":")[1])
                ref_raw = self.raw_ids.filtered(lambda r, ref_raw_id=ref_raw_id: r.id == ref_raw_id)

                _logger.info(
                    f"Resolving many2many for field {field_name} with value {value} | referencing raw {ref_raw_id}"
                )

                if ref_raw and not ref_raw.db_id:
                    resolved_id = self._create_single_record(ref_raw, created_mapping, _creating)
                    many2many_ids.append(resolved_id)
                elif ref_raw and ref_raw.db_id:
                    many2many_ids.append(ref_raw.db_id)
                else:
                    _logger.warning(f"Referenced raw {item} not found for field {field_name}")

        return [(6, 0, many2many_ids)]

    def _create_process_many2one_field(self, field_name, value, created_mapping, _creating):
        """Process many2one field with raw reference."""
        ref_raw_id = int(value.split(":")[1])
        ref_raw = self.raw_ids.filtered(lambda r: r.id == ref_raw_id)

        _logger.info(f"Resolving many2one for field {field_name} with value {value} | referencing raw {ref_raw_id}")

        if ref_raw and not ref_raw.db_id:
            return self._create_single_record(ref_raw, created_mapping, _creating)
        elif ref_raw and ref_raw.db_id:
            return ref_raw.db_id
        else:
            _logger.warning(f"Referenced raw {value} not found for field {field_name}")
            return False

    def _create_process_datetime_field(self, field_type, value):
        """Process date or datetime field values."""
        if not isinstance(value, str):
            return value

        try:
            if field_type == "date":
                if "T" in value:
                    return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
                return datetime.datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d")
            else:  # datetime
                if "T" in value:
                    return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return False

    def _resolve_references(self, data, created_mapping):
        """
        Recursively resolve raw references in data structures.

        :param data: Dict or value containing potential raw references
        :param created_mapping: Mapping of raw:{id} to actual record IDs
        :return: Data with resolved references
        """
        if isinstance(data, dict):
            resolved = {}
            for k, v in data.items():
                resolved[k] = self._resolve_references(v, created_mapping)
            return resolved

        elif isinstance(data, list):
            resolved = []
            for item in data:
                resolved.append(self._resolve_references(item, created_mapping))
            return resolved

        elif isinstance(data, str) and data.startswith("raw:"):
            resolved_id = created_mapping.get(data)
            if resolved_id:
                return resolved_id
            else:
                _logger.warning(f"Unresolved reference: {data}")
                return False

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
