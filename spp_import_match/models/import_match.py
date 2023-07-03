# Part of OpenSPP. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class SPPImportMatch(models.Model):
    _name = "spp.import.match"
    _description = "Import Matching"
    _order = "sequence, name"

    name = fields.Char(compute="_compute_name", store=True, index=True)
    sequence = fields.Integer(index=True)
    model_id = fields.Many2one(
        "ir.model",
        "Model",
        required=True,
        ondelete="cascade",
        domain=[("transient", "=", False)],
        help="Model for Import Matching",
    )
    model_name = fields.Char(related="model_id.model")
    model_description = fields.Char(related="model_id.name")
    field_ids = fields.One2many(
        "spp.import.match.fields",
        "match_id",
        string="Fields",
        required=True,
        help="Fields to Match in Importing",
    )

    @api.onchange("model_id")
    def _onchange_model_id(self):
        for rec in self:
            rec.field_ids = None

    @api.depends("model_id")
    def _compute_name(self):
        for rec in self:
            name = "New"
            if rec.model_id:
                name = rec.model_description

            rec.name = name

    @api.model
    def _match_find(self, model, converted_row, imported_row):
        usable, field_to_match = self._usable_rules(model._name, converted_row)
        usable = self.browse(usable)
        for combination in usable:
            combination_valid = True
            domain = list()
            for field in combination.field_ids:
                if field.conditional:
                    if imported_row[field.name] != field.imported_value:
                        combination_valid = False
                        break
                if field.field_id.name in converted_row:
                    row_value = converted_row[field.field_id.name]
                    field_value = field.field_id.name
                    add_to_domain = True
                    if field.sub_field_id:
                        tuple_val = row_value[0][2]
                        add_to_domain = False
                        if field.sub_field_id.name in tuple_val:
                            row_value = tuple_val[field.sub_field_id.name]
                            add_to_domain = True
                            field_value = field.field_id.name + "." + field.sub_field_id.name
                    if add_to_domain:
                        domain.append((field_value, "=", row_value))
            if not combination_valid:
                continue
            match = model.search(domain)
            if len(match) == 1:
                return match

        return model

    @api.model
    @tools.ormcache("model_name", "frozenset(fields)")
    def _usable_rules(self, model_name, fields):
        result = self
        available = self.search([("model_name", "=", model_name)])
        field_to_match = []
        for record in available:
            field_to_match.append(record.field_ids.mapped("name"))
            for f in record.field_ids:
                if f.name in fields or f.field_id.name in fields:
                    result |= record

        return result.ids, field_to_match


class SPPImportMatchFields(models.Model):
    _name = "spp.import.match.fields"
    _description = "Fields for Import Matching"

    name = fields.Char(compute="_compute_name")
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Field",
        required=True,
        ondelete="cascade",
        domain="[('model_id', '=', model_id)]",
        help="Fields to Match in Importing",
    )
    relation = fields.Char(related="field_id.relation")
    sub_field_id = fields.Many2one(
        "ir.model.fields",
        string="Sub-Field",
        ondelete="cascade",
        help="Sub Fields to Match in Importing",
    )
    match_id = fields.Many2one("spp.import.match", string="Match", ondelete="cascade")
    model_id = fields.Many2one(related="match_id.model_id")
    conditional = fields.Boolean()
    imported_value = fields.Char(
        help="This will be used as a condition to disregard this field if matched"
    )

    def _compute_name(self):
        for rec in self:
            name = rec.field_id.name
            if rec.sub_field_id:
                name = rec.field_id.name + "/" + rec.sub_field_id.name
            rec.name = name

