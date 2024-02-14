from odoo import fields, models


class SppDataSource(models.Model):
    _name = "spp.data.source"
    _description = "SPP Data Source"

    AUTH_TYPE_CHOICES = [
        ("basic_authentication", "Basic Authentication"),
        ("bearer_authentication", "Bearer Authentication"),
        ("api_keys", "API Keys"),
    ]

    name = fields.Char("Data Source Name", required=True)
    url = fields.Char(string="Target URL", required=True)

    auth_type = fields.Selection(AUTH_TYPE_CHOICES, required=True)

    data_source_path_ids = fields.One2many("spp.data.source.path", "data_source_id", string="URL Paths")
    data_source_field_mapping_ids = fields.One2many(
        "spp.data.source.field.mapping",
        "data_source_id",
    )
    data_source_parameter_ids = fields.One2many(
        "spp.data.source.parameter",
        "data_source_id",
    )

    _sql_constraints = [
        ("name_uniq", "unique(name)", "The name of the data source must be unique !"),
    ]

    def get_field_mapping_key_value_pair(self):
        return self.data_source_field_mapping_ids.get_mapping()

    def get_parameter_key_value_pair(self):
        return self.data_source_parameter_ids.get_mapping()

    def get_source_path_id_key_full_path_pair(self):
        pair = {}
        for path_id in self.data_source_path_ids:
            pair[path_id.key] = path_id.get_full_path()

        return pair
