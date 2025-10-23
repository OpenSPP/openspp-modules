import base64

import yaml

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CodeGenerator(models.Model):
    _name = "spp.code.generator"
    _description = "Code Generator"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="YAML Filename", required=True, index=True)
    description = fields.Text(string="Description")
    yaml_file = fields.Binary(string="YAML File", attachment=True, tracking=True)

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
