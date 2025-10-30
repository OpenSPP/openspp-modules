import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SPPResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def search_by_field(self, field_name, search_value, is_group=False):
        """
        Search partners by a specific field
        :param field_name: The field name to search on
        :param search_value: The value to search for
        :param is_group: Whether to search for groups (True) or individuals (False)
        :return: List of matching partner IDs
        """
        if not field_name or not search_value:
            return []

        # Get the field configuration
        field_config = self.env["spp.partner.search.field"].search(
            [("field_name", "=", field_name), ("active", "=", True)], limit=1
        )

        if not field_config:
            _logger.warning(f"Field {field_name} is not configured for searching")
            return []

        # Build the search domain based on field type
        domain = []
        field_type = field_config.field_type

        if field_type in ["char", "text"]:
            domain = [(field_name, "ilike", search_value)]
        elif field_type in ["integer", "float"]:
            try:
                numeric_value = float(search_value)
                domain = [(field_name, "=", numeric_value)]
            except ValueError:
                _logger.warning(f"Invalid numeric value: {search_value}")
                return []
        elif field_type == "boolean":
            bool_value = search_value.lower() in ["true", "1", "yes"]
            domain = [(field_name, "=", bool_value)]
        elif field_type == "selection":
            domain = [(field_name, "=", search_value)]
        elif field_type == "many2one":
            domain = [(field_name + ".name", "ilike", search_value)]
        elif field_type in ["date", "datetime"]:
            domain = [(field_name, "=", search_value)]
        else:
            domain = [(field_name, "ilike", search_value)]

        # Add partner type filter (is_group)
        domain.append(("is_group", "=", is_group))
        
        # Always filter by is_registrant = True
        domain.append(("is_registrant", "=", True))

        return self.search(domain).ids

    @api.model
    def get_searchable_fields(self, partner_type=None):
        """
        Get list of searchable fields configured for partner search
        :param partner_type: 'individual', 'group', or None for all
        :return: List of dictionaries with field information
        """
        domain = [("active", "=", True)]
        
        # Filter by target_type based on partner_type
        if partner_type == "individual":
            domain.append(("target_type", "in", ["individual", "both"]))
        elif partner_type == "group":
            domain.append(("target_type", "in", ["group", "both"]))
        # If partner_type is None, return all active fields
        
        search_fields = self.env["spp.partner.search.field"].search(
            domain, order="sequence, name"
        )

        return [
            {
                "id": field.id,
                "name": field.name,
                "field_name": field.field_name,
                "field_type": field.field_type,
                "target_type": field.target_type,
            }
            for field in search_fields
        ]
