from odoo import api, fields, models
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

    @api.constrains("relation")
    def _check_relation_required(self):
        """Validate that relation is required on save"""
        self._validate_relation_required()
