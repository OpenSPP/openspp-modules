from odoo import fields, models


class DataSourceKeyValueMixin(models.AbstractModel):
    _name = "spp.data.source.key.value.mixin"
    _description = "Data Source Key Value Mixin"

    data_source_id = fields.Many2one("spp.data.source", required=True)
    key = fields.Char(required=True, index=True)
    value = fields.Text(required=True)

    key_uniq_error_message = "Key must be unique in this Data Source."
    _sql_constraints = [("key_uniq", "unique (data_source_id, key)", key_uniq_error_message)]

    def get_mapping(self):
        mapping = {}
        for rec in self:
            mapping[rec.key] = rec.value

        return mapping


class SppDataSourcePath(models.Model):
    _name = "spp.data.source.path"
    _inherit = ["spp.data.source.key.value.mixin"]
    _description = "SPP Data Source Path"

    key_uniq_error_message = "Path Name must be unique in this Data Source."

    def get_full_path(self):
        self.ensure_one()

        return f"{self.data_source_id.url}{self.value}"


class DataSourceFieldMapping(models.Model):
    _name = "spp.data.source.field.mapping"
    _inherit = ["spp.data.source.key.value.mixin"]
    _description = "Data Source Field Mapping"

    key_uniq_error_message = "Client Field must be unique in this Data Source."


class DataSourceParameter(models.Model):
    _name = "spp.data.source.parameter"
    _inherit = ["spp.data.source.key.value.mixin"]
    _description = "Data Source Parameter"
