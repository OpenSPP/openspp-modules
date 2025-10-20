from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SPPRegistrantRelationship(models.Model):
    _inherit = "g2p.reg.rel"

    relation_inverse = fields.Char(related="relation.name_inverse", string="Relation")

    def _validate_relation_required(self):
        """Validate that relation is required"""
        for record in self:
            # Skip validation for completely new records (no ID and no other fields filled)
            if not record.id or not any([record.source, record.destination, record.start_date]):
                continue

            if not record.relation:
                raise ValidationError(
                    "Relation field required. To complete registrant relation, "
                    "please select a relation type from the dropdown. If no options are available, "
                    "go to Configuration > Relation Types to create relation types first."
                )

    @api.constrains("source", "relation", "destination", "start_date", "end_date")
    def _check_relation_uniqueness(self):
        """Forbid multiple active relations of the same type between the same
        partners
        :raises ValidationError: When constraint is violated
        """
        for record in self:
            domain = [
                ("relation", "=", record.relation.id),
                ("id", "!=", record.id),
                ("source", "=", record.source.id),
                ("destination", "=", record.destination.id),
            ]
            if record.start_date:
                domain += [
                    "|",
                    ("end_date", "=", False),
                    ("end_date", ">=", record.start_date),
                ]
            if record.end_date:
                domain += [
                    "|",
                    ("start_date", "=", False),
                    ("start_date", "<=", record.end_date),
                ]
            if record.search(domain):
                raise ValidationError(
                    _(
                        "Duplicate Relation Detected !\n\n"
                        "A record with the same relation type already exists and has overlapping dates. \n"
                        "To save multiple entries of the same relation, please define distinct start and end dates."
                    )
                )

    @api.constrains("relation")
    def _check_relation_required(self):
        """Validate that relation is required on save"""
        self._validate_relation_required()
