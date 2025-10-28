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

    def _exec(self, expr, profile="registry_individuals"):
        """Helper to execute CEL expression."""
        registry = self.env["cel.registry"]
        cfg = registry.load_profile(profile)
        executor = self.env["cel.executor"].with_context(cel_profile=profile, cel_cfg=cfg)
        model = cfg.get("root_model", "res.partner")
        return executor.compile_and_preview(model, expr, limit=50)

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

    def _get_entity_prefix(self, entity_name):
        """
        Determine the field prefix based on entity type.

        Args:
            entity_name (str): Name of the entity (e.g., 'Household', 'Individual')

        Returns:
            str: Field prefix following OpenSPP conventions
                - 'x_cst_grp_' for groups/households
                - 'x_cst_indv_' for individuals
        """
        entity_lower = entity_name.lower()

        # Check if entity is a group/household
        if any(keyword in entity_lower for keyword in ["household", "group", "family"]):
            return "x_cst_grp"
        # Check if entity is an individual
        elif any(keyword in entity_lower for keyword in ["individual", "member", "person"]):
            return "x_cst_indv"
        else:
            # Default to group if uncertain
            _logger.warning(
                "Unknown entity type '%s', defaulting to group prefix. "
                "Consider using 'Household' or 'Individual' as entity names.",
                entity_name,
            )
            return "x_cst_grp"

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

        Field Naming Convention (matching spp_custom_fields_ui):
            - Groups/Households: x_cst_grp_{field_id}
            - Individuals: x_cst_indv_{field_id}
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

        # Prepare field name with prefix based on entity type
        # Follows spp_custom_fields_ui convention: x_cst_grp_ or x_cst_indv_
        prefix = self._get_entity_prefix(entity_name)
        field_name = f"{prefix}_{field_id}"

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

        # Determine target type for spp_custom_fields_ui integration
        target_type = "grp" if "grp" in prefix else "indv"

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
            "target_type": target_type,  # For spp_custom_fields_ui: 'grp' or 'indv'
            "field_category": "cst",  # For spp_custom_fields_ui: 'cst' (custom)
            "draft_name": field_id,  # Original field ID from YAML
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

    def _determine_indicator_type(self, expression, dependencies):
        """
        Determine if the indicator is for groups or individuals based on the expression.

        Args:
            expression (str): CEL expression for the indicator
            dependencies (list): List of field dependencies

        Returns:
            str: 'grp' for group indicators, 'indv' for individual indicators
        """
        expression_lower = expression.lower()

        # Check for group aggregation patterns
        group_patterns = [
            "members.exists",
            "members.count",
            "group_membership_ids",
            "compute_count_and_set_indicator",
        ]

        if any(pattern in expression_lower for pattern in group_patterns):
            return "grp"

        # Default to individual for simple expressions
        return "indv"

    def _generate_compute_method_code(self, field_name, expression, indicator_type, field_type):
        """
        Generate Python code for the compute method of an indicator field.

        Args:
            field_name (str): Full field name (e.g., x_ind_indv_age_yrs)
            expression (str): CEL expression
            indicator_type (str): 'grp' or 'indv'
            field_type (str): Field type (e.g., 'boolean', 'integer')

        Returns:
            str: Python code for the compute method

        Strategy:
            - Individual (indv): Use _exec() with CEL expression
            - Group (grp): Use compute_count_and_set_indicator() with CEL expression
        """

        code = None
        if indicator_type == "indv":
            # Individual indicator: Use _exec to evaluate CEL expression
            code = f"""
for record in self:
    try:
        if record.is_group:
            # This is an individual indicator, skip groups
            record.write({{'{field_name}': None}})
            continue

        # Execute CEL expression using _exec helper
        result = record._exec(
            '''{expression}''',
            profile='registry_individuals'
        )
"""
            if field_type == "integer":
                code += f"""
        record.write({{'{field_name}': result}})
"""
            else:
                code += f"""
        record.write({{'{field_name}': bool(record.id in result.get('ids', []))}})
"""
            code += f"""
    except Exception as e:
        record.write({{'{field_name}': None}})
"""
            return code

        elif indicator_type == "grp":
            # Group indicator: Use compute_count_and_set_indicator with CEL expression
            # This method is extended in group.py to handle CEL expressions
            code = f"""
kinds = None
domain = []
cel_expression = '''{expression}'''
self.compute_count_and_set_indicator(
    '{field_name}',
    kinds,
    domain,
    cel_expression=cel_expression
)
"""
        return code

    def _create_indicator_field(self, derived_spec):
        """
        Create an indicator (computed) field in res.partner from derived_fields specification.

        Args:
            derived_spec (dict): Derived field specification from YAML

        Returns:
            ir.model.fields: Created field record or None if already exists

        Derived Field Specification:
            {
                'id': 'age_yrs',
                'label': 'Age (years)',
                'expression': 'age_years(me.birthdate)',
                'purpose': 'eligibility, reporting',
                'dependencies': ['birthdate']
            }
        """
        self.ensure_one()

        # Extract specifications
        field_id = derived_spec.get("id")
        field_label = derived_spec.get("label")
        expression = derived_spec.get("expression", "")
        purpose = derived_spec.get("purpose", "")
        dependencies = derived_spec.get("dependencies", [])

        if not all([field_id, field_label, expression]):
            _logger.warning("Skipping derived field with incomplete specification: %s", derived_spec)
            return None

        # Determine if it's a group or individual indicator
        indicator_type = self._determine_indicator_type(expression, dependencies)

        # Create field name with indicator prefix
        if indicator_type == "grp":
            field_name = f"x_ind_grp_{field_id}"
        else:
            field_name = f"x_ind_indv_{field_id}"

        # Check if field already exists
        IrModelFields = self.env["ir.model.fields"]
        existing_field = IrModelFields.search([("model", "=", "res.partner"), ("name", "=", field_name)], limit=1)

        if existing_field:
            _logger.info("Indicator field %s already exists in res.partner, skipping", field_name)
            return None

        # Get the res.partner model ID
        partner_model = self.env["ir.model"].search([("model", "=", "res.partner")], limit=1)
        if not partner_model:
            raise UserError(_("res.partner model not found in the system"))

        # Determine field type based on expression
        # Most indicators are boolean or integer
        if any(keyword in expression.lower() for keyword in ["exists", "has", "is_"]):
            field_type = "boolean"
        elif any(keyword in expression.lower() for keyword in ["count", "sum", "age_years"]):
            field_type = "integer"
        else:
            field_type = "boolean"  # Default

        # Generate compute method code
        compute_code = self._generate_compute_method_code(
            field_name, expression, indicator_type, dependencies, field_type
        )

        # Prepare field values
        field_values = {
            "name": field_name,
            "field_description": field_label,
            "model_id": partner_model.id,
            "model": "res.partner",
            "ttype": field_type,
            "store": True,
            "compute": compute_code,
            "help": f"{purpose}",
            "state": "manual",
            "target_type": indicator_type,
            "field_category": "ind",
            "draft_name": field_id,
        }

        # Add dependency fields if specified
        if dependencies:
            # Convert dependencies to proper format
            dep_field_names = []
            for dep in dependencies:
                # Handle both simple names and prefixed names
                if not dep.startswith("x_"):
                    # Try to find the actual field name
                    dep_field = IrModelFields.search(
                        [("model", "=", "res.partner"), ("name", "ilike", f"%{dep}%")], limit=1
                    )
                    if dep_field:
                        dep_field_names.append(dep_field.name)
                    else:
                        dep_field_names.append(dep)
                else:
                    dep_field_names.append(dep)

            field_values["depends"] = ",".join(dep_field_names)

        try:
            # Create the field
            new_field = IrModelFields.create(field_values)
            _logger.info("Created indicator field %s in res.partner (type: %s)", field_name, indicator_type)

            # Log the compute code for debugging
            _logger.debug("Compute code for %s:\n%s", field_name, compute_code)

            return new_field
        except Exception as e:
            _logger.error("Failed to create indicator field %s: %s", field_name, str(e))
            raise UserError(_("Failed to create indicator field %s: %s") % (field_name, str(e))) from e

    def action_process_derived_fields(self):
        """
        Process the 'derived_fields' section from YAML and create indicator fields.

        This method:
        1. Loads and parses the YAML file
        2. Extracts the 'derived_fields' section
        3. For each derived field, creates corresponding indicator field in res.partner
        4. Generates compute methods with CEL expression handling
        5. Logs the processing results

        Returns:
            dict: Action to show success notification
        """
        self.ensure_one()

        # Load YAML content
        yaml_data = self._load_yaml_content()

        # Extract derived_fields section
        derived_fields = yaml_data.get("derived_fields", [])
        if not derived_fields:
            raise UserError(_("No 'derived_fields' section found in the YAML file"))

        # Initialize processing log
        log_lines = [
            "=" * 80,
            f"Processing Derived Fields from: {self.name}",
            f"Started at: {fields.Datetime.now()}",
            "=" * 80,
            "",
        ]

        created_count = 0
        skipped_count = 0
        error_count = 0

        # Process each derived field
        for derived_spec in derived_fields:
            field_id = derived_spec.get("id")
            field_label = derived_spec.get("label")
            expression = derived_spec.get("expression")
            indicator_type = self._determine_indicator_type(expression, derived_spec.get("dependencies", []))

            try:
                result = self._create_indicator_field(derived_spec)
                if result:
                    created_count += 1
                    log_lines.append(f"  ✓ Created: {field_id} ({field_label}) - Type: {indicator_type} indicator")
                    log_lines.append(f"    Expression: {expression}")
                else:
                    skipped_count += 1
                    log_lines.append(f"  ⊗ Skipped: {field_id} ({field_label}) - Already exists")
            except Exception as e:
                error_count += 1
                log_lines.append(f"  ✗ Error: {field_id} - {str(e)}")
                _logger.error("Error creating indicator field %s: %s", field_id, str(e))

        # Summary
        log_lines.extend(
            [
                "",
                "=" * 80,
                "SUMMARY",
                "=" * 80,
                f"Indicator fields created: {created_count}",
                f"Indicator fields skipped: {skipped_count}",
                f"Errors encountered: {error_count}",
                f"Completed at: {fields.Datetime.now()}",
                "=" * 80,
            ]
        )

        # Append to existing log
        existing_log = self.processing_log or ""
        new_log = "\n".join(log_lines)

        self.write(
            {
                "processing_log": existing_log + "\n\n" + new_log if existing_log else new_log,
            }
        )

        # Post message in chatter
        self.message_post(
            body=_(
                "Derived fields processing completed.\n"
                "Indicators created: %s\n"
                "Indicators skipped: %s\n"
                "Errors: %s"
            )
            % (created_count, skipped_count, error_count),
            subject="Derived Fields Processing Complete",
        )

        # Return success notification
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": _("Derived fields processing completed. Created %s indicators, skipped %s, errors %s.")
                % (created_count, skipped_count, error_count),
                "type": "success",
                "sticky": False,
            },
        }

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
            body=_("Entity processing completed successfully.\n" "Fields created: %s\n" "Fields skipped: %s")
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
