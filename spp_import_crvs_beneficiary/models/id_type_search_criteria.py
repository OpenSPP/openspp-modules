from odoo import api, fields, models

from ..models import constants


class IDTypeSearchCriteria(models.Model):
    _name = "spp.id.type.search.criteria"
    _inherit = ["spp.base.search.criteria"]
    _description = "ID Type Search Criteria"

    identifier_type = fields.Selection(constants.ID_TYPE_CHOICES, required=True)
    identifier_value = fields.Char(required=True)

    @api.model
    def get_query_type(self):
        return constants.ID_TYPE_VALUE

    def get_query(self):
        self.ensure_one()
        return {
            "identifier_type": {
                "value": self.identifier_type,
            },
            "identifier_value": self.identifier_value,
        }
