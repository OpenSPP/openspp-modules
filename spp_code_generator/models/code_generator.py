import base64
import logging

import yaml

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class CodeGenerator(models.Model):
    _name = "spp.code.generator"
    _description = "Code Generator"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="YAML Filename", required=True, index=True)
    description = fields.Text(string="Description")
    yaml_file = fields.Binary(string="YAML File", attachment=True, tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("processed", "Processed"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    processing_log = fields.Text(string="Processing Log", readonly=True)

    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", "The YAML filename must be unique!"),
    ]

    @api.constrains("yaml_file", "name")
    def _validate_yaml_file(self):
        """Validate that the uploaded file is a valid YAML file"""
        for record in self:
            if record.yaml_file and record.name:
                # Check file extension
                if not record.name.lower().endswith((".yaml", ".yml")):
                    raise ValidationError(_("Invalid file format. Filename must end with .yaml or .yml extension."))

                # Validate YAML content
                try:
                    yaml_content = base64.b64decode(record.yaml_file)
                    yaml.safe_load(yaml_content)
                except yaml.YAMLError as e:
                    raise ValidationError(_("Invalid YAML file. Error: %s") % str(e)) from e
                except Exception as e:
                    raise ValidationError(_("Failed to process YAML file. Error: %s") % str(e)) from e

    def _load_yaml_content(self):
        """
        Load and parse the YAML file content.

        Returns:
            dict: Parsed YAML content as a Python dictionary

        Raises:
            UserError: If YAML file is not uploaded or cannot be parsed
        """
        self.ensure_one()

        if not self.yaml_file:
            raise UserError(_("No YAML file uploaded. Please upload a YAML file first."))

        try:
            # Decode the binary content
            yaml_content = base64.b64decode(self.yaml_file)
            # Parse YAML
            yaml_data = yaml.safe_load(yaml_content)
            _logger.info("Successfully loaded YAML file: %s", self.name)
            return yaml_data
        except yaml.YAMLError as e:
            raise UserError(_("Failed to parse YAML file: %s") % str(e)) from e
        except Exception as e:
            raise UserError(_("Error loading YAML file: %s") % str(e)) from e

    def _get_odoo_field_type(self, yaml_field_type):
        """
        Map YAML field type to Odoo field type.

        Args:
            yaml_field_type (str): Field type from YAML (e.g., 'string', 'date', 'enum')

        Returns:
            str: Corresponding Odoo field type (e.g., 'char', 'date', 'selection')
        """
        type_mapping = {
            "string": "char",
            "date": "date",
            "datetime": "datetime",
            "enum": "selection",
            "boolean": "boolean",
            "integer": "integer",
            "float": "float",
            "text": "text",
            "admin_code": "char",  # Administrative code, treated as char
        }
        return type_mapping.get(yaml_field_type, "char")

    def _create_field_from_spec(self, entity_name, field_spec):
        """
        Create an Odoo field in res.partner based on field specification from YAML.

        Args:
            entity_name (str): Name of the entity (e.g., 'Household', 'Individual')
            field_spec (dict): Field specification containing id, label, type, etc.

        Returns:
            ir.model.fields: Created field record or None if field already exists

        Field Specification Structure:
            {
                'id': 'field_name',           # Required: Field technical name
                'label': 'Field Label',       # Required: Field display label
                'type': 'string',             # Required: Field type
                'required': True/False,       # Optional: Whether field is required
                'values': [...],              # Optional: For enum types, list of allowed values
                'description': '...'          # Optional: Help text for the field
            }
        """
        self.ensure_one()

        # Extract field specifications
        field_id = field_spec.get("id")
        field_label = field_spec.get("label")
        field_type = field_spec.get("type")
        is_required = field_spec.get("required", False)
        enum_values = field_spec.get("values", [])
        field_description = field_spec.get("description", "")

        if not all([field_id, field_label, field_type]):
            _logger.warning("Skipping field with incomplete specification: %s", field_spec)
            return None

        # Prepare field name with prefix based on OpenSPP conventions
        # z_cst_ prefix for custom fields
        field_name = f"z_cst_{field_id}"

        # Check if field already exists
        IrModelFields = self.env["ir.model.fields"]
        existing_field = IrModelFields.search([("model", "=", "res.partner"), ("name", "=", field_name)], limit=1)

        if existing_field:
            _logger.info("Field %s already exists in res.partner, skipping creation", field_name)
            return existing_field

        # Get the res.partner model ID
        partner_model = self.env["ir.model"].search([("model", "=", "res.partner")], limit=1)
        if not partner_model:
            raise UserError(_("res.partner model not found in the system"))

        # Map YAML type to Odoo type
        odoo_field_type = self._get_odoo_field_type(field_type)

        # Prepare field values
        field_values = {
            "name": field_name,
            "field_description": field_label,
            "model_id": partner_model.id,
            "model": "res.partner",
            "ttype": odoo_field_type,
            "required": is_required,
            "help": field_description or f"Custom field for {entity_name}: {field_label}",
            "state": "manual",  # Manual fields can be deleted
        }

        # Handle selection/enum fields
        if odoo_field_type == "selection" and enum_values:
            # Convert list of values to Odoo selection format
            # Format for selection_ids: [(0, 0, {'value': 'key', 'name': 'Label'}), ...]
            field_values["selection_ids"] = [(0, 0, {"value": val, "name": val}) for val in enum_values]

        try:
            # Create the field
            new_field = IrModelFields.create(field_values)
            _logger.info("Created field %s in res.partner for entity %s", field_name, entity_name)
            return new_field
        except Exception as e:
            _logger.error("Failed to create field %s: %s", field_name, str(e))
            raise UserError(_("Failed to create field %s: %s") % (field_name, str(e))) from e

    def action_process_entities(self):
        """
        Process the 'entities' section from the YAML file and create fields in res.partner.

        This method:
        1. Loads and parses the YAML file
        2. Extracts the 'entities' section
        3. For each entity, creates corresponding fields in res.partner
        4. Logs the processing results
        5. Updates the record state to 'processed'

        Returns:
            dict: Action to reload the form view with a success message
        """
        self.ensure_one()

        # Load YAML content
        yaml_data = self._load_yaml_content()

        # Extract entities section
        entities = yaml_data.get("entities", [])
        if not entities:
            raise UserError(_("No 'entities' section found in the YAML file"))

        # Initialize processing log
        log_lines = [
            "=" * 80,
            f"Processing YAML File: {self.name}",
            f"Started at: {fields.Datetime.now()}",
            "=" * 80,
            "",
        ]

        created_fields_count = 0
        skipped_fields_count = 0

        # Process each entity
        for entity in entities:
            entity_name = entity.get("name")
            entity_label = entity.get("label", entity_name)
            entity_fields = entity.get("fields", [])

            log_lines.append(f"Entity: {entity_name} ({entity_label})")
            log_lines.append("-" * 40)

            # Process each field in the entity
            for field_spec in entity_fields:
                field_id = field_spec.get("id")
                field_label = field_spec.get("label")
                field_type = field_spec.get("type")

                try:
                    result = self._create_field_from_spec(entity_name, field_spec)
                    if result:
                        created_fields_count += 1
                        log_lines.append(f"  ✓ Created: {field_id} ({field_label}) - Type: {field_type}")
                    else:
                        skipped_fields_count += 1
                        log_lines.append(f"  ⊗ Skipped: {field_id} ({field_label}) - Already exists")
                except Exception as e:
                    log_lines.append(f"  ✗ Error: {field_id} - {str(e)}")
                    _logger.error("Error creating field %s: %s", field_id, str(e))

            log_lines.append("")

        # Summary
        log_lines.extend(
            [
                "=" * 80,
                "SUMMARY",
                "=" * 80,
                f"Total fields created: {created_fields_count}",
                f"Total fields skipped: {skipped_fields_count}",
                f"Completed at: {fields.Datetime.now()}",
                "=" * 80,
            ]
        )

        # Update processing log
        processing_log = "\n".join(log_lines)
        self.write(
            {
                "processing_log": processing_log,
                "state": "processed",
            }
        )

        # Post message in chatter
        self.message_post(
            body=_(
                "Entity processing completed successfully.<br/>"
                "Fields created: <b>%s</b><br/>"
                "Fields skipped: <b>%s</b>"
            )
            % (created_fields_count, skipped_fields_count),
            subject="YAML Processing Complete",
        )

        # Return action to show success message and reload form
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": _("Entity processing completed. Created %s fields, skipped %s fields.")
                % (created_fields_count, skipped_fields_count),
                "type": "success",
                "sticky": False,
            },
        }
