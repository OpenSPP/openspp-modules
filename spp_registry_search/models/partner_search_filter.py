# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class SPPPartnerSearchFilter(models.Model):
    _name = "spp.partner.search.filter"
    _description = "Partner Search Filter Configuration"
    _order = "sequence, name"

    name = fields.Char(string="Filter Name", required=True, translate=True)
    sequence = fields.Integer(default=10, help="Order of filter in dropdown")
    active = fields.Boolean(default=True)
    domain = fields.Text(
        string="Domain",
        required=True,
        default="[]",
        help="Domain filter in Python format, e.g., [('gender', '=', 'Female')]",
    )
    target_type = fields.Selection(
        [
            ("individual", "Individual"),
            ("group", "Group"),
            ("both", "Both"),
        ],
        string="Target Type",
        required=True,
        default="both",
        help="Specify whether this filter applies to individuals, groups, or both",
    )
    description = fields.Text(string="Description", translate=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    @api.constrains("domain")
    def _check_domain(self):
        """Validate that the domain is a valid Python expression"""
        for record in self:
            try:
                domain = safe_eval(record.domain or "[]")
                if not isinstance(domain, list):
                    raise ValueError("Domain must be a list")
            except Exception as e:
                from odoo.exceptions import ValidationError

                raise ValidationError(f"Invalid domain: {e}") from e

    def name_get(self):
        """Custom name display"""
        result = []
        for record in self:
            name = record.name
            if record.description:
                name = f"{name} - {record.description}"
            result.append((record.id, name))
        return result
