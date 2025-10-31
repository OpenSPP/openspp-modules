import json
import logging

from odoo import api, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class SPPResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def search_by_field(self, field_name, search_value, is_group=False, filter_domain="[]"):  # noqa: C901
        """
        Search partners by a specific field
        :param field_name: The field name to search on
        :param search_value: The value to search for (empty string for "search all")
        :param is_group: Whether to search for groups (True) or individuals (False)
        :param filter_domain: Additional filter domain in string format (e.g., "[('gender', '=', 'Female')]")
        :return: List of matching partner IDs
        """
        if not field_name:
            return []

        # Start with base domain
        domain = []

        # If search_value is provided, add field-specific search
        if search_value:
            # Get the field configuration
            field_config = self.env["spp.partner.search.field"].search(
                [("field_name", "=", field_name), ("active", "=", True)], limit=1
            )

            if not field_config:
                _logger.warning(f"Field {field_name} is not configured for searching")
                return []

            # Build the search domain based on field type
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
                # search_value should be the ID of the related record
                try:
                    record_id = int(search_value)
                    domain = [(field_name, "=", record_id)]
                except ValueError:
                    # Fallback to name search
                    domain = [(field_name + ".name", "ilike", search_value)]
            elif field_type in ["date", "datetime"]:
                domain = [(field_name, "=", search_value)]
            else:
                domain = [(field_name, "ilike", search_value)]
        # If search_value is empty, we're doing a "search all" - no field-specific filter

        # Add partner type filter (is_group)
        domain.append(("is_group", "=", is_group))

        # Always filter by is_registrant = True
        domain.append(("is_registrant", "=", True))

        # Apply additional filter domain
        include_archived = False
        try:
            # Parse JSON domain from frontend (comes as JSON string with lowercase true/false)
            additional_domain = json.loads(filter_domain or "[]")

            if additional_domain and isinstance(additional_domain, list):
                # Convert list format to tuple format for Odoo
                # JSON: ["|", ["field", "=", value], ...] -> Odoo: ["|", ("field", "=", value), ...]
                for condition in additional_domain:
                    if isinstance(condition, str):
                        # Domain operators like '|', '&', '!'
                        domain.append(condition)
                    elif isinstance(condition, list) and len(condition) >= 3:
                        # Regular domain condition
                        domain.append(tuple(condition))
                        # Check if we're searching for archived records
                        if condition[0] == "active" and not condition[2]:
                            include_archived = True
            else:
                # If no filter domain, only show active records by default
                domain.append(("active", "=", True))
        except Exception as e:
            _logger.warning(f"Error applying filter domain: {e}")
            # Default to active records on error
            domain.append(("active", "=", True))

        # Use with_context to include archived records if needed
        if include_archived:
            return self.with_context(active_test=False).search(domain).ids
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

        search_fields = self.env["spp.partner.search.field"].search(domain, order="sequence, name")

        result = []
        for field in search_fields:
            field_info = {
                "id": field.id,
                "name": field.name,
                "field_name": field.field_name,
                "field_type": field.field_type,
                "target_type": field.target_type,
            }

            # Add relational field information
            if field.field_type == "many2one":
                # Get the related model
                odoo_field = field.field_id
                if odoo_field.relation:
                    field_info["relation"] = odoo_field.relation
                    field_info["relation_field"] = "name"  # Default display field

            elif field.field_type == "selection":
                # Get selection options
                odoo_field = field.field_id
                model = self.env[odoo_field.model]
                field_obj = model._fields.get(odoo_field.name)
                if field_obj and hasattr(field_obj, "selection"):
                    if callable(field_obj.selection):
                        selection_options = field_obj.selection(model)
                    else:
                        selection_options = field_obj.selection
                    field_info["selection"] = selection_options

            result.append(field_info)

        return result

    @api.model
    def get_field_options(self, relation_model):
        """
        Get options for a many2one field
        :param relation_model: The model name to get records from
        :return: List of tuples (id, name)
        """
        try:
            records = self.env[relation_model].search([], limit=200)
            # Use name_get() which is more universal and returns [(id, name), ...]
            return records.name_get()
        except Exception as e:
            _logger.error(f"Error loading options for {relation_model}: {e}")
            return []

    @api.model
    def get_search_filters(self, partner_type=None):
        """
        Get list of search filters configured for partner search
        :param partner_type: 'individual', 'group', or None for all
        :return: List of dictionaries with filter information
        """

        domain = [("active", "=", True)]

        # Filter by target_type based on partner_type
        if partner_type == "individual":
            domain.append(("target_type", "in", ["individual", "both"]))
        elif partner_type == "group":
            domain.append(("target_type", "in", ["group", "both"]))
        # If partner_type is None, return all active filters

        filters = self.env["spp.partner.search.filter"].search(domain, order="sequence, name")

        result = []
        for f in filters:
            # Convert Python domain to JSON-compatible format
            try:
                python_domain = safe_eval(f.domain or "[]")
                # Convert tuples to lists for JSON compatibility
                json_domain = json.dumps(python_domain)
            except Exception as e:
                _logger.warning(f"Error converting domain for filter {f.name}: {e}")
                json_domain = "[]"

            result.append(
                {
                    "id": f.id,
                    "name": f.name,
                    "domain": json_domain,
                    "description": f.description,
                    "target_type": f.target_type,
                }
            )

        return result
