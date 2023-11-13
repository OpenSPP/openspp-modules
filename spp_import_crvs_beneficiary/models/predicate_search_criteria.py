from odoo import api, fields, models

from ..models import constants


class PredicateSearchCriteria(models.Model):
    _name = "spp.predicate.search.criteria"
    _inherit = ["spp.base.search.criteria"]
    _description = "Predicate Search Criteria"

    from_birth_date = fields.Date(required=True)
    to_birth_date = fields.Date(required=True)

    @api.model
    def get_query_type(self):
        return constants.PREDICATE

    def get_query(self):
        self.ensure_one()
        return [
            {
                "condition": "and",
                "expression1": {
                    "attribute_name": "birthdate",
                    "operator": "gt",
                    "attribute_value": str(self.from_birth_date),
                },
                "expression2": {
                    "attribute_name": "birthdate",
                    "operator": "lt",
                    "attribute_value": str(self.to_birth_date),
                },
            }
        ]
