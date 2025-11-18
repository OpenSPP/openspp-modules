# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

import yaml

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProgramSpec(models.Model):
    _name = "spp.program.spec"
    _description = "Program Specification"
    _order = "sequence, name"

    name = fields.Char(string="Program Name", help="Auto-populated from YAML during validation")
    code = fields.Char(string="Program Code", required=True, help="Unique code for the program")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # YAML file upload
    yaml_file = fields.Binary(string="Upload YAML File", help="Upload a YAML program specification file")
    yaml_filename = fields.Char(string="Filename")

    # YAML content (can be populated from file or entered manually)
    yaml_content = fields.Text(
        string="YAML Specification",
        help="Program specification in YAML format (auto-populated from uploaded file or enter manually)",
        required=False,
    )

    # Parsed data
    spec_data = fields.Text(
        string="Parsed Specification",
        compute="_compute_spec_data",
        store=True,
        help="JSON representation of parsed YAML",
    )

    # Status and processing
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("validated", "Validated"),
            ("deployed", "Deployed"),
            ("error", "Error"),
        ],
        default="draft",
        required=True,
    )

    error_message = fields.Text(string="Error Message", readonly=True)
    last_deployed = fields.Datetime(string="Last Deployed", readonly=True)

    # Related event types
    event_type_ids = fields.One2many("spp.event.type.definition", "program_spec_id", string="Event Types")
    event_type_count = fields.Integer(string="Event Type Count", compute="_compute_event_type_count")

    # Metadata from YAML
    program_objectives = fields.Text(string="Objectives")
    currency = fields.Char(string="Currency")
    languages = fields.Char(string="Languages")
    implementing_agencies = fields.Text(string="Implementing Agencies")

    _sql_constraints = [
        ("code_unique", "unique(code)", "Program code must be unique!"),
    ]

    @api.onchange("yaml_file")
    def _onchange_yaml_file(self):
        """Auto-populate yaml_content when file is uploaded"""
        if self.yaml_file:
            try:
                import base64

                # Decode the binary file
                file_content = base64.b64decode(self.yaml_file)
                # Try to decode as UTF-8
                self.yaml_content = file_content.decode("utf-8")
            except Exception as e:
                _logger.error("Error reading YAML file: %s", e)
                return {
                    "warning": {
                        "title": _("File Read Error"),
                        "message": _(
                            "Could not read the uploaded file. Please ensure it's a valid text file.\n\nError: %s",
                            str(e),
                        ),
                    }
                }

    @api.depends("event_type_ids")
    def _compute_event_type_count(self):
        for rec in self:
            rec.event_type_count = len(rec.event_type_ids)

    @api.depends("yaml_content")
    def _compute_spec_data(self):
        """Parse and validate YAML content"""
        for rec in self:
            if not rec.yaml_content:
                rec.spec_data = "{}"
                continue

            try:
                parsed = yaml.safe_load(rec.yaml_content)
                import json

                rec.spec_data = json.dumps(parsed, indent=2)
            except yaml.YAMLError as e:
                rec.spec_data = json.dumps({"error": str(e)})
                _logger.error("YAML parsing error: %s", e)

    @api.constrains("yaml_content", "yaml_file")
    def _check_yaml_valid(self):
        """Validate YAML syntax and ensure either file or content is provided"""
        for rec in self:
            # Check that at least one is provided
            if not rec.yaml_content and not rec.yaml_file:
                raise ValidationError(
                    _("Please provide YAML content either by uploading a file or entering it manually.")
                )

            # Validate YAML syntax if content exists
            if rec.yaml_content:
                try:
                    yaml.safe_load(rec.yaml_content)
                except yaml.YAMLError as e:
                    raise ValidationError(_("Invalid YAML syntax: %s", str(e))) from e

    def action_validate(self):
        """Validate the program specification"""
        self.ensure_one()
        try:
            spec = yaml.safe_load(self.yaml_content)

            # Extract metadata
            program_data = spec.get("program", {})
            self.name = program_data.get("name", self.name)
            self.program_objectives = "\n".join(program_data.get("objectives", []))
            self.currency = program_data.get("currency", "")

            localization = program_data.get("localization", {})
            self.languages = ", ".join(localization.get("languages", []))
            self.implementing_agencies = ", ".join(program_data.get("implementing_agencies", []))

            self.state = "validated"
            self.error_message = False

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Success"),
                    "message": _("Program specification validated successfully."),
                    "type": "success",
                    "sticky": False,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        except Exception as e:
            self.state = "error"
            self.error_message = str(e)
            raise UserError(_("Validation failed: %s", str(e))) from e

    def action_deploy(self):
        """Deploy event types from the specification"""
        self.ensure_one()

        if self.state != "validated":
            raise UserError(_("Please validate the specification before deploying."))

        try:
            spec = yaml.safe_load(self.yaml_content)
            event_types = self._extract_event_types_from_spec(spec)

            # Create or update event type definitions
            created_count = 0
            updated_count = 0

            for event_type_data in event_types:
                existing = self.env["spp.event.type.definition"].search(
                    [
                        ("program_spec_id", "=", self.id),
                        ("technical_name", "=", event_type_data["technical_name"]),
                    ],
                    limit=1,
                )

                if existing:
                    existing.write(event_type_data)
                    updated_count += 1
                else:
                    event_type_data["program_spec_id"] = self.id
                    self.env["spp.event.type.definition"].create(event_type_data)
                    created_count += 1

            # Deploy the event type models
            for event_type in self.event_type_ids:
                event_type.action_deploy()

            self.state = "deployed"
            self.last_deployed = fields.Datetime.now()

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Success"),
                    "message": _(
                        "Deployed %d event types (%d new, %d updated).",
                        created_count + updated_count,
                        created_count,
                        updated_count,
                    ),
                    "type": "success",
                    "sticky": False,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }
        except Exception as e:
            self.state = "error"
            self.error_message = str(e)
            raise UserError(_("Deployment failed: %s", str(e))) from e

    def _extract_event_types_from_spec(self, spec):
        """Extract event type definitions from program spec"""
        event_types = []

        # Extract from external_systems (compliance evidence)
        external_systems = spec.get("external_systems", [])
        for system in external_systems:
            system_id = system.get("id")
            domain = system.get("domain", "")
            data_contract = system.get("data_contract", {})
            record_type = data_contract.get("record_type", "")

            event_types.append(
                {
                    "name": f"{system_id} {record_type.replace('_', ' ').title()}",
                    "technical_name": f"spp.event.{domain}.{record_type}",
                    "description": f"Event type for {system_id} {record_type} data",
                    "source": "external_system",
                    "source_ref": system_id,
                    "field_definitions": self._extract_fields_from_data_contract(data_contract),
                }
            )

        # Extract from compliance conditions
        compliance = spec.get("compliance", {})
        conditions = compliance.get("conditions", [])
        for condition in conditions:
            condition_id = condition.get("id")
            description = condition.get("description", "")

            event_types.append(
                {
                    "name": f"Compliance: {condition_id.replace('_', ' ').title()}",
                    "technical_name": f"spp.event.compliance.{condition_id}",
                    "description": description,
                    "source": "compliance_condition",
                    "source_ref": condition_id,
                    "field_definitions": [
                        {"name": "verified_by", "label": "Verified By", "field_type": "char"},
                        {"name": "verification_date", "label": "Verification Date", "field_type": "date"},
                        {"name": "result", "label": "Result", "field_type": "boolean"},
                        {"name": "notes", "label": "Notes", "field_type": "text"},
                    ],
                }
            )

        # Extract from custom event_types section if present
        custom_events = spec.get("event_types", [])
        for custom_event in custom_events:
            event_types.append(
                {
                    "name": custom_event.get("name"),
                    "technical_name": custom_event.get("model"),
                    "description": custom_event.get("description", ""),
                    "source": "custom",
                    "source_ref": custom_event.get("id"),
                    "field_definitions": custom_event.get("fields", []),
                }
            )

        return event_types

    def _extract_fields_from_data_contract(self, data_contract):
        """Extract field definitions from data contract"""
        fields = []
        required_fields = data_contract.get("required_fields", [])

        for field_def in required_fields:
            field_name = field_def.get("name")
            field_type = field_def.get("type", "char")

            # Map YAML types to Odoo field types
            type_mapping = {
                "string": "char",
                "number": "float",
                "boolean": "boolean",
                "date": "date",
                "datetime": "datetime",
            }

            odoo_type = type_mapping.get(field_type, "char")

            fields.append(
                {
                    "name": field_name,
                    "label": field_name.replace("_", " ").title(),
                    "field_type": odoo_type,
                }
            )

        return fields

    def action_view_event_types(self):
        """Open event types view"""
        self.ensure_one()
        return {
            "name": _("Event Types"),
            "type": "ir.actions.act_window",
            "res_model": "spp.event.type.definition",
            "view_mode": "tree,form",
            "domain": [("program_spec_id", "=", self.id)],
            "context": {"default_program_spec_id": self.id},
        }

    def action_reset_to_draft(self):
        """Reset to draft state"""
        self.ensure_one()
        self.state = "draft"
        self.error_message = False

    def action_export_yaml(self):
        """Export YAML specification as a downloadable file"""
        self.ensure_one()

        if not self.yaml_content:
            raise UserError(_("No YAML content to export."))

        import base64

        # Prepare filename
        filename = f"{self.code or 'program_spec'}.yaml"

        # Encode content
        file_content = self.yaml_content.encode("utf-8")
        file_data = base64.b64encode(file_content)

        # Update the binary field
        self.yaml_file = file_data
        self.yaml_filename = filename

        # Return download action
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/spp.program.spec/{self.id}/yaml_file/{filename}?download=true",
            "target": "self",
        }
