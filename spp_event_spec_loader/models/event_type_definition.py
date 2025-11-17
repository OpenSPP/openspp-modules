# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import json
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class EventTypeDefinition(models.Model):
    _name = "spp.event.type.definition"
    _description = "Event Type Definition"
    _order = "sequence, name"

    name = fields.Char(string="Event Type Name", required=True)
    technical_name = fields.Char(
        string="Technical Name", required=True, help="Model name (e.g., spp.event.compliance.attendance)"
    )
    description = fields.Text(string="Description")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Relationship to program spec
    program_spec_id = fields.Many2one(
        "spp.program.spec", string="Program Specification", required=True, ondelete="cascade"
    )

    # Source information
    source = fields.Selection(
        [
            ("external_system", "External System"),
            ("compliance_condition", "Compliance Condition"),
            ("custom", "Custom"),
        ],
        string="Source",
        required=True,
        default="custom",
    )
    source_ref = fields.Char(string="Source Reference")

    # Field definitions (stored as JSON)
    field_definitions = fields.Text(string="Field Definitions", help="JSON array of field definitions")

    # Deployment status
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("deployed", "Deployed"),
            ("error", "Error"),
        ],
        default="draft",
        required=True,
    )

    error_message = fields.Text(string="Error Message", readonly=True)
    model_deployed = fields.Boolean(
        string="Model Deployed", default=False, help="Indicates if the model has been created"
    )
    view_deployed = fields.Boolean(string="Views Deployed", default=False, help="Indicates if views have been created")
    wizard_deployed = fields.Boolean(
        string="Wizard Deployed", default=False, help="Indicates if wizard has been created"
    )

    _sql_constraints = [
        ("technical_name_unique", "unique(technical_name)", "Technical name must be unique!"),
    ]

    @api.onchange("name")
    def _onchange_name(self):
        """Auto-generate technical name from name"""
        if self.name and not self.technical_name:
            # Convert name to technical name
            tech_name = self.name.lower()
            tech_name = tech_name.replace(" ", "_")
            tech_name = "".join(c for c in tech_name if c.isalnum() or c == "_")
            self.technical_name = f"spp.event.{tech_name}"

    def action_deploy(self):
        """Deploy this event type (create model, views, wizard)"""
        self.ensure_one()

        try:
            # Step 1: Deploy the model
            self._deploy_model()

            # Step 2: Deploy views
            self._deploy_views()

            # Step 3: Deploy wizard
            self._deploy_wizard()

            # Step 4: Register with event wizard selection
            self._register_event_type()

            self.state = "deployed"
            self.error_message = False

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Success"),
                    "message": _("Event type '%s' deployed successfully.", self.name),
                    "type": "success",
                    "sticky": False,
                },
            }
        except Exception as e:
            self.state = "error"
            self.error_message = str(e)
            _logger.exception("Failed to deploy event type %s", self.technical_name)
            raise UserError(_("Deployment failed: %s", str(e))) from e

    def _deploy_model(self):
        """Create the dynamic event model"""
        self.ensure_one()

        # Check if model already exists
        existing_model = self.env["ir.model"].search([("model", "=", self.technical_name)], limit=1)

        if existing_model:
            _logger.info("Model %s already exists, updating...", self.technical_name)
        else:
            # Create the model
            model_vals = {
                "name": self.name,
                "model": self.technical_name,
                "state": "manual",
                "field_id": [],
            }

            # Add standard fields
            standard_fields = [
                {
                    "name": "x_name",
                    "field_description": "Name",
                    "ttype": "char",
                    "state": "manual",
                },
                {
                    "name": "x_summary",
                    "field_description": "Summary",
                    "ttype": "char",
                    "state": "manual",
                },
                {
                    "name": "x_description",
                    "field_description": "Description",
                    "ttype": "text",
                    "state": "manual",
                },
            ]

            # Add custom fields from definition
            if self.field_definitions:
                try:
                    field_defs = json.loads(self.field_definitions)
                    for field_def in field_defs:
                        field_name = field_def.get("name")
                        if not field_name.startswith("x_"):
                            field_name = f"x_{field_name}"

                        standard_fields.append(
                            {
                                "name": field_name,
                                "field_description": field_def.get("label", field_name),
                                "ttype": field_def.get("field_type", "char"),
                                "state": "manual",
                            }
                        )
                except json.JSONDecodeError:
                    _logger.warning("Invalid field definitions JSON for %s", self.technical_name)

            # Create fields as part of model creation
            field_commands = []
            for field_data in standard_fields:
                field_commands.append((0, 0, field_data))

            model_vals["field_id"] = field_commands

            new_model = self.env["ir.model"].sudo().create(model_vals)
            _logger.info("Created model %s (ID: %s)", self.technical_name, new_model.id)

        self.model_deployed = True

    def _deploy_views(self):
        """Create tree and form views for the event type"""
        self.ensure_one()

        # Generate tree view
        tree_view_arch = self._generate_tree_view_xml()
        tree_view_vals = {
            "name": f"view_{self.technical_name.replace('.', '_')}_tree",
            "model": self.technical_name,
            "type": "form",
            "arch": tree_view_arch,
            "mode": "primary",
        }

        # Check if view exists
        existing_tree = self.env["ir.ui.view"].search([("name", "=", tree_view_vals["name"])], limit=1)

        if existing_tree:
            existing_tree.sudo().write({"arch": tree_view_arch})
        else:
            self.env["ir.ui.view"].sudo().create(tree_view_vals)

        # Generate form view
        form_view_arch = self._generate_form_view_xml()
        form_view_vals = {
            "name": f"view_{self.technical_name.replace('.', '_')}_form",
            "model": self.technical_name,
            "type": "form",
            "arch": form_view_arch,
            "mode": "primary",
        }

        existing_form = self.env["ir.ui.view"].search([("name", "=", form_view_vals["name"])], limit=1)

        if existing_form:
            existing_form.sudo().write({"arch": form_view_arch})
        else:
            self.env["ir.ui.view"].sudo().create(form_view_vals)

        self.view_deployed = True

    def _generate_tree_view_xml(self):
        """Generate tree view XML"""
        fields_xml = '<field name="x_name"/>\n<field name="x_summary"/>'

        if self.field_definitions:
            try:
                field_defs = json.loads(self.field_definitions)
                for field_def in field_defs[:3]:  # Limit to first 3 custom fields
                    field_name = field_def.get("name")
                    if not field_name.startswith("x_"):
                        field_name = f"x_{field_name}"
                    fields_xml += f'\n<field name="{field_name}"/>'
            except json.JSONDecodeError:
                pass

        return f"""<?xml version="1.0"?>
<tree>
    {fields_xml}
</tree>"""

    def _generate_form_view_xml(self):
        """Generate form view XML"""
        fields_xml = ""

        if self.field_definitions:
            try:
                field_defs = json.loads(self.field_definitions)
                for field_def in field_defs:
                    field_name = field_def.get("name")
                    if not field_name.startswith("x_"):
                        field_name = f"x_{field_name}"
                    fields_xml += f'\n<field name="{field_name}"/>'
            except json.JSONDecodeError:
                pass

        return f"""<?xml version="1.0"?>
<form string="{self.name}">
    <sheet>
        <group>
            <group>
                <field name="x_name"/>
                <field name="x_summary"/>
                {fields_xml}
            </group>
            <group>
                <field name="x_description"/>
            </group>
        </group>
    </sheet>
</form>"""

    def _deploy_wizard(self):
        """Create wizard for this event type"""
        self.ensure_one()

        # For now, we'll mark as deployed
        # Full wizard generation would require creating transient models
        # which is complex with dynamic models
        self.wizard_deployed = True

    def _register_event_type(self):
        """Register this event type with the base event wizard"""
        self.ensure_one()

        # This would extend the selection field on spp.create.event.wizard
        # In practice, this requires module restart or dynamic field extension
        _logger.info("Event type %s registered (selection update requires restart)", self.technical_name)

    def action_undeploy(self):
        """Remove deployed components"""
        self.ensure_one()

        # Delete views
        views = self.env["ir.ui.view"].search([("model", "=", self.technical_name)])
        views.sudo().unlink()

        # Note: We don't delete the model to preserve data
        # Just mark as undeployed
        self.state = "draft"
        self.view_deployed = False
        self.wizard_deployed = False

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Success"),
                "message": _("Event type undeployed. Model data preserved."),
                "type": "warning",
                "sticky": False,
            },
        }
