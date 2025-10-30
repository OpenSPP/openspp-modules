# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PartnerSearchField(models.Model):
    """Configuration model for managing searchable partner fields"""

    _name = "spp.partner.search.field"
    _description = "Partner Search Field Configuration"
    _order = "sequence, name"

    name = fields.Char(
        string="Field Label",
        required=True,
        help="Display name for the field in the dropdown",
    )
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Field",
        domain="[('model', '=', 'res.partner')]",
        help="Partner field to be searchable",
    )
    field_name = fields.Char(
        string="Field Name",
        related="field_id.name",
        store=True,
        readonly=True,
    )
    field_type = fields.Selection(
        string="Field Type",
        related="field_id.ttype",
        store=True,
        readonly=True,
    )
    target_type = fields.Selection(
        [
            ("individual", "Individual"),
            ("group", "Group"),
            ("both", "Both"),
        ],
        string="Target Type",
        default="both",
        required=True,
        help="Specify if this field is for Individuals, Groups, or Both",
    )
    active = fields.Boolean(
        default=True,
        help="If unchecked, this field will not appear in the search dropdown",
    )
    sequence = fields.Integer(
        default=10,
        help="Order in which fields appear in the dropdown",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=False,
    )

    _sql_constraints = [
        (
            "unique_field_per_company",
            "unique(field_id, company_id)",
            "This field is already configured for this company!",
        ),
    ]

    @api.constrains("field_id")
    def _check_field_type(self):
        """Ensure only searchable field types are selected"""
        searchable_types = [
            "char",
            "text",
            "selection",
            "many2one",
            "many2many",
            "integer",
            "float",
            "date",
            "datetime",
            "boolean",
        ]
        for record in self:
            if record.field_type not in searchable_types:
                raise models.ValidationError(
                    f"Field type '{record.field_type}' is not supported for searching."
                )

    def name_get(self):
        """Custom name display"""
        result = []
        for record in self:
            name = f"{record.name} ({record.field_name})"
            result.append((record.id, name))
        return result

